# Schedule Direct XMLTV icon Proxy

A simple Python server to proxy token generation to download fanart/icons from
Schedule Direct, given an XMLTV file.

## Installation

```
pip install .
```

## Docker

```
docker build . -t sd_proxy
```

## Usage

### Running the proxy

Start the Python server with:

```
python -m sd_proxy --username=my_username --password-hash=sha1-hash-of-password --xmltv=path_to_xmltv.xml
```

or, if you use docker:

```
docker run --rm -it -p 8888:8888 -e USERNAME=my_username -e PASSWORD_HASH=sha1-hash-of-password -e XMLTV=/config/xmltv.xml -v ./config:/config sd_proxy
```

### Using the Proxy

Get the XMLTV, with poster/icon locations updated to the address of the proxy:

```
http://ip.address:port/xmltv
```

By default, `ip.address=localhost` and `port=8888`.

The icons fields in the returned `xmltv`-file have been changed to:

```
http://ip.address:port/image/imagehash.jpg
```

Using, e.g, `curl` or a browser, this URL redirects to
`https://json.scheduledirect.org/...../imagehash.jpg?token=authentication_token`.

The server automatically creates a new authentication token every six hour.
