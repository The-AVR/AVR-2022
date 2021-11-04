#!/bin/bash

set -e
set -x
shopt -s dotglob

# warning, v1.10.2 does not appear to build anymore
PX4_VERSION=v1.11.0

# record starting directory
startdir=$(pwd)

echo "--- Cleaning old data"
basedir="$(readlink -f "$(dirname "$0")")"
cd "$basedir"

sudo rm -rf build/
mkdir -p build
mkdir -p target
cd "$basedir/build"

echo "--- Cloning MAVLink"
mavlinkdir="$basedir/build/mavlink"
git clone https://github.com/mavlink/mavlink.git "$mavlinkdir" --recursive

echo "--- Creating Python venv"
deactivate || true
rm -rf .tmpvenv/
python3 -m venv .tmpvenv
source .tmpvenv/bin/activate
python3 -m pip install pip wheel --upgrade
python3 -m pip install -r "$mavlinkdir/pymavlink/requirements.txt"

echo "--- Cloning PX4 $PX4_VERSION"
cd "$basedir/build"
px4dir="$basedir/build/PX4-Autopilot"
git clone https://github.com/PX4/PX4-Autopilot --depth 5 "$px4dir" --branch $PX4_VERSION --recurse-submodules

echo "--- Applying PX4 patch"
# apply patch
cd "$px4dir"
git apply "$basedir/hil_gps_heading_$PX4_VERSION.patch"

echo "--- Injecting Bell MAVLink message"
cp "$basedir/bell.xml" "$px4dir/mavlink/include/mavlink/v2.0/message_definitions/bell.xml"
cd "$mavlinkdir"
python3 -m pymavlink.tools.mavgen --lang=C --wire-protocol=2.0 --output="$px4dir/mavlink/include/mavlink/v2.0/" "$px4dir/mavlink/include/mavlink/v2.0/message_definitions/bell.xml"
cd "$px4dir"

# changes need to be committeed to build
git add . 
git commit -m "Local commit to facilitate build"

echo "--- Copying MAVLink dialect"
# need to match the dialect used by the FCC and pymavlink, otherwise we'll have a bad time
python3 -m pip install -r "$basedir/../vmc/flight_control_module/requirements.txt"

mkdir -p "$basedir/target"
py=$(ls "$basedir/build/.tmpvenv/lib/")
cp "$basedir/build/.tmpvenv/lib/$py/site-packages/pymavlink/message_definitions/v1.0/common.xml" "$basedir/target/common.xml"
cp "$basedir/build/.tmpvenv/lib/$py/site-packages/pymavlink/message_definitions/v1.0/minimal.xml" "$basedir/target/minimal.xml"
cp "$basedir/bell.xml" "$basedir/target/bell.xml"

# generate Python code
echo "--- Generating Python MAVLink code"
cd "$mavlinkdir"
python3 -m pymavlink.tools.mavgen --lang=Python --wire-protocol=2.0 --output="$basedir/target/bell.py" "$basedir/target/bell.xml"
python3 -m pymavlink.tools.mavgen --lang=Python --wire-protocol=2.0 --output="$basedir/target/common.py" "$basedir/target/common.xml"
python3 -m pymavlink.tools.mavgen --lang=Python --wire-protocol=2.0 --output="$basedir/target/minimal.py" "$basedir/target/minimal.xml"

echo "--- Generating Wireshark MAVLink Lua plugins"
# https://mavlink.io/en/guide/wireshark.html
python3 -m pymavlink.tools.mavgen --lang=WLua --wire-protocol=2.0 --output="$basedir/target/bell.lua" "$basedir/target/bell.xml"
python3 -m pymavlink.tools.mavgen --lang=WLua --wire-protocol=2.0 --output="$basedir/target/common.lua" "$basedir/target/common.xml"
python3 -m pymavlink.tools.mavgen --lang=WLua --wire-protocol=2.0 --output="$basedir/target/minimal.lua" "$basedir/target/minimal.xml"

cd "$px4dir"
base_docker_cmd="docker run --rm -w \"$px4dir\" --volume=\"$px4dir\":\"$px4dir\":rw px4io/px4-dev-nuttx-focal:latest /bin/bash -c"

# echo "--- Building PX4 SITL"
# echo "$base_docker_cmd 'make px4_sitl_default'"
# eval "$base_docker_cmd 'make px4_sitl_default -j$(nproc)'"

# build Pixhawk firmware
echo "--- Building Pixhawk firmware"
echo "$base_docker_cmd 'make px4_fmu-v5_default'"
eval "$base_docker_cmd 'make px4_fmu-v5_default -j$(nproc)'"
cp "$px4dir/build/px4_fmu-v5_default/px4_fmu-v5_default.px4" "$basedir/target/px4_fmu-v5_default.$PX4_VERSION.px4"

# build NXP firmware
echo "--- Building NXP firmware"
echo "$base_docker_cmd 'make nxp_fmuk66-v3_default'"
eval "$base_docker_cmd 'make nxp_fmuk66-v3_default -j$(nproc)'"
cp "$px4dir/build/nxp_fmuk66-v3_default/nxp_fmuk66-v3_default.px4" "$basedir/target/nxp_fmuk66-v3_default.$PX4_VERSION.px4"

echo "--- Cleaning up"
cd "$basedir"
deactivate

echo "--- Copying outputs"
cp target/*.xml ../VMC/FlightSoftware/fcc/mavlink/
cp target/*.py ../VMC/FlightSoftware/fcc/mavlink/
cp target/*.lua ../VMC/FlightSoftware/fcc/mavlink/

cd "$startdir"
