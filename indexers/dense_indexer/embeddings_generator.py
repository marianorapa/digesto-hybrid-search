import os
from sentence_transformers import SentenceTransformer
import logging
import csv
from tqdm import tqdm
import numpy as np
import os.path
from utils.file_eraser import erase_file_from_everywhere

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

                    get_mean_of_embeddings_and_save(sentence_embeddings, OUTPUT_DIR, file)


def generate_sections_embeddings(model):
    generate_section_embedding(model, VISTO_INPUT_DIR, VISTO_OUTPUT_DIR)
    generate_section_embedding(model, CONSIDERANDO_INPUT_DIR, CONSIDERANDO_OUTPUT_DIR)
    generate_section_embedding(model, RESUELVE_INPUT_DIR, RESUELVE_OUTPUT_DIR)
    generate_section_embedding(model, DISPONE_INPUT_DIR, DISPONE_OUTPUT_DIR)


def mean_sections_embeddings(filename):
    embeddings = []

    if os.path.exists(f"{VISTO_OUTPUT_DIR}/{filename}"):
        with open(f"{VISTO_OUTPUT_DIR}/{filename}", "r") as f:
            embeddings.append(np.loadtxt(f"{VISTO_OUTPUT_DIR}/{filename}"))
    else:
        logging.error(f"File not exist {VISTO_OUTPUT_DIR}/{filename}")

    if os.path.exists(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}"):
        with open(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}", "r") as f:
            embeddings.append(np.loadtxt(f"{CONSIDERANDO_OUTPUT_DIR}/{filename}"))
    else:
        logging.error(f"File not exist {CONSIDERANDO_OUTPUT_DIR}/{filename}")

    if os.path.exists(f"{RESUELVE_OUTPUT_DIR}/{filename}") or os.path.exists(f"{DISPONE_OUTPUT_DIR}/{filename}"):
        if os.path.exists(f"{RESUELVE_OUTPUT_DIR}/{filename}"):
            with open(f"{RESUELVE_OUTPUT_DIR}/{filename}", "r") as f:
                embeddings.append(np.loadtxt(f"{RESUELVE_OUTPUT_DIR}/{filename}"))
        else:
            with open(f"{DISPONE_OUTPUT_DIR}/{filename}", "r") as f:
                embeddings.append(np.loadtxt(f"{DISPONE_OUTPUT_DIR}/{filename}"))
    else:
        logging.error(f"File not exist {RESUELVE_OUTPUT_DIR}/{filename} or {DISPONE_OUTPUT_DIR}/{filename}")

    if len(embeddings) == 3: 
        document_embedding = np.mean(embeddings, axis=0)

        if filename.startswith("RES"):
            np.savetxt(f"{COMPLETE_RESUELVE_OUTPUT_DIR}/{filename}", document_embedding)
        elif filename.startswith("DISP"):
            np.savetxt(f"{COMPLETE_DISPONE_OUTPUT_DIR}/{filename}", document_embedding)
        else:
            logging.error(f"File not exist {COMPLETE_RESUELVE_OUTPUT_DIR}/{filename} or {COMPLETE_DISPONE_OUTPUT_DIR}/{filename}")
    else:
        logging.error(f"Couldnt find all embedings for file {filename}")
        erase_file_from_everywhere(filename, "MISSING_EMBEDDINGS")


def generate_documents_embeddings():
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
                mean_sections_embeddings(filename)

def generate_embeddings():
    logging.info("Dense Indexer Started")

    create_directories()

    model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

    generate_sections_embeddings(model)

    generate_documents_embeddings()
