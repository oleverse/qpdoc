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
# from langchain.llms import HuggingFaceHub
# from langchain.evaluation import load_evaluator, EvaluatorType


class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class LanguageModelService(ABC):
    @abstractmethod
    async def run_llm(self, query: str, user_id: int, file_id: int, db: SessionLocal):
        pass


# class HuggingFaceLanguageModel(LanguageModelService):
#     def __init__(self, api_key):
#         openai.api_key = api_key


class OpenAILanguageModel(LanguageModelService):
    def __init__(self, api_key):
        openai.api_key = api_key

    async def run_llm(self, query: str, user_id: int, file_id: int, db: SessionLocal):
        # Отримання вмісту файлу з бази даних
        user_file = db.query(PDFModel).filter(and_(PDFModel.user_id == user_id, PDFModel.id == file_id)).first()

        if not user_file:
            raise ValueError("Файли користувача не знайдено")
        # all_file_content = " ".join([file.content for file in user_file])
        file_content = user_file.content[:1500000] if len(user_file.content) > 1500000 else user_file.content

        # Векторизація тексту
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=0)
        doc = Document(file_content)
        chunks = text_splitter.split_documents(documents=[doc])

        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        index_name = "const-index-react"

        try:
            last_history_file_id = await get_last_history_file_id(user_id, db)
        except AttributeError:
            last_history_file_id = None

        if last_history_file_id != file_id:
            if os.path.exists(index_name):
                shutil.rmtree(index_name, ignore_errors=True)
            print('(Re)Creating index...')
            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(index_name)
            print('The index was created')
        else:
            vectorstore = FAISS.load_local(index_name, embeddings)

        # answer = "LLM didn't return the answer."

        # try:
        model_types = {
            "gpt-3.5": "gpt-3.5-turbo-1106",
            "gpt-4": "gpt-4",
        }
        model_type = "gpt-3.5"
        openai_llm = ChatOpenAI(openai_api_key=settings.openai_api_key, model=model_types[model_type], timeout=100)

        qa = ConversationalRetrievalChain.from_llm(
            llm=openai_llm,
            # working HF models: google/flan-t5-xxl
            # llm=HuggingFaceHub(repo_id='google/flan-t5-large',
            #                    model_kwargs={"temperature": 0.5, "max_length": 256},
            #                    huggingfacehub_api_token=settings.hf_api_access_token),
            # chain_type='stuff',
            retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=True
        )
        # except openai.RateLimitError as err:
        #     return err.message
        # else:
        chat_history = [(h.question, h.answer) for h in await get_history_for_user_by_file(user_id, file_id, db)]
        try:
            result = qa({"question": query, "chat_history": chat_history})

        # try to evaluate the possible answer
        # accuracy_criteria = {
        #     "Score 1": "The answer is completely unrelated to the reference.",
        #     "Score 3": "The answer has minor relevance but does not align with the reference.",
        #     "Score 5": "The answer has moderate relevance but contains inaccuracies.",
        #     "Score 7": "The answer aligns with the reference but has minor errors or omissions.",
        #     "Score 10": "The answer is completely accurate and aligns perfectly with the reference."
        # }

        # evaluator = load_evaluator(EvaluatorType.SCORE_STRING, llm=openai_llm)
        # eval_result = evaluator.evaluate_strings(
        #     prediction=result['answer'],
        #     input="query",
        #     criteria=accuracy_criteria
        # )
            answer = (200, result['answer'])
        except (openai.RateLimitError, openai.BadRequestError) as r_err:
            answer = (r_err.status_code, r_err.message)

        return answer


llm_service = OpenAILanguageModel(api_key=settings.openai_api_key)
