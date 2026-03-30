from typing import List, Dict
import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from retrievers.base_retriever import BaseRetriever

# faiss_retriever.py
from typing import List, Dict
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from retrievers.base_retriever import BaseRetriever

class FaissRetriever(BaseRetriever):
    def __init__(
        self,
        file_path: str,
        top_k: int = 3,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        file_path: путь к файлу базы знаний (txt)
        top_k: сколько документов отдавать по релевантности
        embedding_model: модель для создания эмбеддингов
        """
        self.file_path = file_path
        self.top_k = top_k
        self.model = SentenceTransformer(embedding_model)

        # загружаем и парсим базу
        self.documents = self._load_data()
        
        print("=== CHUNKS CREATED ===")
        for i, doc in enumerate(self.documents):
            print(f"{i+1}: {doc['text']}")

        # создаём эмбеддинги
        self.embeddings = self._create_embeddings()

        # создаём FAISS индекс
        self.index = self._build_index()

    # ---------------- Загрузка и парсинг базы ----------------
    def _load_data(self) -> List[Dict]:
        """
        Читает txt файл и возвращает список словарей
        [
            {"question": "...", "answer": "...", "text": "question + answer"}
        ]
        """
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Разбиваем по числовым заголовкам 1. 2. 3.
        blocks = re.split(r"# Блок \d+ —", text)
        blocks = [b.strip() for b in blocks if b.strip()]
        documents = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Разделяем на вопрос и ответ по первой новой строке
            title = block.split("\n")[0].strip()
            documents.append({"text": f"{title}\n{block}"})

        return documents

    # ---------------- Создание эмбеддингов ----------------
    def _create_embeddings(self) -> np.ndarray:
        texts = [doc["text"] for doc in self.documents]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings

    # ---------------- FAISS индекс ----------------
    def _build_index(self):
        dim = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)  # простой индекс по L2
        index.add(self.embeddings)
        return index

    # ---------------- Поиск ----------------
    def search(self, query: str) -> List[Dict]:
        """
        Поиск top_k документов по смыслу запроса
        Возвращает список словарей {"question", "answer", "text"}
        """
        query_vector = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vector, self.top_k)

        results = []
        for idx in indices[0]:
            results.append(self.documents[idx])

        # threshold = 1.0  # надо подобрать

        # for dist, idx in zip(distances[0], indices[0]):
        #     if dist < threshold:
        #         results.append(self.documents[idx])

        return results