from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url
import pyterrier as pt
import os

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


#def get_relevant_documents_sparse(index, query, k):
#        if not pt.started():
#                pt.init()
#
#        output_dir = INDEXES[index]
#
#        index = pt.IndexFactory.of(f"{output_dir}/data.properties")
#
#        pipe = pt.rewrite.tokenise("utf") >> pt.BatchRetrieve(index, wmodel="BM25")
#
#        query_results = pipe.search(query)
#
#        meta = index.getMetaIndex()
#
#        final_results = []
#        counter = 0
#        for index, row in query_results.iterrows():
#                doc_id = row['docid']
#                score = row['score']
#                rank = row['rank'] + 1
#                filename = meta.getAllItems(doc_id)[1]
#                doc_url = get_url_from_filename(filename)
#                final_results.append([doc_id, score, filename, rank, doc_url])
#
#                counter += 1
#                if counter == k:
#                        break
#
#
#        doc_ids = list(query_results.docid)
#
#        return final_results

## Duplicate and refactor previous function, to retro-compatibility
def get_ranking_sparse(index, query, k, relevant_documents_ids):
        if not pt.started():
                pt.init()

        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")

        pipe = pt.rewrite.tokenise("utf") >> pt.BatchRetrieve(index, wmodel="BM25", num_results = config["RANKING_LIMIT"])

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
                print(f"Filename {filename}")
                break
                #doc_url = get_url_from_filename(filename)

                #document = Document()
                #document.set_id_from_url(doc_url)
                #sparse_ranking.add_document(document, row['score'])

                #counter += 1
                #if counter == config["RANKING_LIMIT"]:
                #        break

        return sparse_ranking