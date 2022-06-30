import base64
from cgi import parse_header, parse_multipart
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

    def _parseFile(self, path: str):
        p = path[path.rfind("/")].removesuffix(".png")
        answer = p[:path.rfind("_")]
        id = p[path.rfind("_"):]
        return {"id": id, "answer": answer}

    def _getFiles(self) -> dict:
        file = {}
        path_of_the_directory = 'images'
        ext = ('.jpg', '.png', '.jpeg', '.HELM')
        for files in os.listdir(path_of_the_directory):
            if files.endswith(ext):
                p = self._parseFile(files)
                f = open(path_of_the_directory + '/' + files, "rb")
                file[p["id"]] = [p["answer"], base64.urlsafe_b64encode(f.read())]
                f.close()
        return file
    
    base64.urlsafe_b64encode
        

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
        image_b64 = unquote(postvars[b"image"][0].decode("utf-8"))
        if image_b64.find("%") != -1:
            print("Error! {}".format(image_b64[image_b64.find("%") - 2 : image_b64.find("%") + 2]))

        file_name = postvars[b"name"][0].decode("utf-8")
        id = postvars[b"id"][0].decode("utf-8")
 
#        print("file name {} from user with id {}".format(file_name, id))
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
            random_key: str = thisRound.getRandomImage()
            random_answer: str = files[random_key][0] # 0 is the name of image
            random_image: bytes = files[random_key][1] # 1 is the base64 representation of the image

            data: bytes = bytes(random_key, "utf-8") + bytes(" ", "utf-8") + bytes(random_answer, "utf-8") + bytes(" ", "utf-8") + random_image
            

            self.wfile.write(data)            
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