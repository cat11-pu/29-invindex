"""invindex.py：倒排索引（基线：词 -> 文档集合，无位置）。"""
from __future__ import annotations


def tokenize(text: str) -> list:
    return text.lower().split()


class InvIndex:
    def __init__(self):
        self.docs = {}
        self.terms = {}
        self.deleted = set()
        self.wal = []

    def add(self, doc_id: str, text: str) -> dict:
        self.docs[doc_id] = text
        for word in tokenize(text):
            self.terms.setdefault(word, set()).add(doc_id)
        self.wal.append(("add", doc_id))
        return {"terms": len(tokenize(text))}

    def search(self, term: str) -> dict:
        """基线：不排除已删除的文档，也没有位置。"""
        return {"docs": sorted(self.terms.get(term.lower(), set()))}

    def phrase(self, words) -> dict:
        raise NotImplementedError("短语查询还没实现")

    def delete(self, doc_id: str) -> dict:
        """基线：只打标记，检索还会返回它。"""
        existed = doc_id in self.docs
        self.deleted.add(doc_id)
        return {"deleted": existed}

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> int:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"docs": len(self.docs), "terms": len(self.terms), "deleted": len(self.deleted)}
