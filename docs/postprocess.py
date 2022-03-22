import os
import urllib.parse
from pathlib import Path

import bs4
import requests
import tomli

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def process_local_tags(
    base_url: str, soup: bs4.BeautifulSoup, tag_type: str, attr: str, name: str
) -> None:
    # for each tag
    for tag in soup.find_all(tag_type):
        tag_attr = tag.get(attr)

        # skip empty items or without a remote url
        if tag_attr is None or not tag_attr.startswith("http"):
            continue

        # get the filename
        parsed = urllib.parse.urlparse(tag_attr)
        filename = os.path.basename(parsed.path)

        # if we don't have the file locally
        local_filename = os.path.join(THIS_DIR, "public", name, filename)
        if not os.path.exists(local_filename):
            # download the file
            print(f"Downloading {tag_attr}")
            response = requests.get(tag_attr)

            # write the file to disk
            with open(local_filename, "wb") as f:
                f.write(response.content)

        # update the html tag
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        tag[attr] = f"{base_url}/{name}/{filename}"


def local_tags(base_url: str, soup: bs4.BeautifulSoup) -> None:
    # download javascript
    process_local_tags(base_url, soup, "script", "src", "js")
    # download css
    process_local_tags(base_url, soup, "link", "href", "css")


def main() -> None:
    with open(os.path.join(THIS_DIR, "config.toml"), "rb") as fp:
        config_data = tomli.load(fp)

    for html_file in Path(THIS_DIR, "public").glob("**/*.html"):
        print(f"Processing file {html_file}")

        # open the html file and parse it
        with open(html_file, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        local_tags(config_data["baseURL"], soup)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(str(soup))


if __name__ == "__main__":
    main()
