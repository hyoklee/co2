# Read the monthly bars off IBDP final report Figure 8-1 (embedded 961x605 PNG).
# Calibration from the gridlines: 0 kt at row 506, 50 kt at row 39.5.
# Each column is walked up from the axis through bar pixels; the red
# cumulative-percent line may cross a bar, so red pixels do not end the walk.
import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
Y0, Y50 = 506.0, 39.5
bar = (r < 60) & (g < 70) & (b < 130) & (b >= r)
red = (r > 150) & (g < 110) & (b < 110)

def top_of(c):
    y, top, gap = int(Y0) - 2, None, 0
    while y > 35:
        if bar[y, c]:
            top, gap = y, 0
        elif red[y, c]:
            gap = 0
        else:
            gap += 1
            if gap > 2: break
        y -= 1
    return top

tops = [top_of(c) for c in range(a.shape[1])]
height = [0 if t is None else Y0 - t for t in tops]
bars, x = [], 70
while x < 870:
    if height[x] > 3:
        s = x
        while x < 870 and height[x] > 3: x += 1
        if x - s >= 5:
            h = float(np.median(height[s + 2:x - 2]))
            bars.append(((s + x) / 2, h * 50.0 / (Y0 - Y50)))
    x += 1
months, y, m = [], 2011, 11
for _ in bars:
    months.append(f"{y}-{m:02d}")
    m += 1
    if m > 12: y, m = y + 1, 1
print("month,injected_kt_digitized")
for mo, (_, kt) in zip(months, bars): print(f"{mo},{kt:.2f}")
print(f"# {len(bars)} bars, total {sum(k for _, k in bars):.1f} kt", file=sys.stderr)
