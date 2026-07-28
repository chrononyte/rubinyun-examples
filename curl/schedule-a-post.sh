#!/usr/bin/env bash
# Schedule an image post to Instagram with Rubinyun.
#   1) ask for the best time to post next
#   2) schedule the post at that time
# Docs: https://www.chrononyte.com/projects/rubinyun/docs.html
set -euo pipefail

API="https://www.chrononyte.com/rubinyun/api.php"
KEY="rby_live_PASTE_YOUR_KEY"
SECRET="rby_sk_PASTE_YOUR_SECRET"

auth=(-H "X-WS-Key: $KEY" -H "X-WS-Secret: $SECRET")

# A refusal comes back as HTTP 200 with {"ok":false,"code":"...","error":"..."},
# so curl -f does not catch it and the script has to look for itself. The code
# is stable, the English message is not: branch on the code.
check() {
  case "$1" in
    *'"ok":false'*) echo "$1" >&2; exit 1 ;;
  esac
}

# 1) Best time to post next, worked out from your account's own history.
best=$(curl -fsS "${auth[@]}" "$API?action=besttime&when=tomorrow")
check "$best"
echo "besttime -> $best"

# Pull the slot's "at" (YYYY-MM-DD HH:MM). With jq installed it is cleaner:
#   WHEN=$(jq -r .slot.at <<<"$best")
# The "|| true" matters: with set -e, a grep that finds nothing would kill the
# script right here, and the fallback on the next line would never run.
WHEN=$(printf '%s' "$best" | grep -o '"at":"[^"]*"' | head -1 | sed 's/.*:"//; s/"$//' || true)
: "${WHEN:=2026-08-01 18:00}"   # fallback if you would rather choose the time yourself
echo "scheduling for: $WHEN"

# 2) Schedule the post.
res=$(curl -fsS -X POST "${auth[@]}" "$API?action=add" \
  --data-urlencode "type=image" \
  --data-urlencode "image_url=https://www.chrononyte.com/assets/demo/rubinyun-demo.jpg" \
  --data-urlencode "caption=Posted from a shell script with Rubinyun" \
  --data-urlencode "scheduled_at=$WHEN")
check "$res"
echo "$res"
