import logging
from typing import List

from langchain_chroma import Chroma
from langchain.storage import LocalFileStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings

from ai.data.config import CACHE_DIR, EMBEDDING_MODEL, SEARCH_QUANTITY


class EmbeddingManager:
    """
    Manages embeddings and the retriever.
    """

    def __init__(self):
        self._initialize_embeddings()
        self._vectorstore = None
        self._retriever = None

    def _initialize_embeddings(self):
        """
        Initialize the embeddings with caching.
        """
        try:
            self._store = LocalFileStore(str(CACHE_DIR))
            underlying_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
            self._cached_embedder = CacheBackedEmbeddings.from_bytes_store(
                underlying_embeddings, self._store, namespace=underlying_embeddings.model
            )
        except Exception as e:
            logging.error(f"Failed to initialize embeddings: {e}")
            raise

    def setup_retriever(self, documents: List[Document]):
        """
        Set up the retriever with the given documents.
        """
        try:
            self._vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self._cached_embedder
            )
            self._retriever = self._vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": SEARCH_QUANTITY}
            )
            return self._retriever
        except Exception as e:
            logging.error(f"Failed to set up retriever: {e}")
            raise

    def get_retriever(self):
        return self._retriever
