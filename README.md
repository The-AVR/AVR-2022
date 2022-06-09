# VRC-2022

## Project Management

For Bell employees and partners, work items are tracked on [Trello](https://trello.com/bellvrc).

## Structure

- `.github`: GitHub Actions files
- `.vscode`: VS Code settings
- `3DPrints`: 3D printing files and source CAD files
- `docs`: Documentation site
- `GUI`: All-in-one GUI
- `Libraries`: Shared libraries that get copied around
- `PCC`: PCC firmware
- `PX4`: PX4 and MAVLink files
- `RVR`: RVR files
- `scripts`: Development scripts
- `VMC`: VMC flight software

## Developer Setup

To do development work, you'll want to have Docker setup, along with Python 3.9
with the `venv` module.

If you need to install Python 3.9 on Linux, do the following:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3-pip python3.9 python3.9-venv
sudo -H python3.9 -m pip install pip wheel --upgrade
```

If you want to build/run Docker images not on a Jetson, run

```bash
docker run --rm --privileged docker.io/multiarch/qemu-user-static --reset -p yes
```

once first.

Refer to individual module README files for specific instructions.

### Repo Setup

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/bellflight/VRC-2022
cd VRC-2022
```

If you already have the repo cloned, run

```bash
git submodule update --init --recursive
```

to initialize and/or update the submodules.

### VS Code Setup

We recommend setting `git.pullTags` to `false` in VS Code workspace settings
to prevent tag errors when doing `git pull`, along with installing the
recommended extensions.

### Python Setup

Create a Python 3.9 virtual environment:

```bash
py -3.9 -m venv .venv # Windows
python3.9 -m venv .venv # Linux
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate # Windows
source .venv/bin/activate # Linux
```

Finally, you can install all the dependencies so you get autocomplete and type hinting:

```bash
python scripts/install_requirements.py
```

## Running Containers on a Jetson

If on a Jetson, clone the repository and check out the git branch you want.
You can now follow the instructions inside
[VMC/README.md](VMC/README.md) to run the `setup.py`
script and add `--dev` for development.

Note, with `start.py` commands, make sure to add `--local` to the command.
This builds the Docker images locally rather than using prebuilt ones from GitHub CR.
