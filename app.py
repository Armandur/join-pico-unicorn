import pyjoin
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

hostname = "localhost"
serverport = 8585

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
            "time": 0
        }

        if inCall:
            data["time"] = time.time() - timer

        self.wfile.write(json.dumps(data).encode("utf-8"))


def callback(data):
    global timer
    global inCall

    data = json.loads(data["json"])["push"]
    if data["title"] == "I samtal":
        inCall = bool(int(data["text"]))
    
    print(inCall)

    if inCall:
        timer = time.time()

def joinThread():
    global api_key
    
    print(f"JoinThread starting")
    l = pyjoin.Listener(name="join-pico-unicorn",port=5050, api_key=api_key)
    l.add_callback(callback)
    l.run()

def webThread():
    print(f"WebThread starting")
    webServer = HTTPServer((hostname, serverport), Server)
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