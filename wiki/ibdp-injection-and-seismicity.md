# IBDP injection history and seismicity

How much CO2 went in each month at the [[illinois-basin-decatur-project]], where that number
comes from, and a first look at whether earthquake counts follow it.

Sources:
- [raw/2026-11-04-ibdp-injection-notes.md](../raw/2026-11-04-ibdp-injection-notes.md)
- [raw/2026-11-04-ibdp-monthly-injection-digitized.csv](../raw/2026-11-04-ibdp-monthly-injection-digitized.csv)

## Injection record

- **Total:** 999,215 tonnes of CO2, injected from 17 Nov 2011 to 26 Nov 2014. The design rate was
  about 1,000 t/day, with breaks of hours to days.
- **Monthly values:** the dataset has no injection table. Monthly values exist only as a bar chart,
  Figure 8-1 of the final IBDP report (`_IBDP_Report_Final_07_July_2021_rev1.pdf`, PDF page 200).
  - Read off that chart, the 37 months add up to 997.1 kt, 0.2% below the stated total.
  - Most months were 25–31 kt. The extremes are 17.4 kt (Mar 2013) and 17.8 kt (Oct 2014), and
    35.5 kt (Dec 2013).
- **Daily rate and pressure:** Figure 8-8 (PDF page 212) plots the daily injection rate and the
  reservoir pressure at several depths. Neither has been digitized yet.
- **Second well:** Figure 8-8 also shows the follow-on project's well (ICCS, CCS2) starting to
  inject in about April 2017 and reaching about 2.1 Mt by late 2020. Catalog events from 2017–18
  can therefore come from either well.
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

## Caveats

- **Detection changed** during the record (the catalog's "Trigger Changes" sheet). Raw counts are
  not comparable across the whole period until a magnitude-of-completeness cut is applied.
- **This is one site and one well** until 2017. Any relation found describes Decatur, not CO2
  storage in general.
- **Monthly totals are coarse** next to the daily rate and pressure in Figure 8-8.

## Next steps

1. Digitize Figure 8-8: daily rate, and pressure at the Westbay and VW1 gauges.
2. Find the magnitude above which detection is complete, and fit the Gutenberg–Richter b-value.
3. Fit a seismogenic index: the probability of exceeding magnitude M per volume injected, for this
   site.
4. Repeat with the double-difference relocated subset, splitting events by fault cluster.

Related: [[illinois-basin-decatur-project]], [[ibdp-publications]].
