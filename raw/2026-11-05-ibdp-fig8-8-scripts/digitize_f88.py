"""Digitize Figure 8-8 of the final IBDP report (PDF page 212).

Usage: python -I digitize_f88.py <img-000.png> <out.csv>

The image is the 1422x1033 raster from `pdfimages -f 212 -l 212 -png`.
Every non-background pixel in the plot is assigned to the nearest palette
colour (legend swatches plus gridline/axis greys), and for each pixel column
the median row of each series is converted to data units.

Calibration (measured from gridlines and tick marks):
  left axis   2900 psi at row 823, 50 psi per 76.75 px
  right axis  0 t at row 823, 2,100,000 t at row 55.5  (2736 t/px)
  x axis      2011-11-01 at column 129 (left axis line) and 2020-11-13 at
              column 1249 (right axis line): the 34 date labels are 100 days
              apart, so 3300 days per 1120 px, about 2.95 days per column.
              Checked against the IBDP rate line ending at column 504
              (about 2014-11-10; injection ended 2014-11-26).
The daily-rate series are plotted as 1000 x (T/hr) on the right axis, so
rate_t_per_hr = right-axis value / 1000 (resolution about 2.7 T/hr).
"""
import csv
import datetime as dt
import sys

import numpy as np
from PIL import Image

PALETTE = {
    "wb1": (51, 88, 153),       # WB Zone 1, 7,061 ft, diamonds
    "wb2": (104, 162, 66),      # WB Zone 2, 6,983 ft, triangles
    "wb3": (155, 173, 219),     # WB Zone 3, 6,946 ft, crosses
    "wb4": (244, 179, 149),     # WB Zone 4, 6,838 ft, crosses
    "wb5": (181, 181, 181),     # WB Zone 5, 6,720 ft, dots
    "wb6": (255, 202, 105),     # WB Zone 6, 6,632 ft, plus
    "g1": (129, 129, 129),      # VW1 G1, 6,935 ft, line
    "g2": (200, 150, 0),        # VW1 G2, 6,430 ft, line
    "g3": (70, 121, 167),       # VW1 G3, 6,418 ft, line
    "ibdp_cum": (0, 176, 240),  # IBDP cumulative injected mass
    "ibdp_q": (186, 97, 36),    # IBDP 1000 x daily average rate, T/hr
    "iccs_q": (86, 135, 54),    # ICCS 1000 x daily average rate, T/hr
    "iccs_cum": (63, 106, 183),  # unlabelled steep line: ICCS cumulative
    # non-data colours, so they are not mistaken for a series
    "_grid1": (225, 225, 225), "_grid2": (167, 167, 167),
    "_grid3": (196, 196, 196), "_black": (0, 0, 0),
    "_white": (255, 255, 255),
}
PRESSURE = ["wb1", "wb2", "wb3", "wb4", "wb5", "wb6", "g1", "g2", "g3"]
TONNES = ["ibdp_cum", "iccs_cum"]
RATE = ["ibdp_q", "iccs_q"]
MAXDIST = 30  # reject pixels far from every palette colour (antialiasing)

X0, XPX, XDAYS = 129, 1120.0, 3300.0
# active periods (days since D0): IBDP 2011-11-17..2014-11-26, ICCS from 2017
IBDP_END, ICCS_START = 1135, 1900
# Westbay zone markers stop at column ~802 (2017-04); VW1 gauge lines start after
WB_END, VW_START = 1990, 1990
# WB zones 1, 3 and 5 have no markers after Dec 2014 (column ~515)
WB_SHORT, WB_SHORT_END = ("wb1", "wb3", "wb5"), 1156
Y_AXIS, Y_TOP = 823.0, 55.5
D0 = dt.date(2011, 11, 1)


def psi(y):
  return 2900.0 + (Y_AXIS - y) * 50.0 / 76.75


def tonnes(y):
  return (Y_AXIS - y) * 2100000.0 / (Y_AXIS - Y_TOP)


def main(src, out):
  a = np.array(Image.open(src).convert("RGB")).astype(int)
  names = list(PALETTE)
  pal = np.array([PALETTE[n] for n in names])
  y_lo, y_hi, x_lo, x_hi = 57, 822, 131, 1248  # inside the axes
  sub = a[y_lo:y_hi + 1, x_lo:x_hi + 1]
  d = ((sub[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
  lab = d.argmin(-1)
  ok = np.sqrt(d.min(-1)) <= MAXDIST
  rows = []
  for xi in range(sub.shape[1]):
    x = x_lo + xi
    day = (x - X0) * XDAYS / XPX
    rec = {"x_px": x, "date": str(D0 + dt.timedelta(days=round(day))),
           "day": round(day, 2)}
    for n in PRESSURE + TONNES + RATE:
      k = names.index(n)
      ys = np.nonzero((lab[:, xi] == k) & ok[:, xi])[0] + y_lo
      if n in RATE:
        # rates live in the bottom band (below ~160 T/hr)
        ys = ys[ys > Y_AXIS - 60]
      elif n in PRESSURE:
        # keep pressure markers out of the rate band at the bottom
        ys = ys[ys < Y_AXIS - 40]
      if (n.startswith("ibdp") and day > IBDP_END) or \
         (n.startswith("iccs") and day < ICCS_START) or \
         (n.startswith("wb") and day > WB_END) or \
         (n in WB_SHORT and day > WB_SHORT_END) or \
         (n.startswith("g") and day < VW_START):
        ys = ys[:0]
      if len(ys) < 2:
        rec[n] = ""
        if n in RATE:
          rec[n + "_min"] = ""
        continue
      ym = float(np.median(ys))
      if n in PRESSURE:
        rec[n] = round(psi(ym), 1)
      elif n in TONNES:
        rec[n] = round(tonnes(ym))
      else:
        rec[n] = round(tonnes(ym) / 1000.0, 1)            # T/hr
        rec[n + "_min"] = round(tonnes(ys.max()) / 1000.0, 1)  # lowest point
    rows.append(rec)
  cols = (["x_px", "date", "day"] + PRESSURE + TONNES +
          ["ibdp_q", "ibdp_q_min", "iccs_q", "iccs_q_min"])
  with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
  print("wrote", len(rows), "columns to", out)


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
