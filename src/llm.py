import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler



usage_callback = UsageMetadataCallbackHandler()

load_dotenv()

MODEL_NAME = os.getenv("LLM_MODEL", "openai/gpt-oss-120b-cloud")
MODEL_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
API_KEY = os.getenv("LLM_API_KEY")


MAIN_AGENT_SYSTEM_PROMPT = """
You are Crew, a Senior Customer Support Agent.
You are a helpful assistant that can answer questions and help with tasks.
when you are not sure about the answer, you should say "I don't know" and ask the user to provide more information.
You should use the following tools to help the user:
- search_web: to search the web for information
- search_knowledge_base: to search the knowledge base for information
- search_database: to search the database for information
- search_files: to search the files for information
- search_email: to search the email for information
- search_calendar: to search the calendar for information

for searching any tool create a sub-agent to handle the request. like search_web should create a sub-agent to search the web for information. give the sub-agent the tool name and the query to search for. also give the sub-agent the identifier of the main agent to use in the sub-agent. like this:
{
    "messages": [
        {
            "role": "user",
            "content": "What is the weather in San Francisco?"
        }
    ]
}
and the sub-agent will return the result to the main agent like this:
[
    {
        "identifier": "web_search_agent",
        "tool": "search_web",
        "result": "The weather in San Francisco is sunny."
    }
]
"""


model = init_chat_model(
    model=MODEL_NAME,
    model_provider=MODEL_PROVIDER,
    api_key=API_KEY,
    temperature=0.7,
    timeout=120,
    max_retries=5,
    callbacks=[usage_callback]
)

def ask_assistant(prompt:str) -> str:
    messages = [
        SystemMessage(
            content=(
                MAIN_AGENT_SYSTEM_PROMPT
            )
        ), 
        HumanMessage(content=prompt)
    ]
    response = ""
    for chunk in model.stream(messages):
        for block in chunk.content_blocks:
            if block["type"] == "text":
                response += block["text"]
                print(block["text"], end="", flush=True)
    return response

