# VRC-2022

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

Create a Python 3.8+ virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate # Windows
source .venv/bin/activate # Linux
```

Install all the dependencies:

```bash
python scripts/dev_setup.py
```

Copy library files around:

```bash
python scripts/copy_libraries.py
```

Finally, install recommended VS Code extensions.

If you want to build PX4 on Windows, you need WSL with the
`python3-venv`, `python3-dev` and `build-essential` packages installed.

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.
