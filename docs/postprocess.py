import os
import urllib.parse
from pathlib import Path

import bs4
import requests

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def process_local_tags(
    soup: bs4.BeautifulSoup, tag_type: str, attr: str, name: str
) -> None:
    # for each tag
    for tag in soup.find_all(tag_type):
        tag_attr = tag.get(attr)

        # skip empty items or without a remote url
        if tag_attr is None or not tag_attr.startswith("http"):
            continue

        print(f"Updating remote resource {tag}")

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
        tag[attr] = f"/{name}/{filename}"


def local_tags(soup: bs4.BeautifulSoup) -> None:
    # download javascript
    process_local_tags(soup, "script", "src", "js")
    # download css
    process_local_tags(soup, "link", "href", "css")


def process_absolute_paths(
    soup: bs4.BeautifulSoup, filepath: Path, tag_type: str, attr: str
) -> None:
    # this ended up not working, because of the _print pages, and flattening
    # the tree structure.

    # for each tag
    for tag in soup.find_all(tag_type):
        tag_attr = tag.get(attr)

        # skip empty items, with a remote url, or starts with #
        if tag_attr is None or tag_attr.startswith("http") or tag_attr.startswith("#"):
            continue

        print(f"Updating tag path {tag}")

        # update the img tag
        # fmt:off
        tag[attr] = f"/{filepath.parent.relative_to(os.path.join(THIS_DIR, 'public'))}/{tag_attr}".replace("\\", "/")
        # fmt:on


def main() -> None:
    for html_file in Path(THIS_DIR, "public").glob("**/*.html"):
        print(f"Checking file {html_file}")

        # open the html file and parse it
        with open(html_file, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        local_tags(soup)
        # absolute_paths(soup, html_file)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(str(soup))


if __name__ == "__main__":
    main()
