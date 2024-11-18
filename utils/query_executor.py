from utils.url_finder import get_filename_from_url
import requests
from bs4 import BeautifulSoup
from retrievers.sparse_retriever.terrier_retriever import get_relevant_documents_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_relevant_documents_hybrid
from retrievers.dense_retriever.dense_retriever import get_relevant_documents_dense
from tabulate import tabulate

def execute_query_current_digest(query, k):
    url = 'https://resoluciones.unlu.edu.ar/busqueda.avanzada.php'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Origin': 'https://resoluciones.unlu.edu.ar',
        'Referer': 'https://resoluciones.unlu.edu.ar/busqueda.avanzada.php?action=replay&busq_id=0&ord=0&page=1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    data = {
        '_qf__busqrapida': '',
        'pag': '0',
        'consulta': query,  # parameterize this value
        'tipo_documento': '',
        'anio_desde': '1984',
        'anio_hasta': '2024'
    }

    # Send POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to fetch the page")
        return []

    # Parse HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all 'div' elements with class 'boletinDoc'
    boletin_divs = soup.find_all('div', class_='boletinDoc')
    
    # Extract hrefs from 'a' elements within each 'boletinDoc' div
    links = []
    i = 0
    while i < k and i < len(boletin_divs):
        div = boletin_divs[i]
        a_tag = div.find('a', href=True)
        if a_tag:
            links.append(a_tag['href'])
        i += 1
    return links


def get_doc_id(link):
    return link.split("cod=")[-1]

def query_current_digest(query, k):
    result_links_URI = execute_query_current_digest(query, k)
    output = []
    rank = 1
    for link in result_links_URI:
        full_link = "https://resoluciones.unlu.edu.ar/" + link.replace("frame", "view")
        doc_code = get_doc_id(full_link)
        output_entry = [rank, doc_code, full_link]
        output.append(output_entry)
        rank += 1
    return output

def build_result_list(retriever_results, url_position):
    result = []
    rank = 1
    for doc in retriever_results:
        url = doc[url_position]
        doc_code = get_doc_id(url)
        result.append([rank, doc_code, url])
        rank += 1
    return result


def query_sparse(query, k):
    default_index = "COMPLETE_COMPLETE"
    docs = get_relevant_documents_sparse(default_index, query, k)
    return build_result_list(docs, 4)

def query_dense(query, k):
    default_index = "COMPLETE_COMPLETE"
    docs = get_relevant_documents_dense(default_index, query, k)
    return build_result_list(docs, 4)

def query_hybrid(query, k):
    default_index = "COMPLETE_COMPLETE"
    docs = get_relevant_documents_hybrid(default_index, query, k)
    return build_result_list(docs, 4)

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
    

def check_docs_were_indexed(results):
    # input format: [rank, doc_code, url]
    enriched_docs = []
    for entry in results:
        doc_code = entry[1]
        doc_url = entry[2]
        is_indexed = check_doc_was_indexed(doc_code, doc_url)
        enriched_docs.append([doc_code, doc_url, is_indexed])

    return enriched_docs

def check_relevant_docs_where_indexed(relevant_documents):
    relevant_documents_with_url = []
    order = 1
    for relevant_document in relevant_documents:
        relevant_documents_with_url.append([order, relevant_document, f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={relevant_document}"])
        order = order + 1

    return check_docs_were_indexed(relevant_documents_with_url)

def print_results(relevant_documents_enriched_results, current_digest_results, sparse_results, dense_results, hybrid_results):
    
    empty_result_string = "-"

    if relevant_documents_enriched_results == []:
        relevant_documents_enriched_results = [[empty_result_string, empty_result_string, empty_result_string]]
    print("\nRelevant Documents Searched:")
    table = tabulate(relevant_documents_enriched_results, 
                    headers=["ID", "URL", "Indexed"],
                    tablefmt="tsv",
                    colalign=("center", "center", "center"))
    print(table)

    if current_digest_results == []:
        current_digest_results = [[empty_result_string, empty_result_string, empty_result_string]]
    print("\nCurrent Digest Results:")
    table = tabulate(current_digest_results, 
                    headers=["ID", "URL", "Indexed"],
                    tablefmt="tsv",
                    colalign=("center", "center", "center"))
    print(table)

    if sparse_results == []:
        sparse_results = [[empty_result_string, empty_result_string, empty_result_string]]
    print("\nSparse Results:")
    table = tabulate(sparse_results, 
                    headers=["Ranking", "ID", "URL"],
                    tablefmt="tsv",
                    colalign=("center", "center", "center"))
    print(table)

    if dense_results == []:
            dense_results = [[empty_result_string, empty_result_string, empty_result_string]]
    print("\nDense Results:")
    table = tabulate(dense_results, 
                    headers=["Ranking", "ID", "URL"],
                    tablefmt="tsv",
                    colalign=("center", "center", "center"))
    print(table)

    if hybrid_results == []:
            hybrid_results = [[empty_result_string, empty_result_string, empty_result_string]]
    print("\nHybrid Results:")
    table = tabulate(hybrid_results, 
                    headers=["Ranking", "ID", "URL"],
                    tablefmt="tsv",
                    colalign=("center", "center", "center"))
    print(table)

def query(query, k, relevant_documents):

    relevant_documents_enriched_results = check_relevant_docs_where_indexed(relevant_documents)

    current_digest_results = query_current_digest(query, k)
    
    sparse_results = query_sparse(query, k)
    
    dense_results = query_dense(query, k)
    
    hybrid_results = query_hybrid(query, k)
    
    current_digest_enriched_results = check_docs_were_indexed(current_digest_results)

    print_results(relevant_documents_enriched_results, current_digest_enriched_results, sparse_results, dense_results, hybrid_results)
