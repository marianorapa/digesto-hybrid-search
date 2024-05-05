import re
import requests
from tqdm import tqdm
import os
import logging
import urllib

logging.basicConfig(level=logging.DEBUG, filename="app.log",filemode="w")

directory = "collection/"


def ensure_unique_filepath(cleaned_file_name):
    filepath = os.path.join(directory, f"{cleaned_file_name}")
    if os.path.isfile(filepath):
        logging.error(f"{filepath} already exist when trying to save")

        counter = 0
        new_filepath = f"{filepath}_{counter}"
        while os.path.isfile(new_filepath):
            counter += 1
            new_filepath = f"{filepath}_{counter}"
        filepath = new_filepath

    return filepath

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

        with open('downloads-meta.txt', 'a', encoding="utf-8") as file:
            file.write(f"{cleaned_file_name},{file_name},{url}\n")

        filepath = ensure_unique_filepath(cleaned_file_name)

        with open(filepath, "wb") as file:
            file.write(response.content)

    else:
        logging.warning(f"Failed to download {url}. Status code: {response.status_code}")


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

    try:
        with open('downloads-progress.txt', 'r') as file:
            # Read the single value from the file
            value = file.readline().strip()
    except FileNotFoundError as e:
        value = "0"

    last_id = download_documents(doc_id_from, doc_id_to)

    with open('downloads-progress.txt', 'w', encoding="utf-8") as file:
        file.write(str(last_id))
