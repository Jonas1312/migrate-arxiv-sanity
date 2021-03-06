
# migrate arxiv-sanity library

Migrate [arxiv-sanity.com](https://arxiv-sanity.com) library to new [arxiv-sanity-lite.com](https://arxiv-sanity-lite.com)

## Run Locally

1) Get your session cookie from [https://arxiv-sanity.com](https://arxiv-sanity.com) (when the website is running... (╯‵□′)╯︵┻━┻ )
2) Add your session cookie to `backup_old_arxiv_sanity.py`:

    ```python
    cookies = {
      "session": "HERE",
    }
    ```
3) Download `my_library.json` from old [arxiv-sanity.com](https://arxiv-sanity.com) using `backup_old_arxiv_sanity.py`

    ```json
    [
        {
            "abstract":"...",
            "authors":[
              "Alice",
              "Bob",
            ],
            "category":"cs.CV",
            "comment":"CVPR 2020...",
            "img":"/static/thumbs/...pdf.jpg",
            "in_library":1,
            "link":"http://arxiv.org/abs/...",
            "num_discussion":0,
            "originally_published_time":"6/18/2045",
            "pid":"2006.123456v2",
            "published_time":"2/10/2045",
            "rawpid":"2006.123456",
            "tags":[
              "cs.CV",
              "cs.LG"
            ],
            "title":"..."
        },
        {
            "abstract":"...",
            "rawpid":"2006.789456",
            ...
        }
    ]
    ```

4) Get your session cookie from [arxiv-sanity-lite.com](https://arxiv-sanity-lite.com)
5) Add your session cookie to `upload_to_arxiv_lite.py`:

    ```python
    cookies = {
      "session": "HERE",
    }
    ```

6) Run `upload_to_arxiv_lite.py`

## Acknowledgements

- [Convert curl command to code](https://curlconverter.com/#python)
