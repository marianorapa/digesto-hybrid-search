import pyterrier as pt

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


def get_relevant_documents_sparse(index, query, k):
        if not pt.started():
                pt.init()

        output_dir = INDEXES[index]

        index = pt.IndexFactory.of(f"{output_dir}/data.properties")
        bm25 = pt.BatchRetrieve(index, wmodel="BM25")

        query_results = bm25.search(query)

        meta = index.getMetaIndex()

        final_results = []
        counter = 0
        for index, row in query_results.iterrows():
                doc_id = row['docid']
                score = row['score']
                rank = row['rank'] + 1
                filename = meta.getAllItems(doc_id)[1]
                final_results.append([doc_id, score, filename, rank])

                counter += 1
                if counter == k:
                        break


        doc_ids = list(query_results.docid)

        return final_results