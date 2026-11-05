# Notes: IBDP injection data in the CO2DataShare reports, and a first comparison with the event catalog

Made 2026-11-04 from the copy of the dataset on Aurora
(`/lus/flare/projects/IOWarp/hyoklee/co2datashare/ibdp/`).

## Where the injection data is

- I extracted the text of all 73 PDFs in `ibdp_reports.zip`, `ibdp_selected_reports.zip` and
  `ibdp_well_information.zip` with `pdftotext` and searched it for injection rates, cumulative
  injection and tonnage.
- The only injection history is in the final report, `_IBDP_Report_Final_07_July_2021_rev1.pdf`
  (in `ibdp_reports.zip`, 461 pages).
  - §8.1, quoted: "CO2 was injected on a consistent basis from November 17, 2011 (start of
    injection) through November 26, 2014, with a total injection of 999,215 tonnes of CO2."
  - Elsewhere the report gives a design rate of "approximately 1,000 tonnes per day". Breaks
    in injection "ranged from several hours to several days" (maintenance, annual well tests,
    logs, equipment problems, weather).
  - **Figure 8-1**, "Cumulative injection record for the IBDP" (PDF page 200, printed 165): a
    bar chart of monthly injected CO2 in kt, with percent of injection completed.
  - **Figure 8-8**, "Pressure monitored in VW1 zones and CO2 injection history" (PDF page 212,
    printed 177), shows:
    - pressures in Westbay zones 1–6 and VW1 gauges G1–G3;
    - IBDP cumulative injected mass;
    - "IBDP 1000 x Daily Ave INJ Q, T/hr" and "ICCS 1000 x Daily Ave INJ Q, T/hr";
    - a "Start of ICCS Injection" label at about April 2017, with cumulative mass reaching
      about 2.1 million tonnes by late 2020.
- None of these is a table. Both are images.
- The reservoir simulation deck in `ibdp_final_petrel_static_model_2021.zip`
  (`IBDP_2021.sim/HM_PRESSURE_RST-FXLR-ES-TLSEIS/MASTER_SCH.INC`) sets the CCS1, WB1 and WB2
  injection rates to 0.00 at a single date, 2 Nov 2011. It holds no injection history.

## Digitized monthly series

- File: [2026-11-04-ibdp-monthly-injection-digitized.csv](2026-11-04-ibdp-monthly-injection-digitized.csv)
- Source: Figure 8-1's embedded 961×605 image (`pdfimages -f 200 -l 200 -png`).
- Method: [digitize.py](2026-11-04-ibdp-injection-scripts/digitize.py) walks each bar up from
  the axis, letting the red line cross it. Calibration is 0 kt at pixel row 506 and 50 kt at row
  39.5, so 1 px ≈ 0.11 kt.
- Result: 37 bars, Nov 2011 – Nov 2014, adding up to **997.1 kt**. That is 0.2% below the stated
  999,215 t, which checks the reading.

## Event catalog facts used

From `seismic-event-catalog.zip`, `20180702.rdv`; split the columns on whitespace, since the file
mixes tabs and spaces.
- **Coverage:** 5,397 located events, from 15 Dec 2011 to 2 Jul 2018. The README says recording
  ran from the start of injection, 17 Nov 2011, to 2 Jul 2018.
- **Magnitudes:** Mw −2.13 to 1.17; the largest was on 29 Jul 2012. 350 events are Mw ≥ 0 and
  6 are Mw ≥ 1.
- **Other files:**
  - `EventRates20180702.xlsx` has 19,579 detected events in sheet "All", and a
    "Trigger Changes" sheet: detection settings changed during the record.
  - `DD_relocations_catalogue_20200428_regionletters_95pcnt_confidence.xlsx` is the
    double-difference relocated subset (Dando et al. 2021, GJI 227(2), doi:10.1093/GJI/GGAB255).

## First comparison

From [corr.py](2026-11-04-ibdp-injection-scripts/corr.py); full output in
[corr_output.txt](2026-11-04-ibdp-injection-scripts/corr_output.txt). It uses the 36 full months
(Nov 2011 left out) and counts located events per calendar month.

| Comparison | Pearson | Spearman |
|---|---|---|
| events/month vs injected that month | +0.07 | −0.04 |
| events/month vs previous month's injection | +0.27 | +0.41 |
| Mw ≥ 0 events, same month | +0.14 | +0.13 |
| Mw ≥ 0 events, 1-month lag | +0.10 | +0.37 |
| cumulative events vs cumulative injected | +0.99 | — |

| Year | Injected (kt) | Located events | Events per kt |
|---|---|---|---|
| 2012 | 326.5 | 1,949 | 6.0 |
| 2013 | 334.7 | 1,064 | 3.2 |
| 2014 | 302.0 | 1,838 | 6.1 |

- During the injection months there were 4,853 located events.
- After injection ended (Dec 2014 – Jul 2018) there were 544.

No magnitude-of-completeness cut was applied, so the counts mix in the effect of detection changes.
