from llm import ask_assistant, model as llm_model, MAIN_AGENT_SYSTEM_PROMPT

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

config = {"configurable": {"thread_id": str(uuid7())}}



SUBAGENT_SYSTEM_PROMPT = """
You are a helpful assistant, you'll given a query and you'll need to solve it by using the tools provided to you.
You should return the result in a structured format like this:
{
    "result": "The result of the query",
}
if you don't know the answer, you should return "I don't know" and ask the user to provide more information.
"""


# subagent

subagent = create_agent(
    model=llm_model,
    system_prompt=SUBAGENT_SYSTEM_PROMPT,
    tools=[search_web],
    checkpointer=InMemorySaver(),
)

# tools for the subagent
@tool
def search_web(query: str) -> str:
    result = subagent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )
    return result["messages"][-1].content
@Tool(name="search_web", description="Search the web for information")


def run_main_agent(query: str) -> str:
    main_agent = create_agent(
        model=llm_model,
        system_prompt=MAIN_AGENT_SYSTEM_PROMPT,
        tools=[subagent],
        checkpointer=InMemorySaver(),
    )

    result = main_agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )
    return result["messages"][-1].content
