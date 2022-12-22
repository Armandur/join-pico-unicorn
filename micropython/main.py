# Thanks to kevinmcaleer!
from scroller import Scroller
import time
import picounicorn
import _thread
import network
import urequests
import gc

SSID = "Network"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, "")

scroll = Scroller()
scroll.clear()
scroll.brightness = 1

message = ("Startup", 0)
inCall = None

states = {"color":"color", "showTime": "showTime"}
error = False


def setColor(color=(0, 0, 0)): # R G B
    r = color[0]
    g = color[1]
    b = color[2]

    scroll.clear()
    for col in range(16):
        for row in range(7):
            picounicorn.set_pixel(col, row, r, g, b)


def checkStatus():
    global inCall
    global message
    global error

    serverURL = "http://192.168.1.4:8585"
    while True:
        error = False
        response = urequests.get(serverURL)

        if response.status_code != 200:
            message = (f"Error {response.status_code}", 0)
            error = True

            response.close()
            gc.collect()
            time.sleep(1)
            continue

        data = response.json()
        inCall = data["inCall"]
        message = (data["time"], 0)

        response.close()
        gc.collect()
        time.sleep(1)


if __name__ == "__main__":
    initMessage = "Initalizing..."
    hue = 60

    for position in range(16, -len(initMessage*(5+1)), -1):
        scroll.show_message(initMessage, position, hue)
        time.sleep(1)

    statusThread = _thread.start_new_thread(checkStatus, ())
    currentState = states["color"]
    t = time.time()

    initMessage = "Thread started..."

    for position in range(16, -len(initMessage*(5+1)), -1):
        scroll.show_message(initMessage, position, hue)
        time.sleep(1)

    while True:
        if error:
            scroll.clear()
            for position in range(16, -len(currentMessage[0]*(5+1)), -1):
                scroll.show_message(currentMessage[0], position, currentMessage[1])
                time.sleep(1)

        if currentState == states["color"]:
            scroll.clear()
            setColor((0, 255, 0))

            if time.time() - t >= 5: #Show color for 5 seconds
                currentState = states["showTime"]
                continue

        if currentState == states["showTime"]:
            currentMessage = message
            for i in range(3): #Scroll message three times
                for position in range(16, -len(currentMessage[0]*(5+1)), -1):
                    scroll.show_message(currentMessage[0], position, currentMessage[1])
                    time.sleep(1)
            currentState = states["color"]

        time.sleep(0.5)
    scroll.clear()