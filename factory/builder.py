# factory/builder.py

import yaml

from Project_chat_bot.llm.base import BaseLLM
from Project_chat_bot.llm.ollama import OllamaLLMClient

from retrievers.base_retriever import BaseRetriever
from retrievers.faiss_retriever import FaissRetriever
from intents.llm_intent_classifier import LLMIntentClassifier
from Project_chat_bot.core.chat_service import ChatService
from Project_chat_bot.core.context_builder import ContextBuilder
from Project_chat_bot.core.session_memory import SessionMemory
from app_logging.logger import Logger


class Builder:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    # -------------------------
    # LOAD CONFIG
    # -------------------------
    def _load_config(self) -> dict:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # -------------------------
    # LLM
    # -------------------------
    def build_llm(self) -> BaseLLM:
        model_cfg = self.config["model"]
        model_type = model_cfg["type"]

        if model_type == "ollama":
            return OllamaLLMClient(model_cfg)

        raise ValueError(f"Неизвестный тип модели: {model_type}")

    # -------------------------
    # RETRIEVER
    # -------------------------
    def build_retriever(self) -> BaseRetriever:
        retr_cfg = self.config["retriever"]
        retr_type = retr_cfg["type"]

        if retr_type == "faiss":
            return FaissRetriever(
                file_path=retr_cfg["file_path"],
                top_k=retr_cfg.get("top_k", 3),
                embedding_model=retr_cfg.get("embedding_model")
            )

        raise ValueError(f"Неизвестный retriever: {retr_type}")

    # -------------------------
    # INTENTS
    # -------------------------
    def build_intent_classifier(self, llm: BaseLLM):
        intents_cfg = self.config["intents"]

        if not intents_cfg.get("enabled", False):
            return None

        return LLMIntentClassifier(
            llm=llm,
            intents_path=intents_cfg["intents_path"],
            prompt_path=intents_cfg["prompt_path"],
            use_rules=intents_cfg.get("use_rules", True),
            use_llm=intents_cfg.get("use_llm", True),
        )

    # -------------------------
    # MEMORY
    # -------------------------
    def build_memory(self) -> SessionMemory:
        mem_cfg = self.config["memory"]

        return SessionMemory(
            max_messages=mem_cfg.get("max_history_messages", 10)
        )

    # -------------------------
    # LOGGER
    # -------------------------
    def build_logger(self) -> Logger:
        log_cfg = self.config["logging"]
        log_file = log_cfg.get("log_file", "app_logging/chat.log")
        return Logger(log_file=log_file)

    # -------------------------
    # CHAT SERVICE
    # -------------------------
    def build_chat_service(self) -> ChatService:
        llm = self.build_llm()
        retriever = self.build_retriever()
        memory = self.build_memory()
        logger = self.build_logger()
        intent_classifier = self.build_intent_classifier(llm)

        context_builder = ContextBuilder()
        return ChatService(
            llm=llm,
            retriever=retriever,
            context_builder=context_builder,
            memory=memory,
            logger=logger,
            intent_classifier=intent_classifier
        )