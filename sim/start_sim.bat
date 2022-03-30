
start docker run -it --rm --add-host=host.docker.internal:host-gateway --name sim-mqtt2 -p 18830:18830 flightsoftware_mqtt 

@REM kill unity sim if running 
taskkill /IM "VRC SIM.exe"
start "" ".\build\VRC SIM.exe" 
start /B scripts\startgui.bat 

@ECHO OFF
PUSHD %~dp0
CALL C:\PX4\toolchain\scripts\setup-environment.bat x
POPD

REM restore working directory, counterpart is in home/.bash_profile
REM if we run the batch script by double click start in home folder
IF NOT EXIST %~nx0 (
	SET PREVIOUS_PWD=%CD%
)

REM start interactive bash terminal
REM login shell required because python modules need /usr/local/bin in the PATH!

CALL bash -l %~dp0/scripts/start_px4.sh

EXIT