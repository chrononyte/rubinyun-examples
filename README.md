![Rubinyun: schedule and auto-publish to Instagram](https://www.chrononyte.com/assets/img/og/rubinyun.png?v=2)

# Rubinyun API examples

[Rubinyun](https://www.chrononyte.com/projects/rubinyun/) schedules and auto-publishes your content to **Instagram** at the time your audience is really online, read from your account's own data. From n8n, Make, a script, or the console. Even with your computer off.

This repository holds **usage examples** for the Rubinyun API, in **cURL, Python, Node and PHP**. The Rubinyun engine itself is closed source; here you only find how to call it.

## Get your keys

Create an account and generate an API **key + secret** (the secret is shown once):
<https://www.chrononyte.com/rubinyun/register.php>

Every request is authenticated with two headers:

```
X-WS-Key:    rby_live_...
X-WS-Secret: rby_sk_...
```

## The API in one minute

Base URL: `https://www.chrononyte.com/rubinyun/api.php`. You pick an action with the `action` parameter.

| action | | what it does |
|---|---|---|
| `besttime` | GET | the best time to post next, worked out from your account's own history. It steps around the posts already queued on that channel, so calling it in a loop gives you different times instead of stacking everything on the same minute |
| `add` | POST | schedule a post: `type` (`image`/`carousel`/`reel`/`story`), `image_url`, `caption`, `scheduled_at` (`YYYY-MM-DD HH:MM`) |
| `list` | GET | your scheduled and published posts |
| `channels`, `update`, `delete`, `retry`, `insights` | | manage channels and posts |

Responses are JSON. Success is `{"ok": true, ...}`. On error you get `{"ok": false, "code": "...", "error": "..."}`: the `code` is **stable** (e.g. `unauthorized`, `missing_scheduled_at`, `insufficient_tokens`), so branch on the `code`, not on the English message.

A refusal also carries an **HTTP status that says so** (401 wrong keys, 402 out of posts, 400 bad parameter, 413 file too large), never a 200. So a client that only checks the status still notices something went wrong, and one that reads the `code` knows exactly what. Two notes if you write your own client: in Python `urllib` **raises** on a 4xx, so read the body off the exception or you lose the reason; and with `curl -f` the body is thrown away, which is why the shell examples here do not use it.

A token is spent **only when a post actually publishes**, and connecting profiles is free. If your balance runs out between scheduling and publishing, the post is not published: it turns `failed` with `out of tokens`, you get an email, and it goes out once you top up and call `retry` on it.

Full API docs: <https://www.chrononyte.com/projects/rubinyun/docs.html>

## The examples

Each folder does the **same two things**, so you can compare languages.

**Schedule a post** from an image you already host somewhere: authenticate, ask for the best time, schedule.

- [`curl/schedule-a-post.sh`](curl/schedule-a-post.sh)
- [`python/schedule_a_post.py`](python/schedule_a_post.py)
- [`node/schedule-a-post.js`](node/schedule-a-post.js)
- [`php/schedule-a-post.php`](php/schedule-a-post.php)

**Park and post**, for when you have a **file** and nowhere public to put it: upload it, get a public URL back, then schedule with that URL. Takes the file as an argument, so run it as `park-and-post.sh photo.jpg`.

- [`curl/park-and-post.sh`](curl/park-and-post.sh)
- [`python/park_and_post.py`](python/park_and_post.py)
- [`node/park-and-post.js`](node/park-and-post.js)
- [`php/park-and-post.php`](php/park-and-post.php)

Open one, paste your key and secret at the top, and run it.

Three things about parking that are easy to get wrong, and that the examples handle for you: the upload field is called `image` **for videos too** (mp4, mov); the extension is read from the **file name** you send, so keep it (`photo.jpg`, not `photo`); and every upload answers with `parking.used_bytes` and `parking.limit_bytes`, so a script can stop on its own instead of hitting `parking_full` on the next file. It is **parking, not hosting**: the file is deleted the moment the post is published, and expires on its own after 14 days if it never is.

## n8n

There is a ready-made **n8n template**: import it and go. It is served from the site and always up to date, so this repo does **not** duplicate it.

- Template (import in n8n): <https://www.chrononyte.com/projects/rubinyun/rubinyun-n8n-template.json>
- Step-by-step guide: <https://www.chrononyte.com/projects/rubinyun/instagram-from-n8n.html>

## Links

- Product: <https://www.chrononyte.com/projects/rubinyun/>
- API docs: <https://www.chrononyte.com/projects/rubinyun/docs.html>
- Honest comparison with the alternatives: <https://www.chrononyte.com/projects/rubinyun/alternatives.html>

## License

MIT, see [LICENSE](LICENSE). These examples exist to be copied.
