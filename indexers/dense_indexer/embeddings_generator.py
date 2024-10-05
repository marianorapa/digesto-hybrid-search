import os
from sentence_transformers import SentenceTransformer
import logging
import csv
from tqdm import tqdm
import numpy as np
import os.path
from utils.file_eraser import erase_file_from_everywhere
import faiss
import json

BASE_INPUT_DIR = "./collection"
VISTO_INPUT_DIR = f"{BASE_INPUT_DIR}/visto/sentences"
CONSIDERANDO_INPUT_DIR = f"{BASE_INPUT_DIR}/considerando/sentences"
RESUELVE_INPUT_DIR = f"{BASE_INPUT_DIR}/resuelve/sentences"
DISPONE_INPUT_DIR = f"{BASE_INPUT_DIR}/dispone/sentences"

BASE_OUTPUT_DIR = "./indexes"
DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index"

VISTO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/visto"
CONSIDERANDO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/considerando"
RESUELVE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/resuelve"
DISPONE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/dispone"

COMPLETE_DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index/completa"
COMPLETE_COMPLETE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/completa"
COMPLETE_RESUELVE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/resuelve"
COMPLETE_DISPONE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/dispone"

def create_directories():
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.mkdir(BASE_OUTPUT_DIR)

    if not os.path.exists(DENSE_OUTPUT_DIR):
        os.mkdir(DENSE_OUTPUT_DIR)

    if not os.path.exists(VISTO_OUTPUT_DIR):
        os.mkdir(VISTO_OUTPUT_DIR)

    if not os.path.exists(CONSIDERANDO_OUTPUT_DIR):
        os.mkdir(CONSIDERANDO_OUTPUT_DIR)

    if not os.path.exists(RESUELVE_OUTPUT_DIR):
        os.mkdir(RESUELVE_OUTPUT_DIR)

    if not os.path.exists(DISPONE_OUTPUT_DIR):
        os.mkdir(DISPONE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_DENSE_OUTPUT_DIR):
        os.mkdir(COMPLETE_DENSE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_RESUELVE_OUTPUT_DIR):
        os.mkdir(COMPLETE_RESUELVE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_DISPONE_OUTPUT_DIR):
        os.mkdir(COMPLETE_DISPONE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_COMPLETE_OUTPUT_DIR):
        os.mkdir(COMPLETE_COMPLETE_OUTPUT_DIR)

        

def add_to_dense_index(dense_indexes, embedding, document_type, filename):
    dense_indexes[document_type]["index"].add(embedding.reshape(1, -1))
    counter = dense_indexes[document_type]["counter"]
    dense_indexes[document_type]["counter"] = dense_indexes[document_type]["counter"] + 1
    dense_indexes[document_type]["metadata"][counter] = filename

def create_embedding(model, sentence):
    return model.encode(sentence)

def get_mean_of_embeddings_and_save(sentence_embeddings, OUTPUT_DIR, FILE):
    if len(sentence_embeddings) == 0:
        logging.error(f"{FILE} without sentence embeddings in {OUTPUT_DIR}")
        return
    elif len(sentence_embeddings) == 1:
        embedding = sentence_embeddings[0]
    else:
        embedding = np.mean(sentence_embeddings, axis=0)

    filename = FILE.replace(".csv", ".txt")
    np.savetxt(f"{OUTPUT_DIR}/{filename}", embedding)

    return embedding

def generate_section_embedding(model, INPUT_DIR, OUTPUT_DIR):
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):

            # Me fijo si no hay un embedding ya generado
            if not os.path.exists(f"{OUTPUT_DIR}/{file.replace('.csv', '.txt')}"):
                sentence_embeddings = []
                with open(INPUT_DIR + "/" + file) as f:
                    reader = csv.reader(f)
                    for row in reader:
                        for sentence in row:
                            sentence_embeddings.append(create_embedding(model, sentence))

                    embedding = get_mean_of_embeddings_and_save(sentence_embeddings, OUTPUT_DIR, file)


def generate_sections_embeddings(model):
    generate_section_embedding(model, VISTO_INPUT_DIR, VISTO_OUTPUT_DIR)
    generate_section_embedding(model, CONSIDERANDO_INPUT_DIR, CONSIDERANDO_OUTPUT_DIR)
    generate_section_embedding(model, RESUELVE_INPUT_DIR, RESUELVE_OUTPUT_DIR)
    generate_section_embedding(model, DISPONE_INPUT_DIR, DISPONE_OUTPUT_DIR)


