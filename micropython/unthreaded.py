# busyLight

from scroller import Scroller

import time
import picounicorn
import network
import urequests
import gc

ssid = "SSID"
password = "PASSWORD"

gc.enable()

w = picounicorn.get_width()
h = picounicorn.get_height()

wlan = network.WLAN(network.STA_IF)
scroll = Scroller()
scroll.clear()

inCall = False
message = ""
error = False
blinkRed = False


def scrollMessage(message, hue, speed):
    global scroll
    for position in range(16,-len(message*(5+1)),-1):
        scroll.show_message(message, position, hue)
        time.sleep(speed)


def connect():
    global scroll
    global wlan
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        scrollMessage("Connecting...", 0.06, 0.01)
        time.sleep(0.5)
    print("Connected!")
    scrollMessage("Connected!", 0.3, 0.01)
    print(wlan.ifconfig())
    

def fillColor(color):
    r, g, b = [255, 255, 255]
    if color == "green":
        r, g, b = [0, 255, 0]
    if color == "red":
        r, g, b = [255, 0, 0]
    for x in range(w):
        for y in range(h):
            picounicorn.set_pixel(x, y, r, g, b)


def checkStatus():
    global inCall
    global message
    global error

    serverURL = "http://192.168.1.4:8585"
    try:
        response = urequests.get(serverURL)
        error = False
    except Exception as e:
        error = True
        print(e)
        return

    if response.status_code != 200:
        message = (f"Error {response.status_code}", 0)
        error = True
        
        response.close()
        gc.collect()
        return

    data = response.json()
    inCall = data["inCall"]
    message = data["time"]
    response.close()
    gc.collect()
    

t = time.time()

connect()

while True or KeyboardInterrupt:
    checkStatus()
    if error:
        scroll.show_message("Error", 0, 61)
        time.sleep(0.1)
        continue
        
    if not error and inCall:
        blinkRed = not blinkRed
        if blinkRed:
            fillColor("red")
        else:
            scroll.clear()
        if time.time() - t > 5:
            scroll.clear()
            strmsg = f"I samtal: {message}"
            scrollMessage(strmsg, 0, 0.01)
            t = time.time()       
    else:
        fillColor("green")
        message = 0
    time.sleep(0.1)

