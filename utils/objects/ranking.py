from nltk.corpus.reader import documents
from tabulate import tabulate

from utils.objects.document import Document

EMPTY_RESULT_STRING = "-"

class Ranking():

    def __init__(self):
        self.documents = []
        self.relevant_documents_ids = []
        self.output_columns_keys = ["ID"]

    def add_document(self, document, score=None):
        #TODO Add Score
        self.documents.append(document)

    def set_relevant_documents_ids(self, relevant_documents_ids):
        self.relevant_documents_ids = relevant_documents_ids

    def set_output_columns(self, output_columns_keys):
        self.output_columns_keys = output_columns_keys

    def __str__(self):
        list_of_documents = []
        element_of_list = []
        if self.documents == []:
            for _ in self.output_columns_keys:
                element_of_list.append(EMPTY_RESULT_STRING)
            list_of_documents.append(element_of_list)


        order = 1
        document: Document
        for document in self.documents:
            element_of_list = []
            for key in self.output_columns_keys:
                if key == "ID":
                    element_of_list.append(document.get_id())
                if key == "URL":
                    element_of_list.append(document.get_url())
                if key == "Order":
                    element_of_list.append(order)
                if key == "Indexed":
                    element_of_list.append(document.is_indexed())
                if key == "Relevant":
                    element_of_list.append(document.get_id() in self.relevant_documents_ids)
                if key == "Rank Sparse":
                    element_of_list.append("TODO")
                if key == "Rank Dense":
                    element_of_list.append("TODO")
                if key == "Rank Hybrid":
                    element_of_list.append("TODO")
                if key == "Rank Current Digest":
                    element_of_list.append("TODO")

            order += 1

            list_of_documents.append(element_of_list)

        table = tabulate(list_of_documents,
                         headers=self.output_columns_keys,
                         tablefmt="tsv")#,
                         #colalign=("center", "center", "center"))
        return table