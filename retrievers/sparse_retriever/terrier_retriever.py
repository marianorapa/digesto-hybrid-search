import pyterrier as pt

from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url

RANKING_LIMIT = 140000

BASE_OUTPUT_DIR = "./indexes"
SPARSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/sparse_index"

VISTO_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/visto"
CONSIDERANDO_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/considerando"
RESUELVE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/resuelve"
DISPONE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/dispone"

COMPLETE_BASE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/completa"
COMPLETE_COMPLETE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/completa"
COMPLETE_RESUELVE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/resuelve"
COMPLETE_DISPONE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/dispone"

INDEXES = {
        "VISTO": VISTO_OUTPUT_DIR,
        "CONSIDERANDO": CONSIDERANDO_OUTPUT_DIR,
        "RESUELVE": RESUELVE_OUTPUT_DIR,
        "COMPLETE_COMPLETE": COMPLETE_COMPLETE_OUTPUT_DIR,
        "COMPLETE_RESUELVE": COMPLETE_RESUELVE_OUTPUT_DIR,
        "COMPLETE_DISPONE": COMPLETE_DISPONE_OUTPUT_DIR,
}

def get_url_from_filename(filename):
        return get_url(filename)


def get_relevant_documents_sparse(index, query, k):
        if not pt.started():
                pt.init()

        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")

        pipe = pt.rewrite.tokenise("utf") >> pt.BatchRetrieve(index, wmodel="BM25")

        query_results = pipe.search(query)

        meta = index.getMetaIndex()

        final_results = []
        counter = 0
        for index, row in query_results.iterrows():
                doc_id = row['docid']
                score = row['score']
                rank = row['rank'] + 1
                filename = meta.getAllItems(doc_id)[1]
                doc_url = get_url_from_filename(filename)
                final_results.append([doc_id, score, filename, rank, doc_url])

                counter += 1
                if counter == k:
                        break


        doc_ids = list(query_results.docid)

        return final_results

## Duplicate and refactor previous function, to retro-compatibility
def get_ranking_sparse(index, query, k, relevant_documents_ids):
        if not pt.started():
                pt.init()

        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")

        pipe = pt.rewrite.tokenise("utf") >> pt.BatchRetrieve(index, wmodel="BM25", num_results = RANKING_LIMIT)

        query_results = pipe.search(query)

        meta = index.getMetaIndex()


        sparse_ranking = Ranking()
        sparse_ranking.set_ranking_name("Rank Sparse")
        sparse_ranking.set_k_documents(k)
        sparse_ranking.set_relevant_documents_ids(relevant_documents_ids)

        counter = 0
        for index, row in query_results.iterrows():
                doc_id = row['docid']
                filename = meta.getAllItems(doc_id)[1]
                doc_url = get_url_from_filename(filename)

                document = Document()
                document.set_id_from_url(doc_url)
                sparse_ranking.add_document(document, row['score'])

                counter += 1
                if counter == RANKING_LIMIT:
                        break

        return sparse_ranking