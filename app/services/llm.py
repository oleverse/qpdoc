import os.path
import shutil
from abc import ABC, abstractmethod
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.repository.histories import get_last_history_file_id, get_history_for_user_by_file
from app.conf.config import settings

from app.database.db import SessionLocal
from app.database.models import PDFModel
from sqlalchemy import and_


class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class LanguageModelService(ABC):
    @abstractmethod
    async def run_llm(self, query: str, user_id: int, file_id: int, db: SessionLocal):
        pass


class OpenAILanguageModel(LanguageModelService):
    def __init__(self, api_key):
        openai.api_key = api_key

    async def run_llm(self, query: str, user_id: int, file_id: int, db: SessionLocal):
        # Отримання вмісту файлу з бази даних
        user_file = db.query(PDFModel).filter(and_(PDFModel.user_id == user_id, PDFModel.id == file_id)).first()

        if not user_file:
            raise ValueError("Файли користувача не знайдено")
        # all_file_content = " ".join([file.content for file in user_file])
        file_content = user_file.content[:150000] if len(user_file.content) > 150000 else user_file.content

        # Векторизація тексту
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        doc = Document(file_content)
        chunks = text_splitter.split_documents(documents=[doc])

        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        index_name = "const-index-react"

        last_history_file_id = await get_last_history_file_id(user_id, db)
        if last_history_file_id != file_id:
            if os.path.exists(index_name):
                shutil.rmtree(index_name, ignore_errors=True)
            print('(Re)Creating index...')
            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(index_name)
            print('The index was created')
        else:
            vectorstore = FAISS.load_local(index_name, embeddings)

        answer = "LLM didn't return the answer."

        try:
            qa = ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(openai_api_key=settings.openai_api_key),
                chain_type='stuff',
                retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
                return_source_documents=True
            )
        except openai.RateLimitError as err:
            return err.message
        else:
            chat_history = [(h.question, h.answer) for h in await get_history_for_user_by_file(user_id, file_id, db)]
            result = qa({"question": query, "chat_history": chat_history})
            answer = result['answer']

        return answer


llm_service = OpenAILanguageModel(api_key=settings.openai_api_key)
