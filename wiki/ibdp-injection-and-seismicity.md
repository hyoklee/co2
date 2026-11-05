# IBDP injection history and seismicity

How much CO2 went in each month at the [[illinois-basin-decatur-project]], where that number
comes from, and a first look at whether earthquake counts follow it.

Sources:
- [raw/2026-11-04-ibdp-injection-notes.md](../raw/2026-11-04-ibdp-injection-notes.md)
- [raw/2026-11-04-ibdp-monthly-injection-digitized.csv](../raw/2026-11-04-ibdp-monthly-injection-digitized.csv)
- [raw/2026-11-05-ibdp-pressure-notes.md](../raw/2026-11-05-ibdp-pressure-notes.md)
- [raw/2026-11-05-ibdp-fig8-8-digitized.csv](../raw/2026-11-05-ibdp-fig8-8-digitized.csv)

## Injection record

- **Total:** 999,215 tonnes of CO2, injected from 17 Nov 2011 to 26 Nov 2014. The design rate was
  about 1,000 t/day, with breaks of hours to days.
- **Monthly values:** the dataset has no injection table. Monthly values exist only as a bar chart,
  Figure 8-1 of the final IBDP report (`_IBDP_Report_Final_07_July_2021_rev1.pdf`, PDF page 200).
  - Read off that chart, the 37 months add up to 997.1 kt, 0.2% below the stated total.
  - Most months were 25–31 kt. The extremes are 17.4 kt (Mar 2013) and 17.8 kt (Oct 2014), and
    35.5 kt (Dec 2013).
- **Daily rate and pressure:** Figure 8-8 (PDF page 212) plots the daily injection rate and the
  reservoir pressure at several depths. Both are now digitized, at about 3-day resolution; see
  the next section.
- **Second well:** Figure 8-8 also shows the follow-on project's well (ICCS, CCS2) starting to
  inject in about April 2017 and reaching about 2.08 Mt by late 2020, at a median of about
  1,380 t/day. Catalog events from 2017–18 can therefore come from either well.
- **Simulation model:** the deck in the Petrel model sets every rate to zero, so it holds no
  injection history.

## Earthquakes vs injection, first look

The event side is the ISGS catalog: 5,397 located events, Mw −2.1 to 1.2. Compared with the
monthly series (36 full months):

- **Same month:** essentially no correlation (Pearson +0.07). Injection was nearly constant, so
  there is little variation to explain.
- **One-month lag:** a weak positive link (Spearman +0.41 for all events, +0.37 for Mw ≥ 0).
  This fits pressure taking time to reach the faults, but is far from conclusive.
- **Running totals:** cumulative events against cumulative injected mass correlate at +0.99. This
  is mostly an artefact: any two series that both rise steadily over the same period correlate.
- **Rate per tonne:** about 6.0 events per kt in 2012, 3.2 in 2013 and 6.1 in 2014, at the same
  injection rate.
- **After injection:** 544 located events came after injection stopped (Dec 2014 – Jul 2018).

The last two points suggest that site conditions, such as basement faults and how pressure
spreads to them, matter more than the amount stored. That agrees with the published studies in
[[ibdp-publications]] (Luu et al. 2022; the MIT-led BSSA 2024 study).

## Pressure and shut-ins (Figure 8-8)

Read off Figure 8-8. The cumulative line peaks at 999 kt, which checks the reading. Dates are
good to about ±2 weeks.

- **Pressure build-up is fast and deep:**
  - At 6,946–7,061 ft (Westbay zones 1–3, nearest the injection interval), pressure rose about
    110 psi within roughly the first seven weeks: WB2 went from about 3230 to 3343 psi. It then
    stayed on a plateau near 3330 psi until injection ended.
  - Zones at 6,632–6,838 ft rose only 15–30 psi.
- **After injection:**
  - WB2 fell about 90 psi within four months, then drifted down to 3191 psi by Feb 2017.
  - Over the same time, events fell from 55 a month (Dec 2014) to 3–11 a month by mid-2015.
  - Across 23 months the two correlate (Spearman +0.60), but both fall over the same period, so
    part of that is the shared trend.
- **During injection, month by month:** pressure explains little.
  - Same month: Spearman about 0 for WB2.
  - One month later: Spearman +0.27.
  - The pressure plateau leaves little variation to work with, as with the monthly tonnage.
- **Shut-ins:**
  - There were 29 breaks in injection, where the rate line dips below 15 T/hr.
  - During a break, the event rate fell to a median 0.73 of the 14 days before. Random windows of
    the same lengths gave 0.99 (one-sided p = 0.04).
  - The drop appears with every threshold and baseline tried (ratio 0.65–0.95), but p ranges from
    0.02 to 0.35. Read it as suggestive, not established.
- **ICCS:**
  - Its pressure shows in the shallower VW1 gauges (6,418–6,430 ft, up about 110 psi over
    2017–2020), not at 6,935 ft.
  - Located events went from 74 in the 12 months before ICCS to 108 in its first 12 months.

**Together:** seismicity responds to pressure changes at the injection depth, both when injection
stops for good and, more weakly, during short breaks. It does not track the tonnage.

## Caveats

- **Detection changed** during the record (the catalog's "Trigger Changes" sheet). Raw counts are
  not comparable across the whole period until a magnitude-of-completeness cut is applied.
- **This is one site and one well** until 2017. Any relation found describes Decatur, not CO2
  storage in general.
- **Figure 8-8 is a chart, not data.**
  - Resolution is about 3 days, 0.65 psi and 2.7 T/hr.
  - The integrated rate comes out 10% under the total.
  - Overlapping markers can be mis-assigned, although series are masked to the periods where the
    chart shows them.

## Next steps

1. Ask ISGS or CO2DataShare for the underlying daily rate and pressure tables. The digitized
   series are a stopgap.
2. Find the magnitude above which detection is complete, and fit the Gutenberg–Richter b-value.
3. Fit a seismogenic index: the probability of exceeding magnitude M per volume injected, for this
   site.
4. Repeat with the double-difference relocated subset, splitting events by fault cluster.
5. Fit a pressure-driven rate model, such as the rate-and-state model of Luu et al. 2022, to the
   digitized WB1–WB2 pressure, and check it against the post-injection decay and the shut-ins.

Related: [[illinois-basin-decatur-project]], [[ibdp-publications]].
