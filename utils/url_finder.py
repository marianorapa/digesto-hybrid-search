# Set the path to your file here
FILE_PATH = 'downloads-meta.txt'

# Initialize the file_map dictionary only once when the module is loaded
_file_map = None

def load_file_to_map():
    global _file_map
    if _file_map is None:  # Load only if not already loaded
        _file_map = {}
        
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue  # Skip lines that don't have all three parts
                
                key = parts[0].replace('.pdf', '')
                value = parts[2]
                _file_map[key] = value

def get_url(file_name):
    # Ensure the file map is loaded
    load_file_to_map()
    
    # Remove any extensions from the file_name
    key = file_name
    if ('/' in file_name):
        key = key.split('/')[-1]
    key = key.split('.')[0]
    return _file_map.get(key, None)  # Returns None if key is not found
