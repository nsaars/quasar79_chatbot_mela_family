import json
import logging
from typing import List, Dict, Tuple

from langchain_core.documents import Document

from ai.data.config import TXT_FILES


class DocumentManager:
    """
    Responsible for loading and parsing documents.
    """

    def __init__(self):
        self.documents: List[Document] = []
        self.kwargs: Dict = {}

    def load_documents(self) -> Tuple[List[Document], Dict]:
        """
        Load documents from the structure file.
        """
        self.documents.extend(self.load_documents_from_txt())

        return self.documents, self.kwargs


    def load_documents_from_txt(self):
        documents = []

        for txt_file_path in TXT_FILES:
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                documents.append(Document(
                    page_content=file.read(),
                    metadata={'file_name': txt_file_path}
                ))
        return documents