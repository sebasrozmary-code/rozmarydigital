"""Trace the RD monogram (blue R + white D) from the supplied PNG into SVG paths."""
import cv2, numpy as np, json, sys
SRC = '/root/.claude/uploads/9ee87979-6e27-5218-8274-dd9214241bf9/69ce836f-image.png'
img = cv2.imread(SRC)  # BGR
S = 4
big = cv2.resize(img, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
b, g, r = [big[:, :, i].astype(int) for i in range(3)]
blue = ((b > 170) & (r < 140) & (b - r > 90)).astype(np.uint8) * 255
white = ((b > 175) & (g > 175) & (r > 175)).astype(np.uint8) * 255
k = np.ones((3, 3), np.uint8)
blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, k); white = cv2.morphologyEx(white, cv2.MORPH_OPEN, k)

def paths(mask, eps):
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = []
    for c in cnts:
        if cv2.contourArea(c) < 400 * S:  # drop specks
            continue
        a = cv2.approxPolyDP(c, eps, True).reshape(-1, 2) / S
        d.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in a) + 'Z')
    return ' '.join(d)

pb, pw = paths(blue, 2.2), paths(white, 2.2)
ys, xs = np.where((blue | white) > 0)
bbox = (xs.min() / S, ys.min() / S, xs.max() / S, ys.max() / S)
json.dump({'blue': pb, 'white': pw, 'bbox': bbox}, open('tools/logo_paths.json', 'w'))
print('bbox', bbox, 'len', len(pb), len(pw))
