import os
import json


def link_item(src: str, dst: str) -> None:
    # symlinks require Admin on Windows, stick with links

    if os.path.isfile(src):
        # if the destination is a directory, add the filename to the end
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))

        # make sure the parent directories exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        # if the file already exists, remove it
        if os.path.isfile(dst):
            os.remove(dst)

        print(f"Linking {src} -> {dst}")
        os.link(src, dst)

    elif os.path.isdir(src):
        # can't link directories, need to do it file by file
        for root, _, filenames in os.walk(src, topdown=False):
            for filename in filenames:
                # build full path to file
                item_src = os.path.join(root, filename)
                # find path relative to source
                rel_item_src = os.path.relpath(item_src, src)
                # build full dest path
                item_dst = os.path.join(dst, rel_item_src)

                # link the file
                link_item(item_src, item_dst)

    else:
        raise ValueError


def main() -> None:
    # top-level directory
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    # libraries directory
    libraries_dir = os.path.join(base_dir, "Libraries")
    libraries_manifest = os.path.join(libraries_dir, "manifest.json")

    # read manifest data
    with open(libraries_manifest, "r") as fp:
        manifest_data = json.load(fp)

    # for each entry
    for entry in manifest_data:
        # build path to source
        src = os.path.abspath(os.path.join(libraries_dir, entry["src"]))
        for dst in entry["dsts"]:
            # build path to dest
            link_item(src, os.path.abspath(os.path.join(base_dir, dst)))


if __name__ == "__main__":
    main()
