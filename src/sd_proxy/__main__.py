if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "sd_proxy", description="Proxy Schedule Direct images from xmltv files"
    )
    parser.add_argument("--username", required=True)
    parser.add_argument("--password-hash", required=True)
    parser.add_argument("--xmltv", required=True)
    parser.add_argument("--hostname", default="localhost")
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    from .main import run

    run(
        hostname=args.hostname,
        port=args.port,
        username=args.username,
        password_hash=args.password_hash,
        xmltv=args.xmltv,
    )
