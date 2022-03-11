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
sudo apt update
sudo apt upgrade
git clone --recurse-submodules https://github.com/bellflight/VRC-2022
```

```bash
ssh-keygen -t ed25519 -C your_email@example.com
cat ~/.ssh/id_ed25519.pub
git clone --recurse-submodules git@github.com:bellflight/VRC-2022.git
```


update jetson to python 3.8, should create a setup script from this:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt-get update
sudo apt install python3.8

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo update-alternatives --config python3 
# Select 2

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
sudo update-alternatives --config python
# Select 2



sudo apt install python3-pip
sudo apt install python-pip
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip2 1
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
sudo update-alternatives --config pip

echo "if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi" >> ~/.bashrc

source ~/.bashrc 

#check version
#pip --version = pip 22.0.4 from /home/nathan/.local/lib/python3.8/site-packages/pip (python 3.8) 

sudo apt-get -y install python3.8-dev python3.8-venv
```


Create a Python 3.8+ virtual environment:

```bash
python -m venv .venv
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
./PX4/generate.sh
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

If you want to build PX4 on Windows, you need WSL with the
`python3-venv`, `python3-dev` and `build-essential` packages installed.

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.
