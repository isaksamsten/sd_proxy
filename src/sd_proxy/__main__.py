if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "sd_proxy", description="Proxy Schedule Direct images from xmltv files"
    )
    parser.add_argument("--username", required=True)
    parser.add_argument("--password-hash", required=True)
    parser.add_argument("--xmltv", required=True, help="XMLTV-file to serve")
    parser.add_argument(
        "--hostname", default="localhost", help="Hostname in image urls"
    )
    parser.add_argument("--cache", default="cache", help="Location of cached images")
    parser.add_argument(
        "--max-cache-age",
        default=4320,
        type=int,
        help="Maximum age of cached image (seconds, default 72hours)",
    )
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    from .main import run

    run(
        hostname=args.hostname,
        port=args.port,
        username=args.username,
        password_hash=args.password_hash,
        xmltv=args.xmltv,
        cache=args.cache,
        max_cache_age=args.max_cache_age,
    )
