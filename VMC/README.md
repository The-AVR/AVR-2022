# VRC-2022

## Setup

If you have problems with the setup script, ensure that you are able to
connect to the following domains. Some schools or networks may block these:

```bash
# used for linux system packages
https://repo.download.nvidia.com
http://ports.ubuntu.com
http://ppa.launchpad.net
# used for python packages
https://pypi.org
https://files.pythonhosted.org
# used for downloading code
https://github.com
https://github-releases.githubusercontent.com
https://developer.nvidia.com
# used for Docker containers
https://nvcr.io
https://index.docker.io
https://ghcr.io
```

Run the following commands:

```bash
sudo apt update
sudo apt install git -y
git clone https://github.com/bellflight/VRC-2022 ~/VRC-2022
cd ~/VRC-2022/VMC/
chmod +x setup.sh
./setup.sh
```

Please note, this setup script WILL take a while the first time
(depending on your download speed),
and you may need to re-enter your `sudo` password a few times.

## Usage

To start the VRC software, just run:

```bash
# Start the Docker Compose stack
sudo docker-compose up -d
```

To stop the VRC software, run:

```bash
# Stop the Docker Compose stack
sudo docker-compose down
```

If you ever need to update the VRC software, run:

```bash
# Update the git repo
git pull
# Re-run the setup script
./setup.sh
```
