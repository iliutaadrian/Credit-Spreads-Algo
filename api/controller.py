import yfinance as yf
from dotenv import load_dotenv

import os
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory

load_dotenv()


def get_chatbot_response(user_message, chat_history):
    custom_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question. If you do not know the answer reply with 'I am sorry'.
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    prompt = PromptTemplate.from_template(custom_template)

    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT"])
    index = pinecone.Index(os.environ["PINECONE_INDEX"])
    vector_store = Pinecone(index, embeddings.embed_query, "text")

    model = ChatOpenAI(temperature=0.3)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    qa = ConversationalRetrievalChain.from_llm(
        model,
        vector_store.as_retriever(),
        condense_question_prompt=prompt,
        memory=memory
    )

    result = qa({"question": user_message, "chat_history": chat_history})
    return result


def get_chart_data(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    live_price = stock.history(period='1d')['Close'].iloc[-1]

    chart_data = stock.history(period='30d')

    dates = chart_data.index.strftime('%m-%d').tolist()
    prices = chart_data['Close'].tolist()

    return live_price, dates, prices