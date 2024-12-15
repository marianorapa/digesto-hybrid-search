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
        self.normalized_score_by_doc_id = {}
        self.last_rank = 0
        self.score_type = None

    def set_ranking_name(self, ranking_name):
        self.ranking_name = ranking_name

    def get_ranking_name(self):
        return self.ranking_name

    def set_k_documents(self, k):
        self.k_documents = k

    def add_document(self, document, score=None):
        if document.get_id() not in self.ranking_by_doc_id.keys():
            self.documents.append([document, score])

            self.ranking_by_doc_id[document.get_id()] = len(self.documents)
        else:
            print(f"Warning - Adding {document.get_id()} duplicated in {self.ranking_name}")

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


    def get_min_score(self):
        return min(self.documents, key=lambda x: x[1])[1]

    def get_max_score(self):
        return max(self.documents, key=lambda x: x[1])[1]

    def normalize_documents(self, type):
        #self.documents = sorted(self.documents, key=lambda x: x[1])
        if type == "Score":
            min_score = self.get_min_score()
            max_score = self.get_max_score()
        elif type == "Distance":
            min_score = self.get_max_score()
            max_score = self.get_min_score()

        print(f"Ranking Name {self.ranking_name}, Max Score: {max_score}, Min Score: {min_score}, Amount of documents {len(self.documents)}")
        for document, score in self.documents:
            normalized_score = (score - min_score) / (max_score - min_score)
            self.normalized_score_by_doc_id[document.get_id()] = normalized_score

    def sort_documents_by_score(self):
        self.documents = sorted(self.documents, key=lambda x: x[1], reverse=True)

    def get_document_normalized_score(self, doc_id, default = 0):
        if self.normalized_score_by_doc_id == {}:
            self.normalize_documents(self.score_type)

        if doc_id in self.normalized_score_by_doc_id.keys():
            return self.normalized_score_by_doc_id[doc_id]
        else:
            return default

    def set_score_type(self, score):
        self.score_type = score

    def merge_interpolating_score(self, ranking):
        w1 = 0.5
        w2 = 0.5

        result_ranking = Ranking()
        result_ranking.set_ranking_name("Hybrid Ranking Interpolating Score")
        result_ranking.set_k_documents(20)
        result_ranking.set_relevant_documents_ids(self.relevant_documents_ids)

        print(f"Amount of Left Ranking Documents {len(self.documents)}")
        print(f"Amount of Right Ranking Documents {len(ranking.documents)}")

        for left_ranking_document, _ in self.documents:

            left_ranking_normalized_score = self.get_document_normalized_score(left_ranking_document.get_id())

            right_ranking_normalized_score = ranking.get_document_normalized_score(left_ranking_document.get_id())

            interpolated_score = w1 * left_ranking_normalized_score + w2 * right_ranking_normalized_score
            result_ranking.add_document(left_ranking_document, interpolated_score)

        for right_ranking_document, _ in ranking.documents:
            #print(f"Right Ranking Document, position in Result Ranking: {result_ranking.get_document_ranking(right_ranking_document.get_id())}")
            if result_ranking.get_document_ranking(right_ranking_document.get_id()) == -1:
                print(f"Adding not found document {right_ranking_document.get_id()}")
                left_ranking_normalized_score = self.get_document_normalized_score(right_ranking_document.get_id())
                right_ranking_normalized_score = ranking.get_document_normalized_score(right_ranking_document.get_id())

                interpolated_score = w1 * left_ranking_normalized_score + w2 * right_ranking_normalized_score
                result_ranking.add_document(right_ranking_document, interpolated_score)
            #break

        print(f"Amount of Result Ranking Documents {len(result_ranking.documents)}")
        result_ranking.sort_documents_by_score()
        return result_ranking
