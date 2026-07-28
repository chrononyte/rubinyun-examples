<?php
// Park a local file on Rubinyun, then schedule it.
//   1) upload the file and get back a public URL
//   2) ask for the best time to post next
//   3) schedule the post with that URL
// Use this when you have a FILE but nowhere public to put it. The file is
// deleted the moment the post is published: it is parking, not hosting.
// Needs the curl extension (bundled with most PHP).
// Run: php park-and-post.php photo.jpg
// Docs: https://www.chrononyte.com/projects/rubinyun/docs.html

const BASE   = 'https://www.chrononyte.com/rubinyun';
const KEY    = 'rby_live_PASTE_YOUR_KEY';
const SECRET = 'rby_sk_PASTE_YOUR_SECRET';

function headers(): array {
    return ['X-WS-Key: ' . KEY, 'X-WS-Secret: ' . SECRET];
}

// GET if no data, POST (form-urlencoded) if data. Throws on API error.
function call(string $action, ?array $data = null): array {
    $ch = curl_init(BASE . '/api.php?action=' . $action);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => headers()]);
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

// Upload a file and return the public URL Rubinyun parks it at.
// Two details matter and are easy to get wrong:
//   - the field is called "image" for videos too (mp4, mov);
//   - Rubinyun reads the extension from the FILE NAME in the body. CURLFile
//     takes it from the path, but pass the third argument when the file on
//     disk is called something else (a temp file with no extension, say).
function park(string $path): array {
    $ch = curl_init(BASE . '/upload.php');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => headers(),
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => ['image' => new CURLFile($path, null, basename($path))],
    ]);
    $out = json_decode((string) curl_exec($ch), true);
    curl_close($ch);
    // Worth branching on: file_too_big, content_mismatch (a .png that is not a
    // png: the first bytes are checked, not the name), parking_full,
    // bad_extension.
    if (empty($out['ok'])) {
        throw new RuntimeException(($out['code'] ?? 'error') . ': ' . ($out['error'] ?? 'upload failed'));
    }
    return $out;
}

$path = $argv[1] ?? '';
if ($path === '' || !is_file($path)) {
    fwrite(STDERR, "usage: php park-and-post.php <file>   (jpg, png, mp4 or mov)\n");
    exit(2);
}

// 1) Park the file.
$up = park($path);
echo "parked -> {$up['url']}\n";

// The answer also says where you stand with your parking space, so a script can
// stop on its own instead of hitting parking_full on the next file.
printf("parking: %.1f MB used of %.0f MB\n",
    $up['parking']['used_bytes'] / 1048576, $up['parking']['limit_bytes'] / 1048576);

// 2) Best time to post next, worked out from your account's own history.
$best = call('besttime');
$when = $best['slot']['at'];        // "YYYY-MM-DD HH:MM"
echo "best time: $when\n";

// 3) Schedule the post with the parked URL.
$isVideo = (bool) preg_match('/\.(mp4|mov)$/i', $path);
$res = call('add', [
    'type'                                  => $isVideo ? 'reel' : 'image',
    $isVideo ? 'video_url' : 'image_url'    => $up['url'],
    'caption'                               => 'Parked and posted from PHP with Rubinyun',
    'scheduled_at'                          => $when,
]);
echo "scheduled: {$res['post']['id']} for {$res['post']['scheduled_at']}\n";
