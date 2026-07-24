<?php
// Schedule an image post to Instagram with Rubinyun.
//   1) ask for the best time to post next
//   2) schedule the post at that time
// Needs the curl extension (bundled with most PHP). Run: php schedule-a-post.php
// Docs: https://www.chrononyte.com/projects/rubinyun/docs.html

const API    = 'https://www.chrononyte.com/rubinyun/api.php';
const KEY    = 'rby_live_PASTE_YOUR_KEY';
const SECRET = 'rby_sk_PASTE_YOUR_SECRET';

// GET if no data, POST (form-urlencoded) if data. Throws on API error.
function call(string $action, ?array $data = null): array {
    $ch = curl_init(API . '?action=' . $action);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ['X-WS-Key: ' . KEY, 'X-WS-Secret: ' . SECRET],
    ]);
    if ($data !== null) {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    }
    $out = json_decode((string) curl_exec($ch), true);
    curl_close($ch);
    if (empty($out['ok'])) {
        throw new RuntimeException(($out['code'] ?? 'error') . ': ' . ($out['error'] ?? 'request failed'));
    }
    return $out;
}

// 1) Best time to post next, worked out from your account's own history.
$best = call('besttime');
$when = $best['slot']['at'];        // "YYYY-MM-DD HH:MM"
echo "best time: $when\n";

// 2) Schedule the post.
$res = call('add', [
    'type'         => 'image',
    'image_url'    => 'https://www.chrononyte.com/assets/demo/rubinyun-demo.jpg',
    'caption'      => 'Posted from PHP with Rubinyun',
    'scheduled_at' => $when,
]);
echo "scheduled: {$res['post']['id']} for {$res['post']['scheduled_at']}\n";
