import os
import urllib.parse
from pathlib import Path

import bs4
import requests

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def update_script_tag(script_tag: bs4.element.Tag, filename: str) -> None:
    print(f"Updating {script_tag}")
    script_tag["src"] = "/js/" + filename


def main() -> None:
    for html_file in Path(THIS_DIR, "public").glob("**/*.html"):
        print(f"Updating {html_file}")

        # open the html file and parse it
        with open(html_file, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        # for each script tag
        for script_tag in soup.find_all("script"):
            script_src = script_tag.get("src")
            # skip items with local references
            if not script_src.startswith("http"):
                continue

            # get the script filename
            parsed = urllib.parse.urlparse(script_src)
            filename = os.path.basename(parsed.path)

            # if we don't have the script locally
            if not os.path.exists(os.path.join(THIS_DIR, "public", "js", filename)):
                # download the script
                print(f"Downloading {script_src}")
                response = requests.get(script_src)

                # write the script to disk
                with open(os.path.join(THIS_DIR, "public", "js", filename), "wb") as f:
                    f.write(response.content)

            # update the script tag
            update_script_tag(script_tag, filename)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(str(soup))


if __name__ == "__main__":
    main()