def mean_sections_embeddings(filename, dense_indexes):
    embeddings = []
    section_embeddings = {}

    if os.path.exists(f"{VISTO_OUTPUT_DIR}/{filename}"):
        with open(f"{VISTO_OUTPUT_DIR}/{filename}", "r") as f:
            #embeddings.append(np.loadtxt(f"{VISTO_OUTPUT_DIR}/{filename}"))
            section_embeddings["visto"] = np.loadtxt(f"{VISTO_OUTPUT_DIR}/{filename}")
    else:
        logging.error(f"File not exist {VISTO_OUTPUT_DIR}/{filename}")

    if os.path.exists(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}"):
        with open(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}", "r") as f:
            #embeddings.append(np.loadtxt(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}"))
            section_embeddings["considerando"] = np.loadtxt(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}")
    else:
        logging.error(f"File not exist {CONSIDERANDO_OUTPUT_DIR}/{filename}")

    if os.path.exists(f"{RESUELVE_OUTPUT_DIR}/{filename}") or os.path.exists(f"{DISPONE_OUTPUT_DIR}/{filename}"):
        if os.path.exists(f"{RESUELVE_OUTPUT_DIR}/{filename}"):
            with open(f"{RESUELVE_OUTPUT_DIR}/{filename}", "r") as f:
                #embeddings.append(np.loadtxt(f"{RESUELVE_OUTPUT_DIR}/{filename}"))
                section_embeddings["resuelve"] = np.loadtxt(f"{RESUELVE_OUTPUT_DIR}/{filename}")
        else:
            with open(f"{DISPONE_OUTPUT_DIR}/{filename}", "r") as f:
                #embeddings.append(np.loadtxt(f"{DISPONE_OUTPUT_DIR}/{filename}"))
                section_embeddings["dispone"] = np.loadtxt(f"{DISPONE_OUTPUT_DIR}/{filename}")
    else:
        logging.error(f"File not exist {RESUELVE_OUTPUT_DIR}/{filename} or {DISPONE_OUTPUT_DIR}/{filename}")

   #if len(embeddings) == 3:
    if len(section_embeddings.keys()) == 3: 
        #document_embedding = np.mean(embeddings, axis=0)
        document_embedding = np.mean(list(section_embeddings.values()), axis=0)

        for section in section_embeddings:
            add_to_dense_index(dense_indexes, section_embeddings[section], section, filename)

        if filename.startswith("RES"):
            np.savetxt(f"{COMPLETE_RESUELVE_OUTPUT_DIR}/{filename}", document_embedding)
            add_to_dense_index(dense_indexes, document_embedding, "resoluciones", filename)
            add_to_dense_index(dense_indexes, document_embedding, "completo", filename)
        elif filename.startswith("DISP"):
            np.savetxt(f"{COMPLETE_DISPONE_OUTPUT_DIR}/{filename}", document_embedding)
            add_to_dense_index(dense_indexes, document_embedding, "disposiciones", filename)
            add_to_dense_index(dense_indexes, document_embedding, "completo", filename)
        else:
            logging.error(f"File not exist {COMPLETE_RESUELVE_OUTPUT_DIR}/{filename} or {COMPLETE_DISPONE_OUTPUT_DIR}/{filename}")
    else:
        logging.error(f"Couldnt find all embedings for file {filename}")
        erase_file_from_everywhere(filename, "MISSING_EMBEDDINGS")


def generate_documents_embeddings(dense_indexes):
    deleted_files = []
    try: 
        with open("./deleted-files.txt", "r") as deleted:
            for line in deleted.readlines():
                filename = line.split(",")[0]
                deleted_files.append(filename)
    except FileNotFoundError: 
        logging.info("No deleted-files.txt file found")

    with open("./preprocessors/digest_downloader_converter/downloads-meta.txt") as f:
        for line in f.readlines():
            filename = line.split(",")[0].replace("pdf", "txt")
            if (filename not in deleted_files):
                mean_sections_embeddings(filename, dense_indexes)

def create_dense_indexes_structure():
    dense_indexes = {}

    for key in ["visto", "considerando", "resuelve", "dispone", "resoluciones", "disposiciones", "completo"]:
        dense_indexes[key] = {}
        dense_indexes[key]["index"] = faiss.IndexFlatL2(768)
        dense_indexes[key]["counter"] = 0
        dense_indexes[key]["metadata"] = {}

    return dense_indexes

def persist_dense_indexes(dense_indexes):
     print(dense_indexes)

     for key in dense_indexes:

        if key == "visto":
            root_directory = VISTO_OUTPUT_DIR
        elif key == "considerando":
            root_directory = CONSIDERANDO_OUTPUT_DIR
        elif key == "resuelve":
            root_directory = RESUELVE_OUTPUT_DIR
        elif key == "dispone":
            root_directory = DISPONE_OUTPUT_DIR
        elif key == "resoluciones":
            root_directory = COMPLETE_RESUELVE_OUTPUT_DIR
        elif key == "disposiciones":
            root_directory = COMPLETE_DISPONE_OUTPUT_DIR
        elif key == "completo":
            root_directory = COMPLETE_COMPLETE_OUTPUT_DIR

        index = dense_indexes[key]["index"]
        faiss.write_index(index, f"{root_directory}/index_{key}.bin")

        with open(f"{root_directory}/metadata_{key}.json", "w") as outfile: 
            json.dump(dense_indexes[key]["metadata"], outfile)


def generate_embeddings():
    logging.info("Dense Indexer Started")

    create_directories()

    model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

    generate_sections_embeddings(model)

    dense_indexes = create_dense_indexes_structure()

    generate_documents_embeddings(dense_indexes)

    persist_dense_indexes(dense_indexes)

   

