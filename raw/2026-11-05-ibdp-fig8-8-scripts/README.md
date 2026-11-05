Scripts behind ../2026-11-05-ibdp-pressure-notes.md. They need Python with numpy and Pillow.

- `digitize_f88.py <img.png> <out.csv>`: reads every series off Figure 8-8 of the final IBDP
  report. Extract the image with
  `pdfimages -f 212 -l 212 -png _IBDP_Report_Final_07_July_2021_rev1.pdf out`; use the
  1422x1033 image (`out-000.png`), not its mask. The calibration is in the docstring.
- `corr_f88.py <out.csv> <20180702.rdv>`: compares the series with the event catalog. Give it
  the plain CSV from `digitize_f88.py`, or strip the `#` lines from the copy in `raw/` first
  (`grep -v '^#'`). The shut-in tests use a fixed random seed, so reruns give the same numbers.
- `corr_f88_output.txt`: the output of the run that the notes quote.
