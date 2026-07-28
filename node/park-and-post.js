#!/usr/bin/env node
// Park a local file on Rubinyun, then schedule it.
//   1) upload the file and get back a public URL
//   2) ask for the best time to post next
//   3) schedule the post with that URL
// Use this when you have a FILE but nowhere public to put it. The file is
// deleted the moment the post is published: it is parking, not hosting.
// Needs Node 18+ (built-in fetch, FormData and Blob). No `npm install`.
// Usage: node park-and-post.js photo.jpg
// Docs: https://www.chrononyte.com/projects/rubinyun/docs.html

const fs = require("fs");
const path = require("path");

const BASE = "https://www.chrononyte.com/rubinyun";
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
  const res = await fetch(`${BASE}/api.php?action=${action}`, opts);
  const out = await res.json();
  if (!out.ok) throw new Error(`${out.code}: ${out.error}`);
  return out;
}

// Upload a file and return the public URL Rubinyun parks it at.
// Two details matter and are easy to get wrong:
//   - the field is called "image" for videos too (mp4, mov);
//   - Rubinyun reads the extension from the FILE NAME in the body, so pass the
//     name as the third argument of append. Without it the body carries
//     "blob" and you get bad_extension on a perfectly good file.
async function park(file) {
  const body = new FormData();
  body.append("image", new Blob([fs.readFileSync(file)]), path.basename(file));
  // Do not set Content-Type by hand here: fetch adds it with the boundary.
  const res = await fetch(`${BASE}/upload.php`, { method: "POST", headers: auth, body });
  const out = await res.json();
  // Worth branching on: file_too_big, content_mismatch (a .png that is not a
  // png: the first bytes are checked, not the name), parking_full,
  // bad_extension.
  if (!out.ok) throw new Error(`${out.code}: ${out.error}`);
  return out;
}

(async () => {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) {
    console.error("usage: node park-and-post.js <file>   (jpg, png, mp4 or mov)");
    process.exit(2);
  }

  // 1) Park the file.
  const up = await park(file);
  console.log("parked ->", up.url);

  // The answer also says where you stand with your parking space, so a script
  // can stop on its own instead of hitting parking_full on the next file.
  const mb = (n, d = 1) => (n / 1048576).toFixed(d);
  console.log(`parking: ${mb(up.parking.used_bytes)} MB used of ${mb(up.parking.limit_bytes, 0)} MB`);

  // 2) Best time to post next, worked out from your account's own history.
  const best = await call("besttime");
  const when = best.slot.at;        // "YYYY-MM-DD HH:MM"
  console.log("best time:", when);

  // 3) Schedule the post with the parked URL.
  const isVideo = /\.(mp4|mov)$/i.test(file);
  const post = {
    type: isVideo ? "reel" : "image",
    caption: "Parked and posted from Node with Rubinyun",
    scheduled_at: when,
  };
  post[isVideo ? "video_url" : "image_url"] = up.url;
  const res = await call("add", post);
  console.log("scheduled:", res.post.id, "for", res.post.scheduled_at);
})();
