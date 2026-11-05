"""Compare the Figure 8-8 digitization with the ISGS event catalog.

Usage: python -I corr_f88.py <f88.csv from digitize_f88.py> <20180702.rdv>
"""
import csv
import datetime as dt
import sys

import numpy as np

DAYS_PER_COL = 3300.0 / 1120.0


def rank(v):
  return np.argsort(np.argsort(v)).astype(float)


def corr(x, y):
  x, y = np.asarray(x, float), np.asarray(y, float)
  return np.corrcoef(x, y)[0, 1], np.corrcoef(rank(x), rank(y))[0, 1]


def num(s):
  return float(s) if s != "" else np.nan


rows = list(csv.DictReader(open(sys.argv[1])))
date = [dt.date.fromisoformat(r["date"]) for r in rows]
col = {k: np.array([num(r[k]) for r in rows]) for k in rows[0] if k != "date"}

# events
ev = []
for n, line in enumerate(open(sys.argv[2])):
  if n < 2:
    continue
  f = line.split()
  d, mo, yy = f[0].split(":")[:3]
  ev.append((dt.date(2000 + int(yy), int(mo), int(d)), float(f[10])))
ev_dates = np.array([e[0].toordinal() for e in ev])
ev_mw = np.array([e[1] for e in ev])

print("== 1. Checks on the digitization ==")
q = col["ibdp_q"]
mass = np.nansum(q) * 24 * DAYS_PER_COL
print(f"IBDP rate integrated over the record: {mass/1e3:.0f} kt "
      f"(report total 999 kt; cumulative line peaks at "
      f"{np.nanmax(col['ibdp_cum'])/1e3:.0f} kt)")
qi = col["iccs_q"]
print(f"ICCS rate integrated: {np.nansum(qi)*24*DAYS_PER_COL/1e3:.0f} kt; "
      f"ICCS cumulative line ends at {np.nanmax(col['iccs_cum'])/1e3:.0f} kt")
inj = ~np.isnan(q)
print(f"IBDP median rate {np.nanmedian(q):.1f} T/hr = "
      f"{np.nanmedian(q)*24:.0f} t/day; ICCS median {np.nanmedian(qi):.1f} T/hr"
      f" = {np.nanmedian(qi)*24:.0f} t/day")

print("\n== 2. Pressure by phase (median psi) ==")
phases = [("first month (Nov-Dec 2011)", dt.date(2011, 11, 1), dt.date(2011, 12, 31)),
          ("injection plateau 2012-2014", dt.date(2012, 3, 1), dt.date(2014, 10, 31)),
          ("6 months after end", dt.date(2015, 3, 1), dt.date(2015, 6, 30)),
          ("late post-injection 2016-17", dt.date(2016, 6, 1), dt.date(2017, 3, 31))]
for k in ("wb1", "wb2", "wb3", "wb4", "wb5", "wb6"):
  out = []
  for _, a, b in phases:
    m = np.array([a <= d <= b for d in date])
    out.append(np.nanmedian(col[k][m]) if np.any(~np.isnan(col[k][m])) else np.nan)
  print(f"{k}: " + "  ".join(f"{p[0]}={v:.0f}" for p, v in zip(phases, out)))

# monthly table
months = sorted({(d.year, d.month) for d in date})
def month_of(o):
  d = dt.date.fromordinal(o)
  return (d.year, d.month)
ev_month = [month_of(o) for o in ev_dates]
tab = []
for ym in months:
  m = np.array([(d.year, d.month) == ym for d in date])
  shut = np.sum(m & inj & (col["ibdp_q_min"] < 15))  # columns touching ~0
  rec = {"month": "%04d-%02d" % ym,
         "events": sum(1 for x in ev_month if x == ym),
         "events_m0": int(sum(1 for x, w in zip(ev_month, ev_mw) if x == ym and w >= 0)),
         "wb2": np.nanmedian(col["wb2"][m]) if np.any(~np.isnan(col["wb2"][m])) else np.nan,
         "wb1": np.nanmedian(col["wb1"][m]) if np.any(~np.isnan(col["wb1"][m])) else np.nan,
         "q": np.nanmean(q[m]) if np.any(~np.isnan(q[m])) else np.nan,
         "shut_cols": int(shut)}
  tab.append(rec)

print("\n== 3. Monthly events vs pressure and rate, during IBDP injection ==")
dur = [t for t in tab if "2011-12" <= t["month"] <= "2014-10"]
for k in ("wb2", "wb1", "q", "shut_cols"):
  x = [t[k] for t in dur]; y = [t["events"] for t in dur]
  ok = ~np.isnan(np.array(x, float))
  x = np.array(x, float)[ok]; y = np.array(y, float)[ok]
  p, s = corr(x, y)
  p1, s1 = corr(x[:-1], y[1:])
  print(f"events vs {k:9s} n={len(x)}: same month Pearson {p:+.2f} Spearman {s:+.2f};"
        f" next month Pearson {p1:+.2f} Spearman {s1:+.2f}")

