from abc import ABC, abstractmethod
from pathlib import Path
import openai
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.conf.config import settings


class LanguageModelService(ABC):
    def __init__(self, api_key):
        openai.api_key = api_key

    @abstractmethod
    def run_llm(self, query: str):
        pass


class OpenAILanguageModel(LanguageModelService):
    def run_llm(self, query: str):
        dir_path = Path.cwd()
        path = str(Path(dir_path, "data", "ext.pdf"))

        loader = PyPDFLoader(path)
        pages = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        chunks = text_splitter.split_documents(documents=pages)

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
        result = qa({"question": query, "chat_history": chat_history})
        answer = result['answer']
        chat_history.append((query, answer))
        return answer


# Example usage
openai_service = OpenAILanguageModel(api_key=settings.openai_api_key)
#result = openai_service.run_llm(input("Ваше питання: "))
#print(f"Answer: {result}")
