import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import  ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools.render import render_text_description

from tools import build_tools, included_tables
from prompt import REACT_PROMPT_TEMPLATE
from cache import *
from callback import AsyncOpenAICallbackHandler

MEMORY_KEY = "chat_history"
OPENAI_MODEL = "gpt-4"

openai_callback = AsyncOpenAICallbackHandler()
model = ChatOpenAI(model=OPENAI_MODEL, max_tokens=128, temperature=0.5, cache=True, streaming=True, callbacks=[openai_callback])

def build_memory(msgs):
    return ConversationBufferWindowMemory(
        llm=model, chat_memory=msgs, k=3, memory_key=MEMORY_KEY, output_key="output"
    )

def __build_agent(template, tools, llm: ChatOpenAI, context):
    prompt = ChatPromptTemplate.from_template(template)
    # setup ReAct style prompt
    prompt = prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
        tables=", ".join(included_tables)
    )
    prompt.partial(**context)

    llm.bind_tools(tools)
    agent = create_openai_tools_agent(llm, tools, prompt)

    return agent

def build_agent(memory):
    tools, context = build_tools(model)
    agent = __build_agent(REACT_PROMPT_TEMPLATE, tools, model, context)

    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, 
                                   return_intermediate_steps=True,
                                    verbose=True, handle_parsing_errors=True)
    print('Agent loaded!')
    return agent_executor
