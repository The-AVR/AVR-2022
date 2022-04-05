[circuitpython setup on jetson nano](https://learn.adafruit.com/circuitpython-libraries-on-linux-and-the-nvidia-jetson-nano/initial-setup)
Only the section that really applies: Enable UART, I2C and SPI 

'''yaml
Need to run in privileged mode:
  thermal:
    depends_on:
      - mqtt
    privileged: true
    image: lance/vrc_thermal_module:latest
    restart: on-failure 
'''