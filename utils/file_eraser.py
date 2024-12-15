import os
import logging

COLLECTION_DIR = "./collection"

COMPLETA_RESUELVE_DIR = f"{COLLECTION_DIR}/completa/resuelve"
COMPLETA_DISPONE_DIR = f"{COLLECTION_DIR}/completa/dispone"

VISTO_DIR = f"{COLLECTION_DIR}/visto"
CONSIDERANDO_DIR = f"{COLLECTION_DIR}/considerando"
RESUELVE_DIR = f"{COLLECTION_DIR}/resuelve"
DISPONE_DIR = f"{COLLECTION_DIR}/dispone"

DELETED_FILES_PATH = './deleted-files.txt'


def erase_file_from_dir(file, dir, delete_sentences = True):
    file_name = f"{dir}/{file}"
    if os.path.exists(file_name):
        os.remove(file_name)

    if delete_sentences and os.path.exists(dir + '/sentences/' + file):
        os.remove(dir + '/sentences/' + file)


def erase_file_from_everywhere(file, reason):
    logging.warn(f"Deleting file {file} from everywhere for {reason}")
    erase_file_from_dir(file, COMPLETA_RESUELVE_DIR, False)
    erase_file_from_dir(file, COMPLETA_DISPONE_DIR, False)
    erase_file_from_dir(file, VISTO_DIR)
    erase_file_from_dir(file, CONSIDERANDO_DIR)
    erase_file_from_dir(file, DISPONE_DIR)
    erase_file_from_dir(file, RESUELVE_DIR)
    save_deleted_file(file, reason)


def save_deleted_file(file, reason):
    with open(DELETED_FILES_PATH, "a+") as f:
        f.write(f"{file},{reason}\n")