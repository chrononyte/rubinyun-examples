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
| `besttime` | GET | the best time to post next, worked out from your account's own history |
| `add` | POST | schedule a post: `type` (`image`/`carousel`/`reel`/`story`), `image_url`, `caption`, `scheduled_at` (`YYYY-MM-DD HH:MM`) |
| `list` | GET | your scheduled and published posts |
| `channels`, `update`, `delete`, `retry`, `insights` | | manage channels and posts |

Responses are JSON. Success is `{"ok": true, ...}`. On error you get `{"ok": false, "code": "...", "error": "..."}`: the `code` is **stable** (e.g. `unauthorized`, `missing_scheduled_at`, `insufficient_tokens`), so branch on the `code`, not on the English message.

A token is spent **only when a post actually publishes**, and connecting profiles is free.

Full API docs: <https://www.chrononyte.com/projects/rubinyun/docs.html>

## The examples

Each folder does the **same thing**, so you can compare languages: authenticate, ask for the best time, then schedule an image post.

- [`curl/schedule-a-post.sh`](curl/schedule-a-post.sh)
- [`python/schedule_a_post.py`](python/schedule_a_post.py)
- [`node/schedule-a-post.js`](node/schedule-a-post.js)
- [`php/schedule-a-post.php`](php/schedule-a-post.php)

Open one, paste your key and secret at the top, and run it.

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
