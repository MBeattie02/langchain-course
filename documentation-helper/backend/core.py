from dotenv import load_dotenv

load_dotenv()
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from consts import INDEX_NAME


def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
    chat = ChatOpenAI(verbose=True, temperature=0)
    # chat = Ollama(model="llama3.2:3b")

    # Convert chat_history to messages format
    messages = []
    for msg in chat_history:
        if isinstance(msg, tuple):
            role, content = msg
            if role == "human":
                messages.append(HumanMessage(content=content))
            elif role == "ai":
                messages.append(AIMessage(content=content))
        elif isinstance(msg, dict):
            if msg.get("role") == "human" or msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "ai" or msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))

    # Create history-aware rephrase prompt
    rephrase_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                "Given the above conversation, generate a search query to look up information to help answer the follow-up question. "
                "If the question is not related to the conversation history, just return the question as-is. "
                "Do not include any other text, only return the search query.",
            ),
            ("human", "{question}"),
        ]
    )

    # Create retrieval QA prompt
    retrieval_qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the question based only on the following context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    # Format documents function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create history-aware retriever chain
    retriever = docsearch.as_retriever()

    # Step 1: Rephrase question based on history
    rephrase_chain = rephrase_prompt | chat | StrOutputParser()

    # Step 2: Retrieve documents using rephrased query
    def get_standalone_query(inputs: Dict[str, Any]) -> str:
        if messages:
            standalone_query = rephrase_chain.invoke(
                {"chat_history": messages, "question": inputs["question"]}
            )
        else:
            standalone_query = inputs["question"]
        return standalone_query

    # Step 3: Retrieve and format documents
    retrieval_chain = (
        RunnablePassthrough.assign(standalone_query=get_standalone_query)
        | RunnablePassthrough.assign(
            context=lambda x: format_docs(retriever.invoke(x["standalone_query"]))
        )
    )

    # Step 4: Generate answer
    qa_chain = retrieval_qa_prompt | chat | StrOutputParser()

    # Combine everything
    rag_chain = retrieval_chain | qa_chain

    result = rag_chain.invoke({"question": query, "chat_history": messages})

    # Return in expected format
    return {
        "answer": result,
        "context": retriever.invoke(
            get_standalone_query({"question": query}) if messages else query
        ),
    }


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def run_llm2(query: str, chat_history: List[Dict[str, Any]] = []):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
    # chat = Ollama(model="llama3.2:3b")
    chat = ChatOpenAI(model="gpt-4o-mini", verbose=True, temperature=0)

    # Convert chat_history to messages format
    messages = []
    for msg in chat_history:
        if isinstance(msg, tuple):
            role, content = msg
            if role == "human":
                messages.append(HumanMessage(content=content))
            elif role == "ai":
                messages.append(AIMessage(content=content))
        elif isinstance(msg, dict):
            if msg.get("role") == "human" or msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "ai" or msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))

    # Create retrieval QA prompt with chat history support
    retrieval_qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the question based only on the following context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # Format documents function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create RAG chain using LCEL
    rag_chain = (
        {
            "context": docsearch.as_retriever() | format_docs,
            "input": RunnablePassthrough(),
            "chat_history": lambda x: messages,
        }
        | retrieval_qa_prompt
        | chat
        | StrOutputParser()
    )

    result = rag_chain.invoke({"input": query})
    return {"answer": result, "context": docsearch.as_retriever().invoke(query)}



