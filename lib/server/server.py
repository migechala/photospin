import base64
from cgi import parse_header, parse_multipart
import socketserver
import game as game
import time
from urllib.parse import parse_qs, unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

hostName = "192.168.1.167"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):

    player_count = 0
    player_scores = dict   
    current_round = 0
    rounds = 6

    def __init__(self, request: bytes, client_address: tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)
        
        
    def _waitUntil(func, timeout, period=0.25):
        mustend = time.time() + timeout
        while time.time() < mustend:
            if (func): return True
            time.sleep(period)
            return False
    
    def _getPlayerCount(self):
        return self.player_count

    def _getFileCount(self):
        dir_path = r'images'
        count = 0
        for path in os.listdir(dir_path):
            if path.isfile(path.join(dir_path, path)):
                count += 1
        return count

    def _parseFile(path: str):
        p = path[path.rfind("/")].removesuffix(".png")
        answer = p[:path.rfind("_")]
        id = p[path.rfind("_"):]
        return {"id": id, "answer": answer}

    def _getFiles(self):
        file = {}
        path_of_the_directory = 'images'
        ext = ('.png')
        for files in os.listdir(path_of_the_directory):
            if files.endswith(ext):
                p = self._parseFile(files)
                f = open(files, "r")
                file[p["id"]] = [p["answer"], f.read()]
                f.close()
            else:
                continue
        return file
        

    def _set_headers(self):
        self.send_response(200, "Ok!")
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.player_count += 1
        print(self.player_count)

    def do_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=True)
        else:
            postvars = {}
        print(postvars.keys()) 
        image_b64 = unquote(postvars[b"image"][0].decode("utf-8"))

        if image_b64.find("%") != -1:
            print("Error! {}".format(image_b64[image_b64.find("%") - 2 : image_b64.find("%") + 2]))

        file_name = postvars[b"name"][0].decode("utf-8")
        id = postvars[b"id"][0].decode("utf-8")
 
        print("file name {} from user with id {}".format(file_name, id))
        type_ext = file_name[file_name.find("."):]

        open("images/{}_{}{}".format(file_name[:file_name.find(".")],
            id,
            type_ext),
            "wb").write(base64.urlsafe_b64decode(image_b64))
        self._set_headers()
        
        self._waitUntil(self._getFiles == self._getPlayerCount())
        self.current_round += 1
        
        files = self._getFiles()
        thisRound = game.Round(files)

        for self.round in range(self.rounds):
            random_key = thisRound.getRandomImage()
            random_answer = files[random_key][0] # 0 is the name of image
            random_image = files[random_key][1] # 1 is the base64 representation of the image

            self.wfile.write(random_key)
            self.wfile.write(random_answer)
            self.wfile.write(random_image)
            break

        return
        
    def do_PUT(self):
        self.do_POST()

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")