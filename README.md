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

### Building Containers Locally

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/bellflight/VRC-2022
cd VRC-2022
```

Copy library files around:

```bash
python3 scripts/copy_libraries.py
```

Now, build the pymavlink package:

```bash
sudo python3 ./PX4/generate.py host --pymavlink
```

### Development Work

If you actually are doing development work, you want to set up a 
Python 3.9 virtual environment with all the dependencies installed.

If you need to install Python 3.9 on Linux, do the following:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3-pip python3.9 python3.9-venv
sudo -H python3.9 -m pip install pip wheel --upgrade
```

Create a Python 3.9 virtual environment:

```bash
python3.9 -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate # Windows
source .venv/bin/activate # Linux
```

You can install all the dependencies so you get autocomplete and type hinting:

```bash
python scripts/install_requirements.py
```

Finally, install recommended VS Code extensions.

If on a Jetson, you can now follow the instructions inside
[VMC/README.md](VMC/README.md) to run the `setup.sh`
script (add `--dev` for development).

Note, with `start.py` commands, make sure to add `--local` to the command.
This builds the Docker images locally rather than using prebuilt ones from GitHub CR.

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.

To build/run ARM Docker images, you may need to run
`docker run --rm --privileged multiarch/qemu-user-static --reset -p yes` first.
