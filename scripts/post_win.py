#!/usr/bin/env python3
"""Post a win to I'm Pretty Amazing (imprettyamazing.com)."""
import argparse
import json
import sys
import urllib.request
import http.cookiejar

API_BASE = "https://api.imprettyamazing.com"


def login(email, password):
    """Authenticate and return cookie jar with access_token."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    data = json.dumps({"email": email, "password": password}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = opener.open(req)
    body = json.loads(resp.read().decode())
    return opener, body.get("user", {})


def post_win(opener, content, win_type="PERSONAL", visibility="PUBLIC"):
    """Post a win. Returns the created win object."""
    from uuid import uuid4

    boundary = uuid4().hex
    parts = []
    for name, value in [("content", content), ("type", win_type), ("visibility", visibility)]:
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )
    body = "".join(parts) + f"--{boundary}--\r\n"

    req = urllib.request.Request(
        f"{API_BASE}/wins",
        data=body.encode(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    resp = opener.open(req)
    return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="Post a win to I'm Pretty Amazing")
    parser.add_argument("--email", required=True, help="Account email")
    parser.add_argument("--password", required=True, help="Account password")
    parser.add_argument("--content", required=True, help="Win description")
    parser.add_argument("--type", default="PERSONAL", choices=["PERSONAL", "PROFESSIONAL", "HEALTH", "SOCIAL", "CREATIVE", "LEARNING"], help="Win type")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "PRIVATE"], help="Visibility")
    args = parser.parse_args()

    opener, user = login(args.email, args.password)
    result = post_win(opener, args.content, args.type, args.visibility)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
