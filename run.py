import os
import time
import datetime
import ast
import urllib
import threading


# Config
JENKINS_URL = "https://ci.freebsd.org/api/python"
UPDATE_INTERVAL = 10
QUICK_INTERVAL = 0.5
SLOW_INTERVAL = 1.5
SLEEP_INTERVAL = 2
JOBS = {
    "FreeBSD-head-aarch64-build": {"pin": "11"},
    "FreeBSD-head-amd64-build": {"pin": "10"},
    "FreeBSD-head-i386-build": {"pin": "5"},
    "FreeBSD-head-riscv64-build": {"pin": "8"}
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
            if self.status == "red":
                while self.is_updated == False:
                    led_on(self.pin)
                    time.sleep(SLEEP_INTERVAL)
            elif self.status in ["blue_anime", "red_anime"]:
                while self.is_updated == False:
                    led_on(self.pin)
                    time.sleep(QUICK_INTERVAL)
                    led_off(self.pin)
                    time.sleep(QUICK_INTERVAL)
            elif self.status in ["blue", "undefined"]:
                while self.is_updated == False:
                    led_off(self.pin)
                    time.sleep(SLEEP_INTERVAL)
            else:
                break
            self.log()
            self.is_updated = False

    def log(self):
        msg = "[" + str(datetime.datetime.now()) + "] "
        msg += self.name + " changed status to " + self.status + "."
        print msg


########### Functions ############
# Get build info from api and write it to threads
def update_build_info():
    data = ast.literal_eval(urllib.urlopen(JENKINS_URL).read())["jobs"]
    for key, value in JOBS.iteritems():
        for item in data:
            if item["name"] == key:
                if value["thread"].status != item["color"]:
                    value["thread"].status = item["color"]
                    value["thread"].is_updated = True
                break


# Init LEDs and corresponding threads
def init():
    for key, value in JOBS.iteritems():
        os.system("gpioctl -c " + value["pin"] + " OUT")
        value["thread"] = Led_controller(key, value["pin"], "undefined", False)
        value["thread"].start()
        print "[" + str(datetime.datetime.now()) + "] Thread " + key\
              + " created at PIN " + value["pin"] + "."     


# Led on
def led_on(pin):
    os.system("gpioctl " + pin + " 1")


# Led off
def led_off(pin):
    os.system("gpioctl " + pin + " 0")


# Clean up at exit
def clean_up():
    for key, value in JOBS.iteritems():
        value["thread"].status = ""
        value["thread"].is_updated = True
    time.sleep(SLEEP_INTERVAL + 1)


# Main
if __name__ == "__main__":
    init()
    try:
        while True:
            update_build_info()
            # print "[" + str(datetime.datetime.now()) + "] Build info has been updated."
            time.sleep(UPDATE_INTERVAL)
    finally:
        print "Cleaning up, please wait..."
        clean_up()
