# This is a Dockerfile. This descibres how to programmatically set up
# what's known as a "container". A "container" is sort of a virtual computer
# inside of another computer. Unlike what some of you may be familiar with,
# and "virtual machines", containers are extremely fast to start up,
# and make it easy to share an application packaged with all the components
# needed for it to run. For AVR, we are going to set up containers for
# each module to make it easier to run them all seperately and simultaneously.

# This begins the process of building our container off the standard Python
# image. The version tag (after the colon), is the Python version (3.9)
# along with the version of Debian (buster) we are building off.
# https://hub.docker.com/_/python
FROM docker.io/library/python:3.9-buster

# Change the working directory to /app
WORKDIR /app

# Copy the file requirements.txt from the host into the container
COPY requirements.txt requirements.txt

# First, upgrade pip (Python's package manager) and install a package
# called "wheel". A "wheel" is a Python package format that is basically
# a ZIP file of Python code that is already pre-built. After that,
# install the requirements in the requirements.txt file for our code.
RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt

# Now, copy everything else in this folder into the container.
COPY . .

# Finally, start the container running our code.
CMD ["python", "armed_indicator_threaded.py"]
#CMD ["python", "armed_indicator_callback.py"]