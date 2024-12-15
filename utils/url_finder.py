# Set the path to your file here
FILE_PATH = 'downloads-meta.txt'

# Initialize the file_map dictionary only once when the module is loaded
_url_filename_map = None
_filename_url_map = None

def load_filename_url_to_map():
    global _filename_url_map
    if _filename_url_map is None:  # Load only if not already loaded
        _filename_url_map = {}
        
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue  # Skip lines that don't have all three parts
                
                key = parts[0].replace('.pdf', '')
                value = parts[2]
                _filename_url_map[key] = value

def get_url(file_name):
    # Ensure the file map is loaded
    load_filename_url_to_map()

    # Remove any extensions from the file_name
    key = file_name
    if ('/' in file_name):
        key = key.split('/')[-1]
    key = key.split('.')[0]
    return _filename_url_map.get(key, None)  # Returns None if key is not found


def load_url_filename_to_map():
    global _url_filename_map
    if _url_filename_map is None:  # Load only if not already loaded
        _url_filename_map = {}
        
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue  # Skip lines that don't have all three parts
                
                value = parts[0].replace('.pdf', '')
                key = parts[2]
                _url_filename_map[key] = value

def get_filename_from_url(doc_url):
    # Ensure the file map is loaded
    load_url_filename_to_map()
    
    # Remove any extensions from the file_name
    return _url_filename_map.get(doc_url, None)  # Returns None if key is not found


