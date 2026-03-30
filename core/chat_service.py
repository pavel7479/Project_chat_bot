from llm.base import BaseLLM
from retrievers.base_retriever import BaseRetriever
from intents.base_intents import BaseIntentClassifier
from Project_chat_bot.core.context_builder import ContextBuilder
from Project_chat_bot.core.session_memory import SessionMemory
from schemas.message import Message
from schemas.response import ChatResponse
from app_logging.logger import Logger
from intents.chunk_post_processor import ChunkPostProcessor
from filters.query_filter import QueryFilter
from filters.rules_loader import load_rules
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class ChatService:
    def __init__(
        self,
        llm: BaseLLM,
        retriever: BaseRetriever,
        context_builder: ContextBuilder,
        memory: SessionMemory,
        logger: Logger,
        intent_classifier: BaseIntentClassifier | None = None
    ):
        self.llm = llm
        self.retriever = retriever
        self.context_builder = context_builder
        self.memory = memory
        self.logger = logger
        self.intent_classifier = intent_classifier
        self.chunk_processor = ChunkPostProcessor(logger=self.logger)
        
        BASE_DIR = Path(__file__).resolve().parent.parent
        rules_path = BASE_DIR / "config/query_rules.txt"
        rules_config = load_rules(str(rules_path))
        
        self.query_filter = QueryFilter(rules_config)

    def handle(self, query: str) -> ChatResponse:
        # 1. история
        history = self.memory.get_history()
        
        response = self.query_filter.process(query, history)
        if response:
            return ChatResponse(text=response, media=[])

        # 2. поиск
        docs = self.retriever.search(query)
        print("\n=== FAISS RAW RESULTS ===")
        for i, doc in enumerate(docs):
            print(f"{i+1}:\n{doc.get('text','')}\n")

        docs = self.chunk_processor.filter_chunks(query, docs)
        print("\n=== AFTER CHUNK FILTER ===")
        for i, doc in enumerate(docs):
            print(f"{i+1}:\n{doc.get('text','')}\n")

        # ЛОГИРУЕМ ЧТО ВЕРНУЛ FAISS
        docs_text = "\n\n".join(f"{i+1}. {doc.get('text','')}" for i, doc in enumerate(docs))
        self.logger.log_prompt("=== FAISS DOCS ===\n" + docs_text)

        # 3. интенты (опционально)
        intents = []
        if self.intent_classifier:
            intents = self.intent_classifier.predict_intents(query=query, history=history, docs=docs)

        # 4. контекст
        prompt = self.context_builder.build(
            query=query,
            docs=docs,
            history=history,
            intents=intents
        )

        self.logger.log_prompt(prompt)

        # 5. генерация
        response_text = self.llm.generate(prompt)

        self.logger.log_response(response_text)

        # 6. сохраняем историю
        self.memory.add_message(Message(role="user", content=query))
        self.memory.add_message(Message(role="assistant", content=response_text))

        return ChatResponse(text=response_text, media=[])