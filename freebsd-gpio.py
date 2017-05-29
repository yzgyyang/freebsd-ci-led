import os

# Gpio value is one of [0, 1]
def set_gpio_value(pin, value):
    os.system("gpioctl " + pin + " " + str(value))


# Direction is one of ["IN", "OUT"]
def set_gpio_direction(pin, direction):
    os.system("gpioctl -c " + pin + " " + direction)

