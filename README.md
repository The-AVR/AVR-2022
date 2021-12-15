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

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
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
