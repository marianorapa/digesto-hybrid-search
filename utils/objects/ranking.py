from nltk.corpus.reader import documents
from tabulate import tabulate

from utils.objects.document import Document

EMPTY_RESULT_STRING = "-"

class Ranking():

    def __init__(self):
        self.documents = []
        self.relevant_documents_ids = []
        self.output_columns_keys = ["ID"]
        self.k_documents = None
        self.reference_rankings = [] 
        self.ranking_name = None
        self.ranking_by_doc_id = {}
        self.last_rank = 0

    def set_ranking_name(self, ranking_name):
        self.ranking_name = ranking_name

    def get_ranking_name(self):
        return self.ranking_name

    def set_k_documents(self, k):
        self.k_documents = k

    def add_document(self, document, score=None):
        #TODO Add Score
        self.documents.append([document, score])
        self.ranking_by_doc_id[document.get_id()] = len(self.documents)
    
    def get_last_rank(self):
        return len(self.documents)

    def set_relevant_documents_ids(self, relevant_documents_ids):
        self.relevant_documents_ids = relevant_documents_ids

    def set_output_columns(self, output_columns_keys):
        self.output_columns_keys = output_columns_keys

    def get_first_k_documents_as_table(self):
        return self.get_k_documents_as_table(self.k_documents)

    def get_all_documents_as_table(self):
        return self.get_k_documents_as_table(len(self.documents))

    def add_reference_ranking(self, reference_ranking):
        self.reference_rankings.append(reference_ranking)

    def get_k_documents_as_table(self, k_documents):
        list_of_documents = []
        element_of_list = []
        if self.documents == []:
            for _ in self.output_columns_keys:
                element_of_list.append(EMPTY_RESULT_STRING)
            list_of_documents.append(element_of_list)


        order = 1
        document: Document
        i = 0
        while i < len(self.documents) and i < k_documents:
            document, score = self.documents[i]
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
                if key == "Score":
                    element_of_list.append(score)

            for reference_ranking in self.reference_rankings:
                element_of_list.append(reference_ranking.get_document_ranking(document.get_id()))

            order += 1
            i += 1

            list_of_documents.append(element_of_list)

        table = tabulate(list_of_documents,
                         headers=self.build_output_column_keys(),
                         tablefmt="tsv")#,
                         #colalign=("center", "center", "center"))
        return table
    
    def build_output_column_keys(self):
        reference_ranking_column_keys = []
        for reference_ranking in self.reference_rankings:
            reference_ranking_column_keys.append(reference_ranking.get_ranking_name())
        return self.output_columns_keys + reference_ranking_column_keys


    def get_document_ranking(self, doc_id):
        return self.ranking_by_doc_id.get(doc_id, -1)

    def __str__(self):
        return self.get_all_documents_as_table()