import os
import urllib.parse
from pathlib import Path

import bs4
import requests

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def download_tags(soup: bs4.BeautifulSoup, tag_type: str, attr: str, name: str) -> None:
    # for each link tag
    for tag in soup.find_all(tag_type):
        tag_attr = tag.get(attr)
        
        # skip items with local references, or not a remote url
        if tag_attr is None or not tag_attr.startswith("http"):
            continue

        print(f"Updating remote resource {tag}")

        # get the script filename
        parsed = urllib.parse.urlparse(tag_attr)
        filename = os.path.basename(parsed.path)

        # if we don't have the script locally
        local_filename = os.path.join(THIS_DIR, "public", name, filename)
        if not os.path.exists(local_filename):
            # download the script
            print(f"Downloading {tag_attr}")
            response = requests.get(tag_attr)

            # write the script to disk
            with open(local_filename, "wb") as f:
                f.write(response.content)

        # update the script tag
        tag[attr] = f"/{name}/{filename}"


def local_tags(soup: bs4.BeautifulSoup) -> None:
    download_tags(soup, "script", "src", "js")
    download_tags(soup, "link", "href", "css")


def absolute_image_paths(soup: bs4.BeautifulSoup, filepath: Path) -> None:
    # for each image tag
    for img_tag in soup.find_all("img"):
        img_src = img_tag.get("src")
        # skip items without local references
        if img_src.startswith("http"):
            continue

        print(f"Updating image path {img_tag}")

        # update the img tag
        # fmt:off
        img_tag["src"] = f"/{filepath.parent.relative_to(os.path.join(THIS_DIR, 'public'))}/{img_src}".replace("\\", "/")
        # fmt:on


def main() -> None:
    for html_file in Path(THIS_DIR, "public").glob("**/*.html"):
        print(f"Checking file {html_file}")

        # open the html file and parse it
        with open(html_file, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        local_tags(soup)
        absolute_image_paths(soup, html_file)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(str(soup))


if __name__ == "__main__":
    main()
