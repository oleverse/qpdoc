from pathlib import Path

import openai
from environs import Env
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter

env = Env()
env.read_env(".env")
openai.api_key = env.str('OPENAI_API_KEY')

def run_llm(query: str):
    dir_path = Path.cwd()
    path = str(Path(dir_path, "data", "ext.pdf"))
    loader = PyPDFLoader(path)
    pages = loader.load()


    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents=pages)
    print(chunks)

    embeddings = OpenAIEmbeddings()
    index_name = "const-index-react"

    try:
        vectorstore = FAISS.load_load(index_name, embeddings)
    except Exception as e:
        print('Creating index...')
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(index_name)
        print('The index was created')

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        chain_type='stuff',
        retriever=vectorstore.as_retriever()
    )

    result = qa({"query": query})
    return result['result']


if __name__ == '__main__':
    while True:
        print(run_llm(input("test:  ")))

