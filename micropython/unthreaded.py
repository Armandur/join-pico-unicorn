# busyLight

from scroller import Scroller
import gol

import time
import picounicorn
import network
import urequests
import gc

networks = [ []]

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
    global networks
    
    wlan.active(True)
    for ssid, password in networks:
        wlan.connect(ssid, password)
        for i in range(5):
            if wlan.isconnected():
                scrollMessage(f"Conn! {ssid}", 0.3, 0.001)
                scrollMessage(str(wlan.ifconfig()[0]), 0.3, 0.001)
                print(wlan.ifconfig())
                print(f"Connected to {ssid}!")
                return
            
            error = False
            scrollMessage(f"Conn {ssid} {i+1}/5", 0.06, 0.001)
            time.sleep(1)
    error = True
    message = "No WiFi"


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

    serverURL = "http://unicorn.pettersson-vik.se"
    try:
        response = urequests.get(serverURL)
        error = False
    except Exception as e:
        error = True
        message = str(repr(e))
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
    
def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4: 
        return t, p, v
    if i == 5:
        return v, p, q

def showRainbow():
    time.sleep(1)
    while not picounicorn.is_pressed(picounicorn.BUTTON_B):
        t = time.ticks_ms() / 3600
        for x in range(w):
            for y in range(h):
                r, g, b = [int(c * 255) for c in hsv_to_rgb(t + ((x + y) / w / 4), 1.0, 1.0)]
                picounicorn.set_pixel(x, y, r, g, b)



t = time.time()
connect()

rainbow = False
gameOfLife = False

while True or KeyboardInterrupt:
    if rainbow:
        showRainbow()
        rainbow = False
    
    if gameOfLife:
        gol.GameOfLife()
        gameOfLife = False
    
    if error:
        scroll.clear()
        scrollMessage(message, 0, 0.02)
        time.sleep(0.1)
        continue
    
    if not wlan.isconnected():
        scroll.clear()
        scrollMessage("No WiFi", 0, 0.02)
        time.sleep(0.1)
        connect()    
    
    checkStatus()
    
    if error:
        scroll.clear()
        scrollMessage(message, 0, 0.02)
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
    
    if picounicorn.is_pressed(picounicorn.BUTTON_A):
        rainbow = True
        
    if picounicorn.is_pressed(picounicorn.BUTTON_X):
        gameOfLife = True
