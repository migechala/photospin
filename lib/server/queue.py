from cgi import parse_header, parse_multipart
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import sqlite3

hostName = "192.168.1.167"
serverPort = 1024

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200, "Ok!")
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()


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

        self._set_headers()
        connection = sqlite3.connect("server_list.db") 
        cursor = connection.cursor()
        
        print(postvars)

        if b'join' in postvars:
            code = postvars[b'code'][0].decode()
            print("Redirecting user to server code {}...".format(code))
            server_ip = cursor.execute("SELECT ip FROM server WHERE code = \"{}\"".format(code)).fetchone()[0]
            print("Redirected user!")

        elif b'create' in postvars:
            print("Creating server...")
            server_ip = cursor.execute("SELECT ip FROM server WHERE code IS NULL").fetchone()[0]
            cursor.execute("UPDATE server SET code = \"{}\" WHERE ip = \"{}\""
            .format(postvars[b'create'][0].decode(), server_ip))
            connection.commit()
            print("Created server!")

        elif b'destroy' in postvars:
            code = postvars[b'destroy'][0].decode() 
            print("Destorying server...")
            cursor.execute("UPDATE server SET code = NULL WHERE code = \"{}\"".format(code))
            connection.commit()
            print("Destroyed server!")

        else:
            print("No such form in {}".format(postvars))

        if "server_ip" in locals() and server_ip != "":
            print("Sending back response: {}".format(server_ip))
            self.wfile.write(bytes(server_ip, "utf-8"))
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