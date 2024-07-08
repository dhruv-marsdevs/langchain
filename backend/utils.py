import datetime
import json
import os
import requests
import logging

from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store Chroma persistence
CHROMA_PERSIST_DIR = "chroma_db"


def fetch_details(ticker, multiplier, timespan, from_, to):
    base_url = os.getenv("BASE_URL")
    aggs_endpoint_raw = os.getenv("AGGS_ENDPOINT")
    version = os.getenv("VERSION")
    if not base_url:
        raise ValueError("BASE_URL is not set")

    aggs_endpoint = aggs_endpoint_raw.format(
        ticker=ticker,
        multiplier=multiplier,
        timespan=timespan,
        from_=from_,
        to=to,
    )

    url = f"{base_url}/{version}/{aggs_endpoint}"
    logger.info(f"Fetching data from URL: {url}")

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
        },
    )
    response.raise_for_status()

    return response.json()


def metadata_func(record: dict, metadata: dict) -> dict:
    """
    Extract metadata from each stock data record.
    """
    date = datetime.datetime.fromtimestamp(record["t"] / 1000).strftime("%Y-%m-%d")
    return {
        "date": date,
        "open": str(record["o"]),
        "high": str(record["h"]),
        "low": str(record["l"]),
        "close": str(record["c"]),
        "volume": str(record["v"]),
        "vwap": str(record["vw"]),
    }


def get_chroma_client():
    """
    Get or create a Chroma client.
    """
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def load_or_create_vector_store(docs=None):
    """
    Load existing vector store if it exists, otherwise create a new one.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    client = get_chroma_client()

    # Check if the collection exists
    collection_name = "stock_data"
    try:
        client.get_collection(name=collection_name)
        logger.info("Loading existing vector store...")
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )
    except Exception:
        pass

    if docs is None:
        raise ValueError("Documents must be provided to create a new vector store.")

    logger.info("Creating new vector store...")
    vector_store = Chroma.from_documents(
        docs, embeddings, client=client, collection_name=collection_name
    )
    return vector_store


def setup_qa_chain(vector_store):
    """
    Set up a retrieval QA chain using the vector store.
    """
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    prompt_template = PromptTemplate(
        input_variables=["context", "input"],
        template="""
        You are a financial expert with access to historical stock price data.

        Given the following context, answer the question regarding the stock prices.
        
        There are following keys in the context: date, open, high, low, close, volume, vwap
        Description  of each keys:
        - date: date of the stock price
        - open: open price of the stock
        - high: high price of the stock
        - low: low price of the stock
        - close: close price of the stock
        - volume: volume of the stock
        - vwap: volume weighted average price of the stock

        It is important for you to return the chart_data with a minimum of ten data points. 

        Provide detailed analytics data and suggest possible trends or insights.

        Never mention how did you get the data.

        The overall response should be json.
        
        Don't include markdown in your response.

        Mandatory keys in the response:
        - "answer": A detailed answer for the question. Always mention the date for which the data was recorded.
        - "chart_data": the charting data with a minimum of ten data points in list of objects (JSON) format. This is very important.
        
        Even when the user enters 'Hi' or any greeting message, maintain the above mandatory keys in the response.
        In this case, you can return empty chart_data. 
        Respond with greetings and one thought provoking question which you can answer.
        
        In any case, maintain the response format. Always include the mandatory keys:- answer and chart_data

        Context: {context}
        Question: {input}
        """,
    )

    document_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt_template,
    )
    retriever = vector_store.as_retriever()

    retrieval_chain = create_retrieval_chain(
        combine_docs_chain=document_chain,
        retriever=retriever,
        # return_source_documents=True,
    )

    return retrieval_chain


def fetch_and_process_data(ticker, multiplier, timespan, from_, to):
    """
    Fetch stock data and process it into documents.
    """

    response = fetch_details(ticker, multiplier, timespan, from_, to)

    with open("response.json", "w") as f:
        json.dump(response, f)

    loader = JSONLoader(
        file_path="./response.json",
        jq_schema=".results[]",
        content_key=None,
        metadata_func=metadata_func,
        text_content=False,
    )
    return loader.load()


def get_stock_data_answer(question):
    """
    Get answer for a stock data question.
    """
    vector_store = load_or_create_vector_store()
    qa_chain = setup_qa_chain(vector_store)
    result = qa_chain.invoke({"question": question})

    return {
        "question": question,
        "answer": result["answer"],
    }


def get_stock_data_analytics(question):
    vector_store = load_or_create_vector_store()
    qa_chain = setup_qa_chain(vector_store)
    result = qa_chain.invoke({"input": question})

    try:
        result = result["answer"].replace("\n", "")
    except Exception as e:
        result = result["answer"]

    return {
        "question": question,
        "result": json.loads(result),
    }
