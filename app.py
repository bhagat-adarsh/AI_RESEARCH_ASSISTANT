import json
import asyncio
from langchain.tools import tool
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


load_dotenv()

app = Flask(__name__)

class Paper(BaseModel):
    title: str
    authors: list[str]
    year: int
    venue: str | None = None
    url: str | None = None
    relevance: str = Field(description="Why this paper is relevant to the topic or research question.")

class Formula(BaseModel):
    name: str
    latex: str = Field(description="LaTeX source for the formula, no surrounding delimiters.")
    description: str
    reference: str | None = Field(default=None, description="Paper, textbook or source where the formula comes from.")

class Trend(BaseModel):
    title: str
    description: str
    reference: list[str] = Field(default_factory=list, description="Titles or URLs of papers backing this trend.")

class Report(BaseModel):
    topic: str
    research_questions: list[str]
    time_frame: str | None = None
    papers: list[Paper] = Field(description="5 to 10 most relevant papers.")
    formulas: list[Formula]
    trends: list[Trend]

import requests
import xml.etree.ElementTree as ET
def search_semantic_scholar(query: str):
    print("🔍 Semantic Scholar query:", query)
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": query,
        "limit": 10,
        "fields": "title,authors,year,url"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch from Semantic Scholar: {str(e)}"}

    results = []
    for paper in data.get("data", []):
        results.append({
            "title": paper.get("title"),
            "authors": [a["name"] for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "url": paper.get("url")
        })

    return results

def search_arxiv(query: str):
    print("🔍 arXiv query:", query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.RequestException as e:
        return {"error": f"Failed to fetch from arXiv: {str(e)}"}
    except ET.ParseError as e:
        return {"error": f"Failed to parse arXiv XML: {str(e)}"}

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    results = []

    for entry in root.findall("atom:entry", ns):
        try:
            title = entry.find("atom:title", ns).text
            authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)]
            published = entry.find("atom:published", ns).text
            year = int(published[:4]) if published else None
            url = entry.find("atom:id", ns).text

            if title and authors and year:
                results.append({
                    "title": title.strip(),
                    "authors": authors,
                    "year": year,
                    "url": url
                })
        except (AttributeError, ValueError) as e:
            continue  # Skip malformed entries

    return results

@tool
def semantic_scholar_tool(query: str):
    """Search for academic papers using Semantic Scholar."""
    return search_semantic_scholar(query)


@tool
def arxiv_tool(query: str):
    """Search for academic papers using arXiv."""
    return search_arxiv(query)

    
async def generate_report(topic, research_questions, timeframe):
    task = f"""Topic: {topic}
    Research questions: {research_questions}
    Time frame: {timeframe or 'no specific focus'}

    STRICT INSTRUCTIONS:
    1. First call semantic_scholar_tool with multiple queries
    2. Then call arxiv_tool with multiple queries
    3. Collect REAL papers only from tool outputs
    4. Combine and filter best 5–10 papers
    5. Then extract formulas and trends

    DO NOT hallucinate papers.
    DO NOT skip tool usage.

    STRICT REQUIREMENTS:
    - papers MUST contain 5 to 10 items (never less than 5)
    - formulas MUST contain at least 3 items
    - trends MUST contain at least 3 items

    If you do not have enough results, call tools again with different queries.

    Populate the Report schema fully.
    """

    tools = [semantic_scholar_tool, arxiv_tool]

    model = init_chat_model(
        "gemini-2.5-flash",
        model_provider="google_genai"
    )

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
    You are a strict academic research assistant.

    RULES (MANDATORY):
    - You MUST use semantic_scholar_tool and arxiv_tool to find papers
    - DO NOT make up papers
    - DO NOT answer without calling tools first
    - ALWAYS call tools before generating final answer
    - Use multiple queries if needed
    - Use atleast minimum 5 -10 research papers and trends

    Return only structured data.
    """,
        response_format=ToolStrategy(Report)
    )
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": task}]
    })

    return result["structured_response"]   


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic', '').strip()
    questions_input = data.get('questions', '').strip()
    research_questions = [q.strip() for q in questions_input.split('\n') if q.strip()]
    timeframe = data.get('timeframe', '').strip()

    if not topic or not research_questions:
        return jsonify({'error': 'Topic and at least one research question are required.'}), 400

    try:
        result = asyncio.run(generate_report(topic, research_questions, timeframe))
        return jsonify(result.model_dump())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)