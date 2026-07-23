#!/usr/bin/env bash
# Schedule an image post to Instagram with Rubinyun.
#   1) ask for the best time to post next
#   2) schedule the post at that time
# Docs: https://www.chrononsync.com/projects/rubinyun/docs.html
set -euo pipefail

API="https://www.chrononsync.com/rubinyun/api.php"
KEY="rby_live_PASTE_YOUR_KEY"
SECRET="rby_sk_PASTE_YOUR_SECRET"

auth=(-H "X-WS-Key: $KEY" -H "X-WS-Secret: $SECRET")

# 1) Best time to post next, worked out from your account's own history.
best=$(curl -fsS "${auth[@]}" "$API?action=besttime&when=tomorrow")
echo "besttime -> $best"

# Pull the slot's "at" (YYYY-MM-DD HH:MM). With jq installed it is cleaner:
#   WHEN=$(jq -r .slot.at <<<"$best")
WHEN=$(printf '%s' "$best" | grep -o '"at":"[^"]*"' | head -1 | sed 's/.*:"//; s/"$//')
: "${WHEN:=2026-08-01 18:00}"   # fallback if you would rather choose the time yourself
echo "scheduling for: $WHEN"

# 2) Schedule the post.
curl -fsS -X POST "${auth[@]}" "$API?action=add" \
  --data-urlencode "type=image" \
  --data-urlencode "image_url=https://www.chrononsync.com/assets/demo/rubinyun-demo.jpg" \
  --data-urlencode "caption=Posted from a shell script with Rubinyun" \
  --data-urlencode "scheduled_at=$WHEN"
echo
