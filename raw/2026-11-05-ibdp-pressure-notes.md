# Notes: IBDP daily injection rate and reservoir pressure (final-report Figure 8-8) against the event catalog

Made 2026-11-05 from the copy of the dataset on Aurora
(`/lus/flare/projects/IOWarp/hyoklee/co2datashare/ibdp/`). Follows
[2026-11-04-ibdp-injection-notes.md](2026-11-04-ibdp-injection-notes.md).

## Source and method

- **Figure 8-8**, "Pressure monitored in VW1 zones and CO2 injection history. (VW1 G1, VW1 G2,
  and VW1 G3 are Baker gauges.)" Final report, PDF page 212 (printed 177). It is one embedded
  1422×1033 image, with no table behind it.
- **Series in the legend:**
  - Westbay zones 1–6 at 7,061 / 6,983 / 6,946 / 6,838 / 6,720 / 6,632 ft;
  - VW1 gauges G1–G3 at 6,935 / 6,430 / 6,418 ft;
  - IBDP calculated cumulative injected mass;
  - IBDP and ICCS "1000 x Daily Ave INJ Q, T/hr".
- **An unlabelled steep blue line** starts at the "Start of ICCS Injection" arrow and ends at
  about 2.08 Mt. I read it as ICCS cumulative mass.
- **Method:** [digitize_f88.py](2026-11-05-ibdp-fig8-8-scripts/digitize_f88.py) gives each
  plot pixel the nearest legend colour. For each pixel column, it takes the median row of each
  series.
  - The rate lines are only read in the band near the axis, and pressure markers only above it.
  - Each series is masked to the period where the chart shows it: Westbay zones to Apr 2017,
    zones 1, 3 and 5 to Dec 2014, VW1 gauges from Apr 2017.
- **Calibration:**
  - Left axis: 2900 psi at row 823, 50 psi per 76.75 px.
  - Right axis: 0 t at row 823, 2.1 Mt at row 55.5.
  - x axis: 11/01/11 at column 129 and 11/13/20 at column 1249. The 34 date labels are 100 days
    apart, so one column is about 2.95 days.
  - The major tick marks are 267 px apart, about 787 days, not 500 days. A first pass that
    assumed 500 days put the end of the record in 2017, so I dropped it.
- **Output:** [2026-11-05-ibdp-fig8-8-digitized.csv](2026-11-05-ibdp-fig8-8-digitized.csv).
- **Comparison:** [corr_f88.py](2026-11-05-ibdp-fig8-8-scripts/corr_f88.py); full output in
  [corr_f88_output.txt](2026-11-05-ibdp-fig8-8-scripts/corr_f88_output.txt).

## Checks on the reading

- **Cumulative mass:** the IBDP line peaks at 999 kt (report total 999,215 t).
- **Timing:** the IBDP rate line ends at about 2014-11-10, against 2014-11-26 in the report.
  Dates are good to about ±2 weeks.
- **Integrated rate:** the digitized IBDP rate integrates to 900 kt, 10% low. The median is
  38.3 T/hr (919 t/day), against a design rate of about 1,000 t/day. Use the cumulative line for
  mass, and the rate only for timing and shut-ins.
- **ICCS:** the rate integrates to 1,921 kt, against 2,084 kt at the end of the cumulative line.
  The median rate is 57.5 T/hr (1,380 t/day).

## Pressure (median psi from the digitized series)

| Zone (depth) | Nov–Dec 2011 | Mar 2012 – Oct 2014 | Mar–Jun 2015 | Jun 2016 – Mar 2017 |
|---|---|---|---|---|
| WB1 (7,061 ft) | 3244 | 3330 | — | — |
| WB2 (6,983 ft) | 3253 | 3327 | 3222 | 3200 |
| WB3 (6,946 ft) | 3199 | 3292 | — | — |
| WB4 (6,838 ft) | 3124 | 3152 | 3123 | 3120 |
| WB5 (6,720 ft) | 3052 | 3072 | — | — |
| WB6 (6,632 ft) | 3014 | 3028 | 3027 | 3020 |

- **Deep zones (WB1–WB3) build up fast:**
  - WB2 rose from about 3230 psi (first readings, early Nov 2011) to about 3343 psi by early
    Jan 2012.
  - It then held a plateau, with drops at each shut-in, until injection ended.
- **Shallower zones (WB4–WB6) rose by only 15–30 psi.**
- **After injection, WB2 fell back:**
  - 3236 psi in Dec 2014;
  - 3222 psi by Mar 2015;
  - 3191 psi by Feb 2017.
- **VW1 gauges during ICCS (2017–2020):**
  - G2 and G3 (6,430 / 6,418 ft) climbed steadily, from about 3035–3043 psi in late 2017 to
    3149–3156 psi in Oct 2020.
  - G1 (6,935 ft) stayed at 3200–3230 psi.
  - So ICCS pressure shows up in the shallower gauges, not at the IBDP injection depth.

## Comparison with the catalog (`20180702.rdv`, 5,397 located events)

**Monthly, during IBDP injection (Dec 2011 – Oct 2014):**

| Events per month vs | n | Same month Pearson / Spearman | Next month Pearson / Spearman |
|---|---|---|---|
| WB2 pressure | 33 | +0.19 / −0.01 | +0.36 / +0.27 |
| WB1 pressure | 23 | +0.17 / +0.18 | −0.09 / +0.03 |
| IBDP rate | 35 | +0.03 / −0.04 | +0.08 / +0.27 |
| shut-in columns in month | 35 | −0.15 / +0.09 | −0.13 / −0.13 |

**After injection (Dec 2014 – Mar 2017):** events per month against WB2 pressure, Pearson +0.61,
Spearman +0.60 (n = 23 months). Sample months:

| Month | WB2 (psi) | Events |
|---|---|---|
| Dec 2014 | 3236 | 55 |
| Mar 2015 | 3222 | 30 |
| Jun 2015 | 3222 | 3 |
| Sep 2015 | 3215 | 11 |
| Dec 2015 | 3204 | 7 |
| Mar 2016 | 3199 | 5 |
| Aug 2016 | 3200 | 3 |
| Feb 2017 | 3191 | 5 |

Both series fall over the same months, so part of this correlation is the shared trend.

**Shut-ins:**
- **Definition:** an episode is consecutive columns where the IBDP rate line dips below
  15 T/hr. There were 29 episodes, Dec 2011 – Nov 2014.
- **Median events/day:** 4.29 in the 14 days before, 3.00 during and 3.50 in the 14 days after.
- **Test against random windows:**
  - The during/before rate ratio is 0.73 at shut-ins.
  - For 2,000 sets of random windows of the same lengths during injection it is 0.99 (5–95%:
    0.75–1.28).
  - One-sided p = 0.041.
- **Sensitivity:** with thresholds of 10, 15 and 20 T/hr and baselines of 7, 14 and 28 days:
  - the ratio is below 1 in all 9 runs (0.65–0.95);
  - p ranges from 0.020 to 0.348;
  - 4 of the 9 runs have p < 0.05;
  - the effect is clearest with the looser 20 T/hr threshold.

**ICCS:** 74 located events in the 12 months before ICCS (Apr 2016 – Mar 2017). 108 in the first
12 months after it began (Jul 2017 – Jun 2018). The catalog ends 2 Jul 2018.

No magnitude-of-completeness cut was applied.
