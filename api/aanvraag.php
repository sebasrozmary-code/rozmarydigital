<?php
/**
 * Rozmary Digital — formulierverwerking (Groeiscan + contact).
 * Stuurt een mail naar $TO en bewaart een kopie in /data (afgeschermd via .htaccess).
 * Antwoordt JSON bij fetch(), anders een redirect naar de bedankpagina.
 */
$TO   = 'info@rozmarydigital.be';
$FROM = 'website@rozmarydigital.be';   // bestaand adres op het domein gebruiken (SPF/DKIM)

$wantsJson = isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false;
function done($ok, $wantsJson, $thanks = '/bedankt/', $code = 200) {
    if ($wantsJson) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok]);
    } else {
        header('Location: ' . ($ok ? $thanks : '/contact/?fout=1'), true, 303);
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') done(false, $wantsJson, '/', 405);

$f = function ($k, $max = 500) {
    $v = isset($_POST[$k]) ? trim((string)$_POST[$k]) : '';
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
};

// Bots: honingpot en minimale invultijd
$thanks = preg_match('#^[a-z0-9/-]+/$#', $f('thanks', 80)) ? '/' . ltrim($f('thanks', 80), '/') : '/bedankt/';
if ($f('company_url') !== '') done(true, $wantsJson, $thanks);
$ts = (int)$f('ts', 20);
if ($ts > 0 && (microtime(true) * 1000 - $ts) < 2500) done(true, $wantsJson, $thanks);

$data = [
    'naam'     => $f('name', 120),
    'bedrijf'  => $f('company', 160),
    'email'    => $f('email', 160),
    'telefoon' => $f('phone', 40),
    'website'  => $f('website', 200),
    'gemeente' => $f('city', 80),
    'interesse'=> $f('interest', 40),
    'bericht'  => $f('message', 4000),
    'taal'     => $f('lang', 5),
    'pagina'   => $f('page', 120),
];
if ($data['naam'] === '' || !filter_var($data['email'], FILTER_VALIDATE_EMAIL) || $f('consent', 2) !== '1') {
    done(false, $wantsJson, $thanks, 422);
}

$subject = 'Nieuwe aanvraag (' . ($data['interesse'] ?: 'contact') . ') — ' . $data['naam'];
$body = "Nieuwe aanvraag via rozmarydigital.be\n\n";
foreach ($data as $k => $v) { if ($v !== '') $body .= str_pad(ucfirst($k) . ':', 12) . $v . "\n"; }
$body .= "\nIP: " . ($_SERVER['REMOTE_ADDR'] ?? '-') . "\nTijd: " . date('Y-m-d H:i:s') . "\n";

$headers = [
    'From: Rozmary Digital website <' . $FROM . '>',
    'Reply-To: ' . $data['naam'] . ' <' . $data['email'] . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
];
$sent = @mail($TO, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, implode("\r\n", $headers), '-f' . $FROM);

// Kopie bewaren (wordt na 12 maanden gewist volgens het privacybeleid)
$dir = dirname(__DIR__) . '/data';
if (!is_dir($dir)) @mkdir($dir, 0750, true);
@file_put_contents($dir . '/aanvragen.jsonl', json_encode($data + ['tijd' => date('c'), 'mail' => $sent], JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX);

done((bool)$sent, $wantsJson, $thanks, $sent ? 200 : 500);
