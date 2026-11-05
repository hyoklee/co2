Scripts behind ../2026-11-04-ibdp-injection-notes.md. They need Python with numpy and Pillow.

- `digitize.py <chart.png>`: reads the monthly bars off Figure 8-1's embedded image. Extract
  the image with `pdfimages -f 200 -l 200 -png _IBDP_Report_Final_07_July_2021_rev1.pdf out`;
  it is the 961x605 image. The script writes a plain CSV to stdout.
- `corr.py <plain.csv> <20180702.rdv>`: monthly located-event counts against injection.
  Give it the plain CSV from `digitize.py`, not the commented copy in `raw/`; or strip that
  copy's `#` lines first, with `grep -v '^#'`.
- `corr_output.txt`: the output of the run that the notes quote.
