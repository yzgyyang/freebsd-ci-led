import os
import time
import ast
import urllib
import threading


# Config
JENKINS_URL = "https://ci.freebsd.org/api/python"
UPDATE_INTERVAL = 10
JOBS = {
    "FreeBSD-head-aarch64-build": {"pin": "11"}
}


############ Classes #############
class Led_controller(threading.Thread):
    def __init__(self, name, pin, status, is_updated):
        threading.Thread.__init__(self)
        self.name = name
        self.pin = pin
        self.status = status
        self.is_updated = is_updated

    def run(self):
        while True:
            if self.status == "blue_anime":
                while self.is_updated == False:
                    led_on(self.pin)
                    time.sleep(0.5)
                    led_off(self.pin)
                    time.sleep(0.5)
                self.is_updated = False
            elif self.status == "undefined":
                while self.is_updated == False:
                    led_off(self.pin)
                    time.sleep(2)
                self.is_updated = False


########### Functions ############
# Get build info from api and write it to threads
def update_build_info():
    data = ast.literal_eval(urllib.urlopen(JENKINS_URL).read())["jobs"]
    for key, value in JOBS.iteritems():
        for item in data:
            if item["name"] == key:
                value["thread"].status = item["color"]
                value["thread"].is_updated = True
                break


# Init LEDs and corresponding threads
def init():
    for key, value in JOBS.iteritems():
        os.system("gpioctl -c " + value["pin"] + " OUT")
        value["thread"] = Led_controller(key, value["pin"], "undefined", False)
        value["thread"].start()


# Led on
def led_on(pin):
    os.system("gpioctl " + pin + " 1")


# Led off
def led_off(pin):
    os.system("gpioctl " + pin + " 0")


# Main
if __name__ == "__main__":
    init()
    while True:
        update_build_info()
        time.sleep(UPDATE_INTERVAL)