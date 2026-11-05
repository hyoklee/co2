# First look: monthly located-event counts vs monthly injected CO2 (IBDP).
import sys, csv, numpy as np
inj = {}
for row in csv.DictReader(open(sys.argv[1])):
    inj[row["month"]] = float(row["injected_kt_digitized"])
counts, counts_m0 = {}, {}
for n, line in enumerate(open(sys.argv[2])):
    if n < 2: continue
    f = line.split()
    d, mo, yy = f[0].split(":")[:3]
    key = f"20{yy}-{mo}"
    mw = float(f[10])
    counts[key] = counts.get(key, 0) + 1
    if mw >= 0: counts_m0[key] = counts_m0.get(key, 0) + 1
months = sorted(set(counts) | set(inj))
def rank(v): return np.argsort(np.argsort(v)).astype(float)
def corr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return np.corrcoef(x, y)[0, 1], np.corrcoef(rank(x), rank(y))[0, 1]
inj_m = [m for m in months if m in inj and m != "2011-11"]  # first month: injection began on the 17th
x = [inj[m] for m in inj_m]
for name, c in (("all located", counts), ("Mw>=0", counts_m0)):
    y = [c.get(m, 0) for m in inj_m]
    p, s = corr(x, y)
    print(f"{name:12s} monthly vs injected (n={len(inj_m)}): Pearson {p:+.2f}, Spearman {s:+.2f}")
    # one-month lag: events this month vs last month's injection
    p1, s1 = corr(x[:-1], y[1:])
    print(f"{'':12s} lag 1 month: Pearson {p1:+.2f}, Spearman {s1:+.2f}")
# cumulative
during = sum(counts.get(m, 0) for m in inj)
after = sum(v for m, v in counts.items() if m > "2014-11")
print(f"located events during injection months: {during}, after (Dec 2014 - Jul 2018): {after}")
cum_i, cum_e = np.cumsum(x), np.cumsum([counts.get(m, 0) for m in inj_m])
print("cumulative events vs cumulative injected: Pearson %+.3f" % np.corrcoef(cum_i, cum_e)[0, 1])
by_year = {}
for m in inj: by_year.setdefault(m[:4], [0, 0]); by_year[m[:4]][0] += inj[m]; by_year[m[:4]][1] += counts.get(m, 0)
for yv, (kt, ev) in sorted(by_year.items()): print(f"  {yv}: {kt:6.1f} kt injected, {ev:5d} located events, {ev/kt:5.1f} events/kt")
