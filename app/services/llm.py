from pathlib import Path

import openai
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.conf.config import settings


openai.api_key = settings.openai_api_key


def run_llm(query: str):

    dir_path = Path.cwd()
    path = str(Path(dir_path, "data", "ext.pdf"))
    loader = PyPDFLoader(path)
    pages = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents=pages)
    # print(chunks)

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    index_name = "const-index-react"

    try:
        vectorstore = FAISS.load_load(index_name, embeddings)
    except Exception as e:
        print('Creating index...')
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(index_name)
        print('The index was created')

    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(openai_api_key=settings.openai_api_key),
        chain_type='stuff',
        retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True
    )

    chat_history = []
    # while True:
    # query = input("Ваше питання:  ")
    result = qa({"question": query, "chat_history": chat_history})
    print("Відповідь:" + result['answer'])
    chat_history.append((query, result['answer']))
    # print(chat_history)
    return result['answer']


if __name__ == '__main__':
    while True:
        print(run_llm(input("Ваше питання:  ")))
