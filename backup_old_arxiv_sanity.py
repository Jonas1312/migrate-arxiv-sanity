import json
from datetime import date
from time import sleep, time

import requests
from tqdm import tqdm

cookies = {
    "session": "",
}


def get_total_number_papers_library():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "http://www.arxiv-sanity.com/library",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(
        "http://www.arxiv-sanity.com/library", headers=headers, cookies=cookies
    )

    response = response.text

    # TODO: use regex
    start_index = response.find('var numresults = "') + 18
    stop_index = response.find('";', response.find('var numresults = "'))
    num_papers_in_library = int(response[start_index:stop_index])
    return num_papers_in_library


def delete_paper_from_library(paper_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://www.arxiv-sanity.com",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "http://www.arxiv-sanity.com/library",
    }

    data = {"pid": paper_id}

    response = requests.post(
        "http://www.arxiv-sanity.com/libtoggle",
        headers=headers,
        cookies=cookies,
        data=data,
    )
    assert response.text == "OFF", response.text


def get_library():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "http://www.arxiv-sanity.com/library",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(
        "http://www.arxiv-sanity.com/library", headers=headers, cookies=cookies
    )

    response = response.text
    start_index = response.find('[{"')
    stop_index = response.find('"}];\n') + 3
    library_json = response[start_index:stop_index]
    library_json = json.loads(library_json)
    return library_json


def save_library(library):
    with open(f"my_library_{str(time())}.json", "w") as outfile:
        json.dump(library, outfile)


def main():
    num_papers_in_library = get_total_number_papers_library()
    print(f"Found {num_papers_in_library} papers in library")

    library_complete = []

    library_partial = get_library()
    library_complete.extend(library_partial)

    # need to delete some papers to get the full library (200 papers displayed max)
    try:
        while len(library_complete) < num_papers_in_library:
            for paper_to_delete in (pbar := tqdm(library_partial)):
                paper_id = paper_to_delete["rawpid"]
                pbar.set_description(f"Deleting {paper_id}")
                delete_paper_from_library(paper_id)
                sleep(36)  # 20 requests per 1 minute max, 100 per 1 hour...
            library_partial = get_library()
            library_complete.extend(library_partial)
    except Exception as e:
        print(e)
    finally:
        save_library(library_complete)


if __name__ == "__main__":
    main()