print("\n== 4. After injection: events vs pressure decay (Dec 2014 - Mar 2017) ==")
post = [t for t in tab if "2014-12" <= t["month"] <= "2017-03" and not np.isnan(t["wb2"])]
x = [t["wb2"] for t in post]; y = [t["events"] for t in post]
p, s = corr(x, y)
print(f"events vs WB2 pressure, n={len(post)} months: Pearson {p:+.2f}, Spearman {s:+.2f}")
for t in post[::3]:
  print(f"  {t['month']}: WB2 {t['wb2']:.0f} psi, {t['events']} events")

print("\n== 5. Shut-ins: event rate around rate drops ==")
# shut-in columns: IBDP rate line touches below 15 T/hr
def episodes(thr):
  sh = [i for i in range(len(rows)) if inj[i] and col["ibdp_q_min"][i] < thr]
  out = []
  for i in sh:
    if out and i - out[-1][-1] <= 1:
      out[-1].append(i)
    else:
      out.append([i])
  return [e for e in out if date[e[0]] > dt.date(2011, 12, 15)]
sh = [i for i in range(len(rows)) if inj[i] and col["ibdp_q_min"][i] < 15]
# group consecutive columns
eps = []
for i in sh:
  if eps and i - eps[-1][-1] <= 1:
    eps[-1].append(i)
  else:
    eps.append([i])
eps = [e for e in eps if date[e[0]] > dt.date(2011, 12, 15)]
def rate(a, b):  # events per day in [a, b)
  n = np.sum((ev_dates >= a) & (ev_dates < b))
  return n / max(b - a, 1)
before, during_, after = [], [], []
for e in eps:
  a = date[e[0]].toordinal(); b = date[e[-1]].toordinal() + 3
  before.append(rate(a - 14, a)); during_.append(rate(a, b)); after.append(rate(b, b + 14))
print(f"{len(eps)} shut-in episodes (rate line below 15 T/hr), Dec 2011 - Nov 2014")
print(f"mean events/day: 14 d before {np.mean(before):.2f}, during {np.mean(during_):.2f},"
      f" 14 d after {np.mean(after):.2f}")
for e, b0, d0, a0 in zip(eps, before, during_, after):
  print(f"  {date[e[0]]}..{date[e[-1]]}: {b0:.2f} / {d0:.2f} / {a0:.2f}")

print("\n== 6. ICCS period (catalog runs to Jul 2018) ==")
for a, b, name in ((dt.date(2016, 4, 1), dt.date(2017, 3, 31), "12 months before ICCS"),
                   (dt.date(2017, 7, 1), dt.date(2018, 6, 30), "first 12 months of ICCS (from Jul 2017)")):
  n = np.sum((ev_dates >= a.toordinal()) & (ev_dates <= b.toordinal()))
  print(f"{name}: {n} located events")

print("\n== 7. Shut-in test against random windows ==")
# Ratio of the event rate during each episode to the 14 days before, compared with
# the same ratio for randomly placed windows of the same lengths during injection.
rng = np.random.default_rng(1)
lens = [date[e[-1]].toordinal() + 3 - date[e[0]].toordinal() for e in eps]
lo, hi = dt.date(2012, 1, 1).toordinal(), dt.date(2014, 11, 1).toordinal()
def log_ratio(a, L):
  return np.log((rate(a, a + L) + 0.1) / (rate(a - 14, a) + 0.1))
obs = np.median([log_ratio(date[e[0]].toordinal(), L) for e, L in zip(eps, lens)])
null = [np.median([log_ratio(int(rng.integers(lo, hi - L)), L) for L in lens])
        for _ in range(2000)]
pval = np.mean(np.array(null) <= obs)
print(f"median during/before rate ratio: shut-ins {np.exp(obs):.2f}, random windows "
      f"{np.exp(np.median(null)):.2f} (5-95%: {np.exp(np.percentile(null, 5)):.2f}-"
      f"{np.exp(np.percentile(null, 95)):.2f}); one-sided p = {pval:.3f}")
print(f"median events/day: before {np.median(before):.2f}, during {np.median(during_):.2f},"
      f" after {np.median(after):.2f}")

print("\n== 8. Sensitivity of the shut-in test ==")
def shut_test(thr, win, n_iter=1000):
  E = episodes(thr)
  L = [date[e[-1]].toordinal() + 3 - date[e[0]].toordinal() for e in E]
  def lr(a, l):
    n1 = np.sum((ev_dates >= a) & (ev_dates < a + l)) / l
    n0 = np.sum((ev_dates >= a - win) & (ev_dates < a)) / win
    return np.log((n1 + 0.1) / (n0 + 0.1))
  o = np.median([lr(date[e[0]].toordinal(), l) for e, l in zip(E, L)])
  nl = [np.median([lr(int(rng.integers(lo, hi - l)), l) for l in L]) for _ in range(n_iter)]
  return len(E), np.exp(o), np.mean(np.array(nl) <= o)
for thr in (10, 15, 20):
  for win in (7, 14, 28):
    n, r, pv = shut_test(thr, win)
    print(f"threshold {thr:2d} T/hr, baseline {win:2d} d: {n:2d} episodes, ratio {r:.2f}, p = {pv:.3f}")
