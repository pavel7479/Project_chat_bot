from typing import List, Dict
from intents.synonyms import SYNONYMS

class ChunkPostProcessor:
    def __init__(self, synonyms: dict = SYNONYMS, logger=None):
        self.synonyms = synonyms
        self.reverse_map = self._build_reverse_map()
        self.logger = logger

    def _build_reverse_map(self):
        reverse = {}

        for key, values in self.synonyms.items():
            for v in values:
                reverse[v.lower()] = key

        return reverse

    def extract_keywords(self, query: str):
        words = query.lower().split()

        normalized = []
        for w in words:
            normalized.append(self.reverse_map.get(w, w))

        return set(normalized)
    
    def filter_chunks(self, query: str, chunks: List[Dict], min_score: int = 1):
        keywords = self.extract_keywords(query)

        scored = []

        for chunk in chunks:
            text = chunk["text"].lower()

            matched_keywords = [k for k in keywords if k in text]
            score = len(matched_keywords)

            if self.logger:
                self.logger.log_prompt(
                    f"[CHUNK SCORE] score={score} | matched={matched_keywords} | text={text[:150]}"
                )

            if score >= min_score:
                scored.append((score, chunk))

        # fallback (ВАЖНО для безопасности)
        if not scored:
            if self.logger:
                self.logger.log_prompt("[CHUNK FILTER] fallback: return top-1 chunk")
            return chunks[:1]

        scored.sort(key=lambda x: x[0], reverse=True)

        filtered = [c for _, c in scored]

        if self.logger:
            self.logger.log_prompt("=== FILTERED CHUNKS ===")
            for i, c in enumerate(filtered):
                self.logger.log_prompt(f"{i+1}. {c['text'][:150]}")

        return filtered