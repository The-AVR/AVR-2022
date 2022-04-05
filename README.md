# VRC-2022

## Project Management

For Bell employees and partners, work items are tracked on [Trello](https://trello.com/bellvrc).

## Structure

- `.github`: GitHub Actions files
- `.vscode`: VS Code settings
- `3DPrints`: 3D printing files and source CAD files
- `docs`: Documentation site
- `Libraries`: Shared libraries that get copied around
- `PCC`: PCC files
  - `ControlSoftware`: PCC firmware
  - `GUI`: PCC test GUI
- `PX4`: PX4 and MAVLink files
- `RVR`: RVR files
- `scripts`: Development scripts
- `VMC`: VMC files
  - `FlightSoftware`: VMC flight software
  - `GUI`: VMC control GUI

## Developer Setup

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/bellflight/VRC-2022
```

update jetson to python 3.8, should create a setup script from this:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt-get update
sudo apt install python3.8 python3-pip python3.8-venv
sudo python3.8 -m pip install pip wheel --upgrade
```

Create a Python 3.8+ virtual environment:

```bash
python3.8 -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate # Windows
source .venv/bin/activate # Linux
```

Copy library files around:

```bash
python scripts/copy_libraries.py
```

Now, build the pymavlink package:

```bash
python ./PX4/generate.py host --pymavlink
```

If you actually are doing development work, you can install all the dependencies
so you get autocomplete and type hinting:

```bash
python scripts/dev_setup.py
```

If on a Jetson, you can now follow the instructions inside
[VMC/FlightSoftware/README.md](VMC/FlightSoftware/README.md) to run the `setup.sh`
script (add `--dev` for development).

Note, with `docker-compose` commands, make sure to add `-f docker-compose-dev.yml`
before the action such as `sudo docker-compose -f docker-compose-dev.yml up -d`.
This builds the Docker images locally rather than using prebuilt ones from GitHub CR.

Finally, install recommended VS Code extensions.

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.

To build/run ARM Docker images, you may need to run
`docker run --rm --privileged multiarch/qemu-user-static --reset -p yes` first.