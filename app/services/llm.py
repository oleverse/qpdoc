from abc import ABC, abstractmethod
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.conf.config import settings

from app.database.db import SessionLocal
from app.database.models import PDFModel


class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class LanguageModelService(ABC):
    @abstractmethod
    def run_llm(self, query: str, user_id: int, db: SessionLocal):
        pass


class OpenAILanguageModel(LanguageModelService):
    def __init__(self, api_key):
        openai.api_key = api_key

    def run_llm(self, query: str, user_id: int, db: SessionLocal):
        # Отримання вмісту файлу з бази даних
        user_files = db.query(PDFModel).filter(PDFModel.user_id == user_id).all()

        if not user_files:
            raise ValueError("Файли користувача не знайдено")
        all_file_content = " ".join([file.content for file in user_files])

        # Векторизація тексту
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        doc = Document(all_file_content)
        chunks = text_splitter.split_documents(documents=[doc])

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


llm_service = OpenAILanguageModel(api_key=settings.openai_api_key)
