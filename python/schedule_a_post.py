#!/usr/bin/env python3
"""Schedule an image post to Instagram with Rubinyun.

1) ask for the best time to post next
2) schedule the post at that time

Standard library only, no `pip install`.
Docs: https://www.chrononsync.com/projects/rubinyun/docs.html
"""
import json
import urllib.parse
import urllib.request

API = "https://www.chrononsync.com/rubinyun/api.php"
KEY = "rby_live_PASTE_YOUR_KEY"
SECRET = "rby_sk_PASTE_YOUR_SECRET"

HEADERS = {"X-WS-Key": KEY, "X-WS-Secret": SECRET}


def call(action, data=None):
    """GET if no data, POST (form-urlencoded) if data. Raises on API error."""
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(f"{API}?action={action}", data=body, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        out = json.load(resp)
    if not out.get("ok"):
        raise RuntimeError(f"{out.get('code')}: {out.get('error')}")
    return out


# 1) Best time to post next, worked out from your account's own history.
best = call("besttime")
when = best["slot"]["at"]          # "YYYY-MM-DD HH:MM"
print("best time:", when)

# 2) Schedule the post.
res = call("add", {
    "type": "image",
    "image_url": "https://www.chrononsync.com/assets/demo/rubinyun-demo.jpg",
    "caption": "Posted from Python with Rubinyun",
    "scheduled_at": when,
})
print("scheduled:", res["post"]["id"], "for", res["post"]["scheduled_at"])
