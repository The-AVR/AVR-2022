import os
import urllib.parse
from pathlib import Path

import bs4
import requests

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def local_script_tags(soup: bs4.BeautifulSoup) -> None:
    # for each script tag
    for script_tag in soup.find_all("script"):
        script_src = script_tag.get("src")
        # skip items with local references
        if not script_src.startswith("http"):
            continue

        print(f"Updating {script_tag}")

        # get the script filename
        parsed = urllib.parse.urlparse(script_src)
        filename = os.path.basename(parsed.path)

        # if we don't have the script locally
        local_filename = os.path.join(THIS_DIR, "public", "js", filename)
        if not os.path.exists(local_filename):
            # download the script
            print(f"Downloading {script_src}")
            response = requests.get(script_src)

            # write the script to disk
            with open(local_filename, "wb") as f:
                f.write(response.content)

        # update the script tag
        script_tag["src"] = "/js/" + filename


def absolute_image_paths(soup: bs4.BeautifulSoup, filepath: Path) -> None:
    # for each image tag
    for img_tag in soup.find_all("img"):
        img_src = img_tag.get("src")
        # skip items without local references
        if img_src.startswith("http"):
            continue

        print(f"Updating {img_tag}")

        # update the img tag
        # fmt:off
        img_tag["src"] = f"/{filepath.parent.relative_to(os.path.join(THIS_DIR, 'public'))}/{img_src}".replace("\\", "/")
        # fmt:on


def main() -> None:
    for html_file in Path(THIS_DIR, "public").glob("**/*.html"):
        print(f"Updating {html_file}")

        # open the html file and parse it
        with open(html_file, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        local_script_tags(soup)
        absolute_image_paths(soup, html_file)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(str(soup))


if __name__ == "__main__":
    main()
