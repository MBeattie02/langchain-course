from langsmith import Client
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

client = Client()
llm = ChatOpenAI(temperature=0, model="gpt-5-nano")
prompt = client.pull_prompt("rlm-eu/rag-prompt")

generation_chain = prompt | llm | StrOutputParser()
