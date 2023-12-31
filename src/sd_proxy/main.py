from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from datetime import datetime
from .xmltv import change_icon_path

from pathlib import PurePosixPath, Path
from urllib.parse import urlparse

import requests
import threading
import os
import time
import sys

def clear_cache(dir, max_age):
    def f():
        while True:
            now = datetime.utcnow()
            print("Clearing cache...", file=sys.stderr)
            for file in Path(dir).glob("*.jpg"):
                created_time = datetime.utcfromtimestamp(os.path.getmtime(file))
                age = (now - created_time).seconds / 60
                if age > max_age:
                    print(f"Purging {file.name} from cache ({int(age)} minutes old)...", file=sys.stderr)
                    file.unlink()

            # Sleep for at least max_age minutes.
            time.sleep(min(max_age * 60, 3600))

    return f


@dataclass
class Token:
    token: str
    issued: datetime


class SDRedirect(BaseHTTPRequestHandler):
    def send_file_from_cache_or_download(self, dir, image):
        dir = Path(dir)
        dir.mkdir(exist_ok=True)
        cache = dir / Path(image)
        if cache.is_file():
            print("Reading image from cache...", file=sys.stderr)
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.end_headers()
            self.wfile.write(cache.open("rb").read())
        else:
            print("Downloading image from schedulesdirect...", file=sys.stderr)
            token = self.server.get_auth_token()
            with requests.get(
                f"https://json.schedulesdirect.org/20141201/image/{image}?token={token}",
                stream=True,
            ) as remote:
                if remote.status_code == 200 and "schedulesdirect-api20141201a" in remote.url :
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.end_headers()
                    try:
                        with cache.open("wb") as local:
                            for chunk in remote.iter_content(chunk_size=8192):
                                local.write(chunk)
                                self.wfile.write(chunk)
                    except Exception:
                        if cache.is_file():
                            cache.unlink()
                else:
                    print("Downloading failed...", file=sys.stderr)
                    self.send_response(404)
                    self.end_headers()

    def do_HEAD(self):
        path = PurePosixPath(urlparse(self.path).path)
        if len(path.parts) < 1:
            self.send_response(404)
            self.end_headers()
        elif path.parts[1] == "xmltv":
            self.send_response(200)
            self.send_header("Content-Type", "text/xml")
            self.end_headers()
        elif path.parts[1] == "image":
            if len(path.parts) > 2:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
            else:
                self.send_response("404")
                self.end_headers()

    def do_GET(self):
        path = PurePosixPath(urlparse(self.path).path)
        if len(path.parts) < 1:
            self.send_response(404)
            self.end_headers()
        elif path.parts[1] == "xmltv":
            self.send_response(200)
            self.send_header("Content-Type", "text/xml")
            self.end_headers()
            print("Begin parsing xml....", file=sys.stderr)
            hostname, port = self.server.server_address
            tree = change_icon_path(self.server.xmltv, self.server.hostname, port)
            print("Parsing done...", file=sys.stderr)
            tree.write(self.wfile, xml_declaration=True, encoding="utf-8")
        elif path.parts[1] == "image":
            if len(path.parts) > 2:
                self.send_file_from_cache_or_download(self.server.cache, path.parts[-1])
            else:
                print("Malforemed image request...", file=sys.stderr)
                self.send_response(404)
                self.end_headers()


class SDProxy(ThreadingHTTPServer):
    def __init__(self, server_address, hostname, username, password_hash, xmltv, cache):
        super().__init__(server_address, SDRedirect)
        self.token = None
        self.hostname = hostname
        self.username = username
        self.password_hash = password_hash
        self.xmltv = xmltv
        self.cache = cache
        self.lock = threading.Lock()

    def invalidate_token(self):
        self.lock.acquire()
        self.token = None
        self.lock.release()

    def xmltv_last_changed(self):
        time = datetime.utcfromtimestamp(os.path.getmtime(self.xmltv))
        print(f"XMLTV was last generated {time}...", file=sys.stderr)
        return time

    def get_auth_token(self):
        self.lock.acquire()
        if (
            self.token is None
            or (datetime.utcnow() - self.token.issued).seconds > 6 * 3600
            or self.token.issued < self.xmltv_last_changed()
        ):
            print("Requesting authentication token...", file=sys.stderr)
            response = requests.post(
                "https://json.schedulesdirect.org/20141201/token",
                json={"username": self.username, "password": self.password_hash},
            ).json()
            print("Got authentication token...", file=sys.stderr)
            token = response["token"] if response["code"] == 0 else None
            if token is None:
                print("Failed to acquire authentication token...", file=sys.stderr)

            self.token = Token(token, datetime.utcnow())
        else:
            print("Token is still valid... (token `{}` issued at {})".format(self.token.token, self.token.issued), file=sys.stderr)

        self.lock.release()
        return self.token.token


def run(*, hostname, port, username, password_hash, xmltv, cache, max_cache_age):
    print(f"Starting server {hostname}...")
    if max_cache_age > 10:
        t = threading.Thread(target=clear_cache(cache, max_cache_age))
        t.start()

    SDProxy(("", port), hostname, username, password_hash, xmltv, cache).serve_forever()
