import os

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

def create_embeddings(sections):
    return model.encode(sections)

file_path = '../../raw-digest/RES_PHCS_NÂº_259_03.pdf.txt'

with open(file_path, 'r') as f:
    text = f.read()
    embeddings = create_embeddings(text)

with open(file_path + '-embeddings.txt', 'w') as f:
    f.write(str(embeddings))