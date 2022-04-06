import os
from typing import List

import commentjson
import jinja2

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def titleify(text: str) -> str:
    return "".join(i.title() for i in text.replace("_", "/").split("/"))


def process_klass(klass: dict) -> List[dict]:
    """
    Take an class and generate a list a new classes that also need to be generated.
    Acts recursively.
    """
    # list to hold the new generated classes
    new_klasses = []

    for item in klass["payload"]:
        if not isinstance(item["type"], str):
            # if the type of a key is not a string, create a new helper class for it
            # and replace it with a reference to that class
            new_class_name = klass["name"] + titleify(item["key"])
            # copy over the documentation as well if present
            new_klasses.append(
                {
                    "name": new_class_name,
                    "payload": item["type"],
                    "docs": item.get("docs", ""),
                }
            )
            item["type"] = new_class_name

    # list to hold the newly proccessed new classes
    new_new_klasses = []
    for new_klass in new_klasses:
        new_new_klasses.extend(process_klass(new_klass))

    # return the new klasses and their children
    return new_klasses + new_new_klasses


def main() -> None:
    # setup jinja
    template_loader = jinja2.FileSystemLoader(searchpath=THIS_DIR)
    template_env = jinja2.Environment(loader=template_loader)

    # load data
    print("Loading data")
    with open(os.path.join(THIS_DIR, "data.jsonc"), "r") as fp:
        topics = commentjson.load(fp)

    # generate addtional class configuration
    # we need to do some pre-processing to make templating easier
    print("Preprocessing data")
    klasses = []
    for topic in topics:
        if "name" not in topic:
            # generate a class name
            topic["name"] = titleify(topic["path"])

        # add generated klasses to seperate list
        klasses.extend(process_klass(topic))

    # generate python code
    template = template_env.get_template("main.j2")

    print("Rendering template")
    with open(os.path.join(THIS_DIR, "..", "mqtt_library.py"), "w") as fp:
        fp.write(template.render(klasses=klasses, topics=topics))


if __name__ == "__main__":
    main()
