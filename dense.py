from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')
index = faiss.IndexFlatL2(768)


sentence = "Esta es una sentencia de prueba, para obtener un embedding"

embedding = model.encode(sentence)

faiss_embedding = embedding.reshape(1, -1)

index.add(faiss_embedding)





sentence = "Esta es una sentencia productiva, para terminar el tp"

embedding = model.encode(sentence)

faiss_embedding = embedding.reshape(1, -1)

index.add(faiss_embedding)





query_sentence = "Esta es una sentencia de prueba"

query_embedding = model.encode(query_sentence)

faiss_query_embedding = query_embedding.reshape(1, -1)

k = 2
D, I = index.search(faiss_query_embedding, k)

print("Distancias:\n", D)
print("Índices:\n", I)

#faiss.write_index(index, "index.bin")
#index2 = faiss.read_index("index.bin") 