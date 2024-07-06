import pyterrier as pt

BASE_OUTPUT_DIR = "./indexes"
SPARSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/sparse_index"

VISTO_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/visto"

if not pt.started():
        pt.init()


#print(f"{VISTO_OUTPUT_DIR}/data.properties")
index = pt.IndexFactory.of(f"{VISTO_OUTPUT_DIR}/data.properties")
bm25 = pt.BatchRetrieve(index, wmodel="BM25")

result = bm25.search("Gabriel Tolosa")


meta = index.getMetaIndex()

print(meta.getAllItems(20196))

#doi = index.getDocumentIndex()

#print(doi.getDocumentEntry(20196).toString())

#print(result)