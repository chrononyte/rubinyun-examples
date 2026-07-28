#!/usr/bin/env python3
"""Park a local file on Rubinyun, then schedule it.

1) upload the file and get back a public URL
2) ask for the best time to post next
3) schedule the post with that URL

Use this when you have a FILE but nowhere public to put it. The file is deleted
the moment the post is published: it is parking, not hosting.

Standard library only, no `pip install`.
Usage: python park_and_post.py photo.jpg
Docs: https://www.chrononyte.com/projects/rubinyun/docs.html
"""
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import uuid

BASE = "https://www.chrononyte.com/rubinyun"
KEY = "rby_live_PASTE_YOUR_KEY"
SECRET = "rby_sk_PASTE_YOUR_SECRET"

HEADERS = {"X-WS-Key": KEY, "X-WS-Secret": SECRET}


def call(action, data=None):
    """GET if no data, POST (form-urlencoded) if data. Raises on API error."""
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}/api.php?action={action}", data=body, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        out = json.load(resp)
    if not out.get("ok"):
        raise RuntimeError(f"{out.get('code')}: {out.get('error')}")
    return out


def park(path):
    """Upload a file and return the public URL Rubinyun parks it at.

    The multipart body is built by hand because the standard library has no
    helper for it. Two details matter and are easy to get wrong:
      - the field is called "image" for videos too (mp4, mov);
      - Rubinyun reads the extension from the FILE NAME in the body, so the
        filename has to keep it. Send "photo.jpg", never "photo".
    """
    filename = os.path.basename(path)
    with open(path, "rb") as fh:
        content = fh.read()
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    boundary = uuid.uuid4().hex

    body = b"".join([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode(),
        f"Content-Type: {ctype}\r\n\r\n".encode(),
        content,
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    headers = dict(HEADERS, **{"Content-Type": f"multipart/form-data; boundary={boundary}"})
    req = urllib.request.Request(f"{BASE}/upload.php", data=body, headers=headers)
    with urllib.request.urlopen(req) as resp:
        out = json.load(resp)
    if not out.get("ok"):
        # Worth branching on: file_too_big, content_mismatch (a .png that is not
        # a png: the first bytes are checked, not the name), parking_full,
        # bad_extension.
        raise RuntimeError(f"{out.get('code')}: {out.get('error')}")
    return out


if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    sys.exit("usage: python park_and_post.py <file>   (jpg, png, mp4 or mov)")
path = sys.argv[1]

# 1) Park the file.
up = park(path)
url = up["url"]
print("parked ->", url)

# The answer also says where you stand with your parking space, so a script can
# stop on its own instead of hitting parking_full on the next file.
used, limit = up["parking"]["used_bytes"], up["parking"]["limit_bytes"]
print(f"parking: {used / 1048576:.1f} MB used of {limit / 1048576:.0f} MB")

# 2) Best time to post next, worked out from your account's own history.
best = call("besttime")
when = best["slot"]["at"]          # "YYYY-MM-DD HH:MM"
print("best time:", when)

# 3) Schedule the post with the parked URL.
is_video = path.lower().endswith((".mp4", ".mov"))
post = {
    "type": "reel" if is_video else "image",
    "caption": "Parked and posted from Python with Rubinyun",
    "scheduled_at": when,
}
post["video_url" if is_video else "image_url"] = url
res = call("add", post)
print("scheduled:", res["post"]["id"], "for", res["post"]["scheduled_at"])
