from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from datetime import datetime
from .xmltv import change_icon_path

from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests


@dataclass
class Token:
    token: str
    issued: datetime


class SDRedirect(BaseHTTPRequestHandler):
    def do_GET_XMLTV(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/xml")
        self.end_headers()
        print("Begin parsing xml....")
        hostname, port = self.server.server_address
        tree = change_icon_path(self.server.xmltv, hostname, port)
        print("Parsing done...")
        tree.write(self.wfile, xml_declaration=True, encoding="utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        path = PurePosixPath(url.path)
        if len(path.parts) < 1:
            self.send_response(404)
            self.end_headers()
        elif path.parts[1] == "xmltv":
            self.do_GET_XMLTV()
        elif path.parts[1] == "image":
            if len(path.parts) > 2:
                token = self.server.get_auth_token()
                print(f"Redirecting {path.parts[-1]} to schedule direct...")
                self.send_response(301)
                self.send_header(
                    "Location",
                    "https://json.schedulesdirect.org/20141201/image/{}?token={}".format(
                        path.parts[-1], token
                    ),
                )
                self.end_headers()
            else:
                print("Malforemed image request...")
                self.send_response("404")
                self.end_headers()


class SDProxy(ThreadingHTTPServer):
    def __init__(self, server_address, username, password_hash, xmltv):
        super().__init__(server_address, SDRedirect)
        self.token = None
        self.username = username
        self.password_hash = password_hash
        self.xmltv = xmltv

    def get_auth_token(self):
        if (
            self.token is None
            or (datetime.now() - self.token.issued).seconds > 6 * 3600
        ):
            print("Requesting authentication token...")
            response = requests.post(
                "https://json.schedulesdirect.org/20141201/token",
                json={"username": self.username, "password": self.password_hash},
            ).json()
            print("Got authentication token...")
            token = response["token"] if response["code"] == 0 else None
            if token is None:
                print("Failed to acquire authentication token...")

            self.token = Token(token, datetime.now())

        return self.token.token


def run(*, hostname, port, username, password_hash, xmltv):
    print("Starting server {}...".format(hostname))
    SDProxy((hostname, port), username, password_hash, xmltv).serve_forever()


if __name__ == "__main__":
    run()
