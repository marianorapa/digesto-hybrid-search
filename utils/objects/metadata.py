from typing import List
from utils.objects.document import Document
import json

class Metadata:
    def __init__(self, filepath = None):
        self.filepath = filepath
        self.metadata = {}

    def success(self, document: Document):
        self.metadata[document.get_id()] = document.success().to_json()
    
    def error(self, document: Document, error):
        self.metadata[document.get_id()] = document.error(error).to_json()

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.metadata, f)

    def load(self):
        with open(self.filepath, 'r') as file:
            self.metadata = json.load(file)

    def get_valid_documents(self) -> List[Document]:
        return [document for document in self.metadata.values() if document.is_success()]