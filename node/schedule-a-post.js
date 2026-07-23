#!/usr/bin/env node
// Schedule an image post to Instagram with Rubinyun.
//   1) ask for the best time to post next
//   2) schedule the post at that time
// Needs Node 18+ (built-in fetch). No `npm install`.
// Docs: https://www.chrononsync.com/projects/rubinyun/docs.html

const API = "https://www.chrononsync.com/rubinyun/api.php";
const KEY = "rby_live_PASTE_YOUR_KEY";
const SECRET = "rby_sk_PASTE_YOUR_SECRET";

const auth = { "X-WS-Key": KEY, "X-WS-Secret": SECRET };

// GET if no data, POST (form-urlencoded) if data. Throws on API error.
async function call(action, data) {
  const opts = { headers: auth };
  if (data) {
    opts.method = "POST";
    opts.body = new URLSearchParams(data);
  }
  const res = await fetch(`${API}?action=${action}`, opts);
  const out = await res.json();
  if (!out.ok) throw new Error(`${out.code}: ${out.error}`);
  return out;
}

(async () => {
  // 1) Best time to post next, worked out from your account's own history.
  const best = await call("besttime");
  const when = best.slot.at;        // "YYYY-MM-DD HH:MM"
  console.log("best time:", when);

  // 2) Schedule the post.
  const res = await call("add", {
    type: "image",
    image_url: "https://www.chrononsync.com/assets/demo/rubinyun-demo.jpg",
    caption: "Posted from Node with Rubinyun",
    scheduled_at: when,
  });
  console.log("scheduled:", res.post.id, "for", res.post.scheduled_at);
})();
