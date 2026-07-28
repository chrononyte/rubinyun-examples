#!/usr/bin/env bash
# Park a local file on Rubinyun, then schedule it.
#   1) upload the file and get back a public URL
#   2) ask for the best time to post next
#   3) schedule the post with that URL
# Use this when you have a FILE but nowhere public to put it. The file is
# deleted the moment the post is published: it is parking, not hosting.
# Usage: ./park-and-post.sh photo.jpg
# Docs: https://www.chrononyte.com/projects/rubinyun/docs.html
set -euo pipefail

BASE="https://www.chrononyte.com/rubinyun"
KEY="rby_live_PASTE_YOUR_KEY"
SECRET="rby_sk_PASTE_YOUR_SECRET"

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "usage: $0 <file>   (jpg, png, mp4 or mov)" >&2
  exit 2
fi

auth=(-H "X-WS-Key: $KEY" -H "X-WS-Secret: $SECRET")
# Reads a top-level field out of a JSON response, string or number. With jq
# installed it is cleaner: jq -r .url <<<"$json"
field() { printf '%s' "$2" | grep -oE "\"$1\":(\"[^\"]*\"|[0-9]+)" | head -1 | sed 's/^[^:]*://; s/^"//; s/"$//'; }

# A refusal comes back as HTTP 200 with {"ok":false,"code":"...","error":"..."},
# so curl -f does not catch it and the script has to look for itself. Without
# this a rejected file (content_mismatch, file_too_big, parking_full,
# bad_extension) would kill the script with no message at all.
check() {
  case "$1" in
    *'"ok":false'*) echo "$1" >&2; exit 1 ;;
  esac
}

# 1) Park the file. The field is called "image" for videos too, and the
#    extension is taken from the FILE NAME you send: park it as photo.jpg,
#    not as photo. curl sends the name for you with @.
up=$(curl -fsS "${auth[@]}" -F "image=@$FILE" "$BASE/upload.php")
check "$up"
URL=$(field url "$up")
echo "parked -> $URL"

# The answer also says where you stand with your parking space, so a script can
# stop on its own instead of hitting parking_full on the next file.
echo "parking: $(field used_bytes "$up") of $(field limit_bytes "$up") bytes used"

# 2) Best time to post next, worked out from your account's own history.
best=$(curl -fsS "${auth[@]}" "$BASE/api.php?action=besttime&when=tomorrow")
check "$best"
WHEN=$(field at "$best")
: "${WHEN:=2026-08-01 18:00}"   # fallback if you would rather choose the time yourself
echo "scheduling for: $WHEN"

# 3) Schedule the post with the parked URL. Use video_url and type=reel for mp4.
curl -fsS -X POST "${auth[@]}" "$BASE/api.php?action=add" \
  --data-urlencode "type=image" \
  --data-urlencode "image_url=$URL" \
  --data-urlencode "caption=Parked and posted from a shell script with Rubinyun" \
  --data-urlencode "scheduled_at=$WHEN"
echo
