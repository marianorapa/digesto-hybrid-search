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

def get_ranking_sparse(index, query, k, relevant_documents_ids):
        if not pt.started():
                pt.init()

        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")

        retriever = pt.terrier.Retriever(index, wmodel=config['SPARSE_MODEL'])
        query_results = retriever.search(query)

        meta = index.getMetaIndex()

        sparse_ranking = Ranking()
        sparse_ranking.set_ranking_name("Rank Sparse")
        sparse_ranking.set_k_documents(k)
        sparse_ranking.set_relevant_documents_ids(relevant_documents_ids)

        counter = 0
        for index, row in query_results.iterrows():
                doc_id = row['docid']
                filename = meta.getAllItems(doc_id)[1]
                document = Document(txt_path = filename)
                document.get_url()
                sparse_ranking.add_document(document, row['score'])

                counter += 1
                if counter == int(config["RANKING_LIMIT"]):
                        break

        return sparse_ranking