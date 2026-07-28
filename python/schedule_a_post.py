#!/usr/bin/env python3
"""Schedule an image post to Instagram with Rubinyun.

1) ask for the best time to post next
2) schedule the post at that time

Standard library only, no `pip install`.
Docs: https://www.chrononyte.com/projects/rubinyun/docs.html
"""
import json
import urllib.error
import urllib.parse
import urllib.request

API = "https://www.chrononyte.com/rubinyun/api.php"
KEY = "rby_live_PASTE_YOUR_KEY"
SECRET = "rby_sk_PASTE_YOUR_SECRET"

HEADERS = {"X-WS-Key": KEY, "X-WS-Secret": SECRET}


def call(action, data=None):
    """GET if no data, POST (form-urlencoded) if data. Raises on API error."""
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(f"{API}?action={action}", data=body, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            out = json.load(resp)
    except urllib.error.HTTPError as e:
        # A refusal comes back with a 4xx status AND a JSON body saying why.
        # urllib raises on 4xx, so the body has to be read off the exception:
        # without this you would lose the code and see a bare traceback.
        out = json.load(e)
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
    "image_url": "https://www.chrononyte.com/assets/demo/rubinyun-demo.jpg",
    "caption": "Posted from Python with Rubinyun",
    "scheduled_at": when,
})
print("scheduled:", res["post"]["id"], "for", res["post"]["scheduled_at"])
