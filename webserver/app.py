import pyjoin
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

hostname = "localhost"
webserverport = 8585
joinport = 5050

inCall = False
timer = None
api_key = ""


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        global inCall
        self._set_headers()
        data = {
            "inCall": inCall,
            "time": "0"
        }

        if inCall:
            callTime = round(time.time() - timer)
            if callTime < 60:
                data["time"] = f"{callTime}s"
            else:
                minutes, seconds = divmod(callTime, 60)
                data["time"] = f"{minutes}m{seconds}s"

        self.wfile.write(json.dumps(data).encode("utf-8"))


def callback(data):
    global timer
    global inCall

    data = json.loads(data["json"])["push"]
    if data["title"] == "I samtal":
        # inCall is pushed on tasker Phone Offhook and Phone Idle,
        # but also value inCall is pushed every 1500ms in order to not stop at true or false wrongly
        # Trigger on switch of value, not value updating
        if bool(int(data["text"])) != inCall:
            inCall = not inCall
            print(f"State updated -  inCall: {inCall}")
            
            if inCall:
                timer = time.time()


def joinThread():
    global api_key
    
    print(f"JoinThread starting")
    l = pyjoin.Listener(name="join-pico-unicorn",port=joinport, api_key=api_key)
    l.add_callback(callback)
    l.run()


def webThread():
    print(f"WebThread starting")
    webServer = HTTPServer((hostname, webserverport), Server)
    webServer.serve_forever()


if __name__ == "__main__":
    with open("api", "r") as file:
        api_key = file.readline()
    
    join = threading.Thread(target=joinThread)
    web = threading.Thread(target=webThread)

    join.start()
    web.start()
    
    #Keep running until kill
    join.join()
    web.join()