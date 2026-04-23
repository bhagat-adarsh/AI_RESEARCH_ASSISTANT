well its a sample AI Agent for research purpose, i have tried to include tools and MCP in it you can customize the system_prompts and use it accordingly 
i have used an gemini2.5-flash model, yeah the free one,
you can cutomize he classes as per the repective requirements,
i have Vibe coded the index.html (FRONTEND) file because honestly i was not intrested in sitting and designing the UI i just wanna experiment with AI Agents, MCP and stuff,
and also i have used two new things here pydantic BaseModels and Fields its basically for Data validation and self documendation ensuring API inputs match our defined types and constrains,
and Fields is just to add metadata or extra validation rules like (min/max values) to ensure output data is valid
Two real search services i have used:
-Semantic Scholar and 
-arXiv
these tools help to find sources
and just i have added some SS of the flask app/web.

yeah the papers formula trends those pydantic models are the strict law suit contract times that AI has to return 

and honsetly speaking LLM + tool orchestration has troubled me a lot in it i have to go and search through chatbots and various documendation  and learn how tool orchestration works it overall was a nice expereince

ooh i do realise i sounded like a some great people highlighting their own hardwork,  i should just stop yapping and simply explain the workflow and shut it now :

==========
WORKFLOW:
so first few pydantic modesl are defined then i have used  ToolStratergy(Reoprt part) which basically bounds the agent to match the schema,
then a few tool integration which bridge with the LLM agent,
the agent can call them like functions during reasoning instead of guessing answers from raw model knowledge,
search_semantic_scholar() uses a JSON REST API adn search_arxiv uses XML,
they extract titles authors  published year and id,
craeate_agemt(...) builds tool using agent bounded by the system prompt ,
the **task** text then reinforces this with structured instructions,
gemerate-report(...) is async because model.ainvoke is asynchronous well i just was getting errors and ai suggested me to switch to asyncio,
the agent returns result["structured_response"], which is already aligned to the Report schema ,
result.model_dump() converts the Pydantic object into JSON-compatible data to display it and the input thing question_input (var) takes the questions rfom the web while Flas routes,
it is then split because schema requires a list and browser sends a single text block (honsetly i just got to know about it while making it).

|well signning of your yapper|
_____|-JINDA INSAN-|_________
