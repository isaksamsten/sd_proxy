from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def change_icon_path(filepath, hostname, port):
    xml = ET.parse(filepath)
    root = xml.getroot()
    for programme in root.findall("programme"):
        for icon in programme.findall("icon"):
            url = urlparse(icon.attrib["src"])
            path = PurePosixPath(url.path)
            image = path.parts[-1]
            icon.attrib["src"] = "http://{}:{}/image/{}".format(hostname, port, image)
    return xml
