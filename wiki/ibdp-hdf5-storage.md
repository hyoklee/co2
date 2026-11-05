# IBDP data in HDF5

How much smaller and faster the IBDP dataset would be if its array data were stored in
HDF5, measured on samples on Aurora (ALCF) on 2026-11-05. Methods, scripts and raw output:
[raw/2026-11-05-ibdp-hdf5-eval/](../raw/2026-11-05-ibdp-hdf5-eval/README.md).

## Summary

- **Storage:** about 113 GB unzipped becomes about 68 GB with lossless HDF5 (−40%).
  That is roughly the 67 GB of the zips, but HDF5 can be read in place while the zips
  must be unpacked first (about 17 minutes at the 0.11 GB/s measured here).
- **Depth slices** are 2.3–4.4× faster in HDF5.
- **Line reads** are slower than SEG-Y unless the chunk shape suits the access pattern;
  no chunk shape wins in every direction.
- **Many small files:** 5,399 SEG-2 files in one HDF5 file read 12–100× faster on Lustre.
- **Converting at ingest works:** a clio-core CAE `run:` step turned the 2.79 GB porosity
  volume into a 0.333 GB HDF5 file and stored that in the CTE.

## Storage

| Data | Raw | Lossless HDF5 (zstd) | Lossy HDF5 (ZFP) | Basis |
|---|---|---|---|---|
| SEG-Y, 6 files | 13.0 GB | 6.5 GB (−50%) | 3.2–3.8 GB | measured on 3 files |
| SEG-2, 5,399 files | 8.8 GB | 6.9 GB (−21%), one file | — | measured on 100 files |
| Petrel ZGY | 59.0 GB | ~21–23 GB (−62%) | not tested | estimate from zip ratio |
| Everything else | 32.5 GB | unchanged | — | already compressed or proprietary |
| **Total** | **113 GB** | **~68 GB (−40%)** | | |

Source: [README](../raw/2026-11-05-ibdp-hdf5-eval/README.md),
[h5eval_output.txt](../raw/2026-11-05-ibdp-hdf5-eval/h5eval_output.txt).

- **Volumes differ a lot.** Lossless zstd shrinks the PSTM amplitude volume to 72% and the
  porosity volume to 12%.
- **ZFP suits amplitudes, not smooth properties.** At about 90 dB SNR it takes PSTM to 36%
  (27% at 72 dB), but porosity only to 29%, worse than lossless.
- **Uncompressed HDF5 can be larger than SEG-Y** (125% for PSTM), because the survey fills
  77% of its grid and the gaps become padding. Compression removes it.
- **zstd over gzip:** same size (2.61 vs 2.65 GB for PSTM) but 8× faster to write
  (10.6 s vs 86 s) and 2–3× faster to read.

## Read speed

Seconds, best of 3, cache dropped. PSTM is 3.6 GB, porosity 2.8 GB; HDF5 is zstd with
64×64×64 chunks unless noted.

| Read | SEG-Y | HDF5 zstd | HDF5 uncompressed |
|---|---|---|---|
| Depth slice | 3.0 / 2.2 | 1.3 / 0.51 | 1.8 / 0.79 |
| Line in SEG-Y order | 0.07 / 0.08 | 1.4 / 0.9 | 0.02 / 0.02 |
| Line across that order | 0.005 / 0.003 | 0.53 / 0.14 | 0.03 / 0.06 |
| 100 SEG-2 files vs one HDF5 file | 4.3 | 0.14–0.35 | 0.04 |

Source: [h5eval_output.txt](../raw/2026-11-05-ibdp-hdf5-eval/h5eval_output.txt).

- SEG-Y stores trace by trace, so a depth slice reads the whole file; HDF5 reads only the
  chunks that hold it.
- SEG-Y samples are IBM floats converted on every read; HDF5 holds IEEE floats, which is
  why uncompressed HDF5 beats SEG-Y on lines.
- The SEG-2 time includes a Python parser, so 12–100× overstates the format difference.

### Chunk shape (zstd, PSTM)

| Chunks (inline × crossline × sample) | Size | Inline s | Crossline s | Depth slice s |
|---|---|---|---|---|
| SEG-Y as is | 3.64 GB | 0.073 | 0.005 | 3.05 |
| 64×64×64 | 2.61 GB | 1.47 | 0.42 | 1.39 |
| 8×256×64 | 2.61 GB | 0.30 | 1.19 | 1.89 |
| 16×16×1451 (whole traces) | 2.63 GB | 0.37 | 0.14 | 4.34 |
| 4×512×32 | 2.69 GB | 0.23 | 1.34 | 8.98 |
| 32×32×128 | 2.61 GB | 0.77 | 2.68 | 17.9 |

Source: [h5chunks_output.txt](../raw/2026-11-05-ibdp-hdf5-eval/h5chunks_output.txt).

- Chunk shape barely changes size for PSTM. For porosity, whole-trace chunks are smallest
  (0.27 GB, 10%) with the fastest lines (0.21 / 0.09 s) but slow depth slices (1.79 s).
- No shape beats SEG-Y on lines; pick 64³ or 8×256×64 for slice-heavy work, whole-trace
  chunks for trace and line work.

## Conversion at ingest (CAE `run:`)

clio-core CAE can run a script on a transfer's source before ingest
(https://github.com/iowarp/clio-core/pull/1332). On `Porosity-NN-Depth.sgy`
(PBS job 9040949, 6 of 6 checks passed):

| Ingest | Bytes in CTE | Time |
|---|---|---|
| SEG-Y as is | 2,789,140,368 (2,660 blobs) | 5 s |
| `run:` SEG-Y → HDF5, then ingest | 333,150,770 (318 blobs) | 65 s, 45 s of it conversion |

- The script read all 461,472 traces back and matched them to the SEG-Y before exiting 0.
- A depth slice took 1.22 s from the HDF5 file against 2.94 s from the SEG-Y.
- The file was ingested as bytes (`format: binary`), since that build had CAE's HDF5
  support off.

Source: [run-step/ibdp_run_output.txt](../raw/2026-11-05-ibdp-hdf5-eval/run-step/ibdp_run_output.txt).

## Caveats

- ZGY is half the dataset and untested; its figure uses the zip ratio as a stand-in.
- Two of the six SEG-Y volumes are estimated from their zip sizes, not measured.
- One node, one run of each job; Lustre load varies.

## Next steps

- Read the ZGY volumes (OpenZGY) and measure them.
- Rerun the `run:` test with `format: hdf5` on a build with CAE HDF5 support.
- Try whole-trace chunks with ZFP for the amplitude volumes.

Related: [[illinois-basin-decatur-project]], [[ibdp-injection-and-seismicity]].
