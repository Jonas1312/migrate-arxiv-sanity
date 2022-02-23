import json
from time import sleep
from urllib.parse import quote

import requests
from tqdm import tqdm

cookies = {
    "session": "",
}


class PaperNotFound(Exception):
    pass


def get_paper_tags(paper_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://arxiv-sanity-lite.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    params = (("pid", paper_id),)
    response = requests.get(
        "https://arxiv-sanity-lite.com/inspect",
        headers=headers,
        params=params,
        cookies=cookies,
    )
    if "error, malformed pid" in response.text:
        raise PaperNotFound(
            f"Paper {paper_id} not in database yet (too old?). https://arxiv-sanity-lite.com/stats"
        )
    response = response.text
    start_index = response.find('[{"')
    stop_index = response.find('"}]', start_index)
    response = response[start_index : stop_index + 3]
    response = json.loads(response)
    return response


def filter_paper_tags(tags, num_max_tags=None, weight_threshold=None):
    if num_max_tags:
        tags = tags[:num_max_tags]  # tags are already sorted by decreasing weight value
    if weight_threshold:
        tags = [x for x in tags if x["weight"] >= weight_threshold]
    tags = [x["word"] for x in tags]
    return tags


def add_to_library(paper_id, tags):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://arxiv-sanity-lite.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    for tag in tags:
        tag_escaped = quote(tag)  # replace spaces with %20
        url = f"https://arxiv-sanity-lite.com/add/{paper_id}/{tag_escaped}"
        response = requests.get(
            url,
            headers=headers,
            cookies=cookies,
        )
        response = response.text
        assert "ok: " in response, response
        # TODO: fix ugly parsing
        response = response.replace("ok: ", "")
        response = response.replace(": {'", ": ['")
        response = response.replace("'}, '", "'], '")
        response = response.replace("}}", "]}")
        response = response.replace("'", '"')
        response = json.loads(response)
        assert paper_id in response[tag], response
        sleep(0.01)  # TODO: needed?


def delete_tag_from_library(tag):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://arxiv-sanity-lite.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    tag_escaped = quote(tag)  # replace spaces with %20
    url = f"https://arxiv-sanity-lite.com/del/{tag_escaped}"
    response = requests.get(url, headers=headers, cookies=cookies)
    response = response.text
    assert "ok: " in response, response
    assert f"'{tag}'" not in response, response


def get_all_user_tags():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://arxiv-sanity-lite.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    response = requests.get(
        "https://arxiv-sanity-lite.com/", headers=headers, cookies=cookies
    )
    response = response.text
    start_index = response.find("var tags =") + 11
    stop_index = response.find("];\nvar words", start_index) + 1
    response = response[start_index:stop_index]
    user_tags = json.loads(response)
    user_tags = [x["name"] for x in user_tags]
    user_tags.remove("all")
    return user_tags


def delete_all_tags_from_library():
    user_tags = get_all_user_tags()
    for tag in (pbar := tqdm(user_tags)):
        pbar.set_description(tag)
        delete_tag_from_library(tag)


def main():
    with open("my_library.json", "r") as f:  # pylint: disable=unspecified-encoding
        library_json = json.load(f)

    print(f"Found {len(library_json)} papers")

    for paper in (pbar := tqdm(library_json)):
        paper_id = paper["rawpid"]
        pbar.set_description(paper_id)
        try:
            tags = get_paper_tags(paper_id)
        except PaperNotFound as e:
            print("")  # get out of tqdm progress bar
            print(e)
            continue  # skip this paper
        tags = filter_paper_tags(tags, num_max_tags=10, weight_threshold=None)
        add_to_library(paper_id, tags)


if __name__ == "__main__":
    main()
    # delete_all_tags_from_library()  # purge library
