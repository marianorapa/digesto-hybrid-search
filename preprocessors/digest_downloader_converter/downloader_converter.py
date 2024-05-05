import fitz_old as fitz
import re
import requests
from tqdm import tqdm
import os
import logging
import urllib


BASE_COLLECTION_DIR = "collection/"
RESOLUTION_DIR = BASE_COLLECTION_DIR + "completa/resuelve/"
DISPOSITION_DIR = BASE_COLLECTION_DIR + "completa/dispone/"

BASE_DIR = "preprocessors/digest_downloader_converter/"
RAW_OUTPUT_DIR = "%sraw/" % BASE_DIR

logging.basicConfig(level=logging.DEBUG, filename=f"{BASE_DIR}app.log",filemode="w")

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


def ensure_unique_filepath(cleaned_file_name):
    filepath = os.path.join(BASE_COLLECTION_DIR, f"{cleaned_file_name}")
    if os.path.isfile(filepath):
        logging.error(f"{filepath} already exist when trying to save")

        counter = 0
        new_filepath = f"{filepath}_{counter}"
        while os.path.isfile(new_filepath):
            counter += 1
            new_filepath = f"{filepath}_{counter}"
        filepath = new_filepath

    return filepath


def save_parsed_text(parsed_text, filename):
    final_filepath = ""
    if filename.startswith("RES"):
        final_filepath = RESOLUTION_DIR + filename
    elif filename.startswith("DISP"):
        final_filepath = DISPOSITION_DIR + filename

    with open(final_filepath.replace("pdf", "txt"), "w") as file:
        file.write(parsed_text)


def process_document_from_url(url, index):
    # Make an HTTP GET request to download the PDF file
    response = requests.get(url, stream=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1]
        except:
            file_name = f"doc-{index}"

        cleaned_file_name = urllib.parse.quote_plus(file_name)

        with open(f'{BASE_DIR}downloads-meta.txt', 'a', encoding="utf-8") as file:
            file.write(f"{cleaned_file_name},{file_name},{url}\n")

        # filepath = ensure_unique_filepath(cleaned_file_name)

        save_complete_pdf(cleaned_file_name, response)

        parsed_text = parse_pdf_content(response.content)
        save_parsed_text(parsed_text, cleaned_file_name)

    else:
        logging.warning(f"Failed to download {url}. Status code: {response.status_code}")


def save_complete_pdf(filepath, response):
    with open(RAW_OUTPUT_DIR + filepath, "wb") as file:
        file.write(response.content)


def download_documents(id_from: int, id_to: int):
    for i in tqdm(range(id_from, id_to + 1)):
        try:
            url = f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={i}"
            process_document_from_url(url, i)

        except Exception as e:
            logging.warning(f"Skipping process of URL {url}. Exception {e}")
            continue

    return id_to + 1


def download_and_convert(doc_id_from, doc_id_to):

    progress_file = f'{BASE_DIR}downloads-progress.txt'
    try:
        with open(progress_file, 'r') as file:
            # Read the single value from the file
            value = file.readline().strip()
    except FileNotFoundError as e:
        value = "0"

    last_id = download_documents(max(doc_id_from, int(value)), doc_id_to)

    with open(progress_file, 'w', encoding="utf-8") as file:
        file.write(str(last_id))
