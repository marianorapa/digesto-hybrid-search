import os

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')
number_of_docs = len(os.listdir('input'))

def get_progress():
    with open('../embeddings-progress.txt', 'r') as file:
        # Read the single value from the file
        return int(file.readline().strip())

def create_embeddings(sections):
    return model.encode(sections)

# start_line = get_progress()
# print(start_line)
# print(number_of_docs)

embeddings = create_embeddings(sentences)
print(embeddings)


