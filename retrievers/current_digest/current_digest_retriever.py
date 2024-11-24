from bs4 import BeautifulSoup
import requests
from utils.objects.document import Document
from utils.objects.ranking import Ranking

def build_headers(session_id):
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'PHPSESSID={session_id}',
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


def get_session_id(base_url):
    response = requests.get(base_url)
    return response.cookies.get('PHPSESSID')


def execute_query_current_digest(query):
    base_url = 'https://resoluciones.unlu.edu.ar/busqueda.avanzada.php'
    session_id = get_session_id(base_url)
    results = do_execute_query_current_digest(base_url, query, session_id)
    page = 2
    while len(results) > 0:
        url = base_url + f"?action=replay&busq_id=0&ord=0&page={page}"
        page_results = do_execute_query_current_digest(url, query, session_id)
        if len(page_results) == 0:
            break  # No more results on this page, stop fetching more pages
        results.extend(page_results)
        page += 1

    return results


def do_execute_query_current_digest(url, query, session_id=None):
    headers = build_headers(session_id)
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
    while i < len(boletin_divs):
        div = boletin_divs[i]
        a_tag = div.find('a', href=True)
        if a_tag:
            links.append(a_tag['href'])
        i += 1
    return links


def get_relevant_documents_current_digest(index, query, k, relevant_documents_ids):
    # TODO index modification is not implemented, only querying default index adding parameter to be consistent
    #  with other retrievers

    result_links_URI = execute_query_current_digest(query)

    ranking_current_digest = Ranking()
    ranking_current_digest.set_ranking_name("Rank Current Digest")
    ranking_current_digest.set_k_documents(k)
    ranking_current_digest.set_relevant_documents_ids(relevant_documents_ids)

    for link in result_links_URI:
        document = Document()
        document.set_id_from_url(link)
        ranking_current_digest.add_document(document)

    return ranking_current_digest