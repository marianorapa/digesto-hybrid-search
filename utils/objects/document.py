from utils.url_finder import get_filename_from_url
import urllib
from pypdf import PdfReader
import re

def file_was_downloaded(doc_url):
    return get_filename_from_url(doc_url) != None

def not_empty(doc_code):
    with open("downloads-empty.txt", 'r') as file:
        for line in file.readlines():
            # check if the file url contains the doc code passed as arg
            if line.split(",")[-1].split('cod=')[-1] == doc_code:
                return False
    return True

def not_deleted(doc_url):
    filename = get_filename_from_url(doc_url)
    with open("deleted-files.txt", 'r') as file:
        for line in file.readlines():
            if line.split(",")[0] == filename:
                return False
    return True

def check_doc_was_indexed(doc_code, doc_url):
    file_downloaded = file_was_downloaded(doc_url)
    not_empty_result = not_empty(doc_code)
    not_deleted_result = not_deleted(doc_url)
    return file_downloaded and not_empty_result and not_deleted_result
    
class Document:
    def __init__(self, url = None, content_bytes = None, file_name = None):
        self.id = None
        self.url = url
        if url:
            self.set_id_from_url(url)
        self.content_bytes = content_bytes
        self.file_name = file_name
        self.pdf_path = None
        self.txt_path = None
        self.txt_file_name = None
        self.successful = None
        self.error_type = None
        self.visto_file_path = None
        self.considerando_file_path = None
        self.resolutiva_file_path = None
        self.resuelve_file_path = None
        self.dispone_file_path = None

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def set_id_from_url(self, url):
        self.id = int(url.split("cod=")[-1])

    def get_url(self):
        return f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={self.id}"

    def is_indexed(self):
        return check_doc_was_indexed(self.get_id(), self.get_url())

    def cleaned_filename(self):
        return urllib.parse.quote_plus(self.file_name)
    
    def set_pdf_path(self, path):
        self.pdf_path = path
    
    def set_txt_path(self, path):
        self.txt_path = path
    
    def get_txt_filename(self):
        return self.cleaned_filename().replace('pdf', 'txt')
    
    def get_text_path(self):
        return self.txt_path

    def set_visto_file_path(self, path):
        self.visto_file_path = path

    def set_considerando_file_path(self, path):
        self.considerando_file_path = path

    def set_resolutiva_file_path(self, path):
        self.resolutiva_file_path = path

    def set_resuelve_file_path(self, path):
        self.resuelve_file_path = path

    def set_dispone_file_path(self, path):
        self.dispone_file_path = path

    def get_text_content(self):
        if self.txt_path is None:
            reader = PdfReader(self.pdf_path)
            text = ""
            for page in reader.pages:  # iterate the document pages
                text += page.extract_text()
            return self.remove_exp_fragment(text)
        else:
            with open(self.txt_path, 'r') as file:
                return file.read().strip()
    
    def remove_exp_fragment(self, text):
        # Define the regular expression pattern to match the fragment
        pattern = r'EXP-LUJ:\s*\d+/\d+'

        # Replace the matched fragment with an empty string
        cleaned_text = re.sub(pattern, '', text)

        return cleaned_text.strip()

    
    def success(self):
        self.successful = True
        return self
    
    def is_success(self):
        return self.successful
        
    def error(self, error):
        self.successful = False
        self.error_type = error
        return self
    
    def is_resolution(self):
        return self.cleaned_filename().startswith("RES")
    
    def is_disposition(self):
        return self.cleaned_filename().startswith("DISP")
    
    def to_json(self):
        return {
            "id": self.id,
            "url": self.url,
            "file_name": self.file_name,
            "pdf_path": self.pdf_path,
            "txt_path": self.txt_path,
            "visto_file_path": self.txt_path,
            "considerando_file_path": self.txt_path,
            "resolutiva_file_path": self.txt_path,
            "dispone_file_path": self.txt_path,
            "resuelve_file_path": self.txt_path,
            "successful": self.successful,
            "error": self.error_type if self.error_type else None
        }
    
    def from_json(json):
        document = Document()
        document.id = json["id"]
        document.url = json["url"]
        document.file_name = json["file_name"]
        document.pdf_path = json["pdf_path"]
        document.txt_path = json["txt_path"]
        document.visto_file_path = json["visto_file_path"]
        document.considerando_file_path = json["considerando_file_path"]
        document.resolutiva_file_path = json["resolutiva_file_path"]
        document.dispone_file_path = json["dispone_file_path"]
        document.resuelve_file_path = json["resuelve_file_path"]
        document.successful = json["successful"]
        document.error_type = json["error"] if "error" in json else None
        return document