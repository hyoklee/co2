# IBDP data in HDF5: storage and read-speed evaluation (2026-11-05)

Notes on what was measured, how, and how the whole-dataset estimate was built.
All runs on Aurora (ALCF) compute nodes against the copy in
`/lus/flare/projects/IOWarp/hyoklee/co2datashare/ibdp/` (unzipped samples under
`/lus/flare/projects/IOWarp/hyoklee/h5eval/`).

## Tools

- h5py 3.16 / HDF5 2.0.0 / hdf5plugin 7.1.0 (zstd, Blosc, ZFP filters).
- SEG-Y samples are IBM floats (format 1), converted to IEEE float32 for HDF5.
- Header bytes: PSTM-grid volumes inline at byte 17, crossline at 25; VSP inline 9, crossline 13.
- The page cache was dropped (`posix_fadvise DONTNEED`) before every timed read; best of 3.

## Files

| File | What |
|---|---|
| `h5eval.py`, `sg2eval.py`, `h5eval.pbs` | Filter comparison on 3 SEG-Y volumes and 100 SEG-2 files (PBS job 9040863) |
| `h5eval_output.txt` | Its output |
| `h5chunks.py`, `h5chunks.pbs` | Chunk-shape sweep, zstd level 3 + shuffle |
| `h5chunks_output.txt` | Its output |
| `run-step/` | SEG-Y -> HDF5 as a clio-core CAE OMNI `run:` step (PBS job 9040949) |

Read columns: "inline s" reads one line in SEG-Y storage order, "xline s" one line across
it, "z-slice s" one sample from every trace (a depth slice).

## Whole-dataset estimate

Raw sizes are the uncompressed member sizes in
[2026-11-04-ibdp-archive-inventory.txt](../2026-11-04-ibdp-archive-inventory.txt):
113 GB in all, of which ZGY 59.0 GB, SEG-Y 13.0 GB (6 files), SEG-2 8.8 GB (5,399 files).

| Data | Raw | Lossless HDF5 (zstd) | Lossy (ZFP) | Basis |
|---|---|---|---|---|
| SEG-Y | 13.0 GB | 6.5 GB | 3.2–3.8 GB | 3 of 6 files measured; phase-shifted PSTM assumed equal to PSTM (identical zip size); impedance assumed equal to its zip size, as porosity was |
| SEG-2 | 8.8 GB | 6.9 GB in one file | — | 100 files measured (zstd 79% of raw), scaled |
| ZGY | 59.0 GB | ~21–23 GB | not tested | no ZGY reader on Aurora; zip ratio used as a stand-in (on SEG-Y, zstd came out 0.85–0.96 x the zip size) |
| Everything else | 32.5 GB | unchanged | — | GIS rasters and PDFs already compressed; Petrel project files proprietary |
| Total | 113 GB | ~68 GB | | about the 67 GB of the zips |

The ZGY volumes are not duplicates: several share a size but all CRCs differ.

## Run step test (`run-step/`)

`sgy2h5.py` converts one 3-D post-stack SEG-Y to HDF5 (`/volume` float32
[inline, crossline, sample] with NaN where there is no trace, `/live`, `/trace_headers`,
`/inline`, `/crossline`, text and binary headers as attributes; gzip 4 + shuffle,
chunks 8x256x64) and reads every trace back before exiting 0. `ibdp_run.pbs` ingests
`Porosity-NN-Depth.sgy` once as is and once through the `run:` step, with clio-core
branch `feat/cae-omni-run` (https://github.com/iowarp/clio-core/pull/1332).
Result in `run-step/ibdp_run_output.txt`.
