import requests
from tqdm import tqdm
import os
import logging
import time
from utils.objects.document import Document
from utils.objects.metadata import Metadata

logger = logging.getLogger("digesto-hybrid-search-logger")

config = os.environ
metadata = Metadata(config["DOWNLOADER_CONVERTER_META_FILE"])

RESOLUTION_DIR = config["RESOLUTIONS_DIR"]
DISPOSITION_DIR = config["DISPOSITIONS_DIR"]

RAW_OUTPUT_DIR = config["DOWNLOADER_CONVERTER_RAW_DIR"]
DOWNLOADS_NOT_FOUND = config["DOWNLOADER_CONVERTER_NOT_FOUND_DOCS"]


def create_directories():
    os.makedirs(RESOLUTION_DIR, exist_ok = True)
    os.makedirs(DISPOSITION_DIR, exist_ok = True)
    os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)


def save_parsed_text(parsed_text, document: Document):
    filepath = ""
    if document.is_resolution():
        filepath = RESOLUTION_DIR + "/" + document.get_txt_filename()
    elif document.is_disposition():
        filepath = DISPOSITION_DIR + "/" + document.get_txt_filename()

    if os.path.isfile(filepath):
        logger.warning(f"{filepath} already exist when trying to save")

    with open(filepath, "w") as file:
        file.write(parsed_text)
    document.set_txt_path(filepath)


def process_not_found_document(filename, url):
    with open(DOWNLOADS_NOT_FOUND, 'a', encoding="utf-8") as file:
        file.write(f"{filename},{url}\n")


def not_found_document(content):
    return "El documento que ha solicitado no existe." in str(content) or "No tiene permisos suficientes para ver este documento." in str(content)


def process_valid_document(file_name, response, url):
    document = Document(url=url, content_bytes=response.content, file_name=file_name)
    save_as_pdf(document)

    parsed_text = document.get_text_content()

    if len(parsed_text) > 1:
        save_parsed_text(parsed_text, document)
        metadata.success(document)
    else:
        metadata.error(document, "Empty doc") # TODO: enum/class for error


def process_document_from_url(url, index, retry_number=0):
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
        retry_number = retry_number + 1
        if retry_number < 5:
            logger.warning(f"Failed to download {url}. Status code: {response.status_code}, Retrying...")
            time.sleep(10)
            process_document_from_url(url, index, retry_number=retry_number)
        else:
            logger.error(f"Failed to download {url}. Status code: {response.status_code}, Retries exceeded")


def save_as_pdf(document: Document):

    filepath = f"{RAW_OUTPUT_DIR}/{document.cleaned_filename()}"

    if os.path.isfile(filepath):
        logger.warning(f"{filepath} already exist when trying to save")

    with open(filepath, "wb") as file:
        file.write(document.content_bytes)
    document.set_pdf_path(filepath)

    return filepath


def download_documents(number_of_docs: int):

    create_directories()

    for i in tqdm(range(0, number_of_docs + 1)):
        try:
            url = f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={i}"
            process_document_from_url(url, i)

        except Exception as e:
            logger.warning(f"Skipping process of URL {url}. Exception {e}")
            continue

    return number_of_docs + 1


def download_and_convert(doc_id_to):
    logger.info("Downloader Converter Started")
    download_documents(doc_id_to)
    metadata.save()
