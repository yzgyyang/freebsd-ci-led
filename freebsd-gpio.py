import os


def led_on(pin):
    os.system("gpioctl " + pin + " 1")


def led_off(pin):
    os.system("gpioctl " + pin + " 0")


def pin_out(pin):
    os.system("gpioctl -c " + pin + " OUT")


