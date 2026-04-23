import json 
import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model

load_dotenv()
#things i personally wanted to be in the research paper or report which can be adjusted for diffrent needs whatever you want just specify that particular class 
class Paper(BaseModel):
	title: str
	authors: list[str]
	year: int 
	venue: str | None = None # the pipe symbol basically means venue is either gonna be str or None
	url: str | None = None
	relevance : str = Field(description="Why this paper is relevant to the topic or research question.")

class Formula(BaseModel):
	name: str
	latex: str = Field(description="LaTeX source for the formula, no surrounding delimiters.")
	# latex is for displaying the latex synthax, kind of as if you want you can use \\frac{1}{2} something like this to display fraction
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

async def main():
	topic = input("What is the topic for the paper / thesis: ").strip()
	questions = input("What are the key research questions: ").strip()
	timeframe = input("What time frame should the papers be from").strip()

	task  = f"""Topic: {topic}
Researc questions: {questions}
Time frame: {timeframe or 'no specific focus'}
Gather 5-10 highly relevant papers.
Then identify the most important mathematical formulas for this subject and recent trends.
Populate the Report schema fully."""
	
	model = init_chat_model(
	    "gemini-2.5-flash",
	    model_provider="google_genai"
	).with_structured_output(Report)
	result = await model.ainvoke([
		{'role': 'system', 'content':'You are a thorough IT research assistant helping write academic papares and theses.'},
		{'role': 'user', 'content': task}
		])

	print(json.dumps(result.model_dump(), indent = 2))

asyncio.run(main())