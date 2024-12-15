from utils.url_finder import get_filename_from_url


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
    def __init__(self):
        self.id = None
        self.url = None

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
