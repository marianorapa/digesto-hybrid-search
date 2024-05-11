import fitz_old as fitz
import re
import requests
from tqdm import tqdm
import os
import logging
import urllib


BASE_COLLECTION_DIR = "./collection"
COMPLETE_COLLECTION_DIR = "/completa"
RESOLUTION_DIR = BASE_COLLECTION_DIR + COMPLETE_COLLECTION_DIR + "/resuelve"
DISPOSITION_DIR = BASE_COLLECTION_DIR + COMPLETE_COLLECTION_DIR + "/dispone"

BASE_DIR = "./preprocessors/digest_downloader_converter"
RAW_OUTPUT_DIR = f"{BASE_DIR}/raw/"

logging.basicConfig(level=logging.DEBUG, filename=f"{BASE_DIR}/app.log", filemode="w")

def create_directories():
    if not os.path.exists(RAW_OUTPUT_DIR):
        os.mkdir(RAW_OUTPUT_DIR)

    if not os.path.exists(BASE_COLLECTION_DIR):
        os.mkdir(BASE_COLLECTION_DIR)

    if not os.path.exists(BASE_COLLECTION_DIR + COMPLETE_COLLECTION_DIR):
        os.mkdir(BASE_COLLECTION_DIR + COMPLETE_COLLECTION_DIR)

    if not os.path.exists(RESOLUTION_DIR):
        os.mkdir(RESOLUTION_DIR)

    if not os.path.exists(DISPOSITION_DIR):
        os.mkdir(DISPOSITION_DIR)

def remove_exp_fragment(text):
    # Define the regular expression pattern to match the fragment
    pattern = r'EXP-LUJ:\s*\d+/\d+'

    # Replace the matched fragment with an empty string
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text.strip()

def parse_pdf_content(pdf_content):
    # Use fitz to open the PDF from binary content
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in doc:  # iterate the document pages
        text += page.get_text()
    return remove_exp_fragment(text)

def save_parsed_text(cleaned_file_name, parsed_text):
    filepath = ""
    if cleaned_file_name.startswith("RES"):
        filepath = RESOLUTION_DIR + "/" + cleaned_file_name
    elif cleaned_file_name.startswith("DISP"):
        filepath = DISPOSITION_DIR + "/" + cleaned_file_name

    filepath = filepath.replace("pdf", "txt")

    if os.path.isfile(filepath):
        logging.warning(f"{filepath} already exist when trying to save")

    with open(filepath, "w") as file:
        file.write(parsed_text)

def process_not_found_document(filename, url):
    with open(f'{BASE_DIR}/downloads-not-founds.txt', 'a', encoding="utf-8") as file:
        file.write(f"{filename},{url}\n")

def not_found_document(content):
    return "El documento que ha solicitado no existe." in str(content) or "No tiene permisos suficientes para ver este documento." in str(content)

def process_valid_document(file_name, response, url):
    cleaned_file_name = urllib.parse.quote_plus(file_name)

    parsed_text = parse_pdf_content(response.content)

    save_complete_pdf(cleaned_file_name, response)

    if len(parsed_text) > 1:
        with open(f'{BASE_DIR}/downloads-meta.txt', 'a', encoding="utf-8") as file:
            file.write(f"{cleaned_file_name},{file_name},{url}\n")

        save_parsed_text(cleaned_file_name, parsed_text)
    else:
        with open(f'{BASE_DIR}/downloads-empty.txt', 'a', encoding="utf-8") as file:
            file.write(f"{file_name},{url}\n")

def process_document_from_url(url, index):
    # Make an HTTP GET request to download the PDF file
    response = requests.get(url, stream=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1]
        except:
            file_name = f"doc-{index}"

        if not_found_document(response.content):
            process_not_found_document(file_name, url)
        else:
            process_valid_document(file_name, response, url)

    else:
        logging.warning(f"Failed to download {url}. Status code: {response.status_code}")


def save_complete_pdf(cleaned_file_name, response):
    filepath = RAW_OUTPUT_DIR + cleaned_file_name

    if os.path.isfile(filepath):
        logging.warning(f"{filepath} already exist when trying to save")

    with open(filepath, "wb") as file:
        file.write(response.content)


def download_documents(id_from: int, id_to: int):

    create_directories()

    for i in tqdm(range(id_from, id_to + 1)):
        try:
            url = f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={i}"
            process_document_from_url(url, i)

        except Exception as e:
            logging.warning(f"Skipping process of URL {url}. Exception {e}")
            continue

    return id_to + 1


def download_and_convert(doc_id_from, doc_id_to):

    progress_file = f'{BASE_DIR}/downloads-progress.txt'
    try:
        with open(progress_file, 'r') as file:
            # Read the single value from the file
            value = file.readline().strip()
    except FileNotFoundError as e:
        value = "0"

    last_id = download_documents(max(doc_id_from, int(value)), doc_id_to)

    with open(progress_file, 'w', encoding="utf-8") as file:
        file.write(str(last_id))
