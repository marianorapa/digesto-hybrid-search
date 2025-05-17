from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url
import pyterrier as pt
import os
from nltk import word_tokenize
from nltk.stem import SnowballStemmer

config = os.environ

INDEXES = {
        "VISTO": config["SPARSE_INDEX_VISTO_DIR"],
        "CONSIDERANDO": config["SPARSE_INDEX_CONSIDERANDO_DIR"],
        "RESUELVE": config["SPARSE_INDEX_RESUELVE_DIR"],
        "DISPONE": config["SPARSE_INDEX_DISPONE_DIR"],
        "RESOLUTIVA": config["SPARSE_INDEX_RESOLUTIVA_DIR"],
        "COMPLETE_COMPLETE": config["SPARSE_INDEX_COMPLETE_COMPLETE_DIR"],
        "COMPLETE_RESUELVE": config["SPARSE_INDEX_COMPLETE_RESUELVE_DIR"],
        "COMPLETE_DISPONE": config["SPARSE_INDEX_COMPLETE_DISPONE_DIR"],
}

def get_url_from_filename(filename):
        return get_url(filename)

def get_ranking_sparse(index, query, k, relevant_documents_ids, docs_metadata, ranking_name = "Rank Sparse"):
        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")

        retriever = pt.terrier.Retriever(index, wmodel=config['SPARSE_MODEL'])
        query_results = retriever.search(query)

        terrier_metadata = index.getMetaIndex()

        sparse_ranking = Ranking()
        sparse_ranking.set_ranking_name(ranking_name)
        sparse_ranking.set_k_documents(k)
        sparse_ranking.set_relevant_documents_ids(relevant_documents_ids)

        counter = 0
        for index, row in query_results.iterrows():
                terrier_doc_id = row['docid']
                filename = terrier_metadata.getAllItems(terrier_doc_id)[1]

                if docs_metadata != None:
                        document = docs_metadata.get_document_by_id(Document.get_doc_id_from_filename(filename), True)
                else:
                        document = Document(txt_path = filename)

                sparse_ranking.add_document(document, row['score'])

                counter += 1
                if counter == int(config["RANKING_LIMIT"]):
                        break

        return sparse_ranking