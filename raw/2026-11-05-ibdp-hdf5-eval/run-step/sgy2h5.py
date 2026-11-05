"""SEG-Y (IBM float, 3D post-stack) -> HDF5, for use as a CAE OMNI `run:` step.

Usage: python -I sgy2h5.py <in.sgy> <out.h5>
Env:   SGY_IL_BYTE / SGY_XL_BYTE  1-based trace-header bytes of inline/crossline
                                  (default 17 / 25, as in the IBDP PSTM-grid text header)
       SGY_CHUNKS                 chunk shape il,xl,z (default 8,256,64)

Writes, gzip level 4 + shuffle (built into every HDF5, no filter plugin needed):
  /volume            float32 [inline, crossline, sample]; grid cells with no trace are NaN
  /live              uint8 [inline, crossline]; 1 where the SEG-Y has a trace
  /trace_headers     uint8 [trace, 240], the SEG-Y trace headers in file order
  /inline, /crossline  int32 [trace], each trace's grid position
  attributes: the 3200-byte text header (decoded from EBCDIC), the 400-byte binary
  header, sample interval and count, inline/crossline origin, source file name.

Before exiting 0 it reads every trace back from the HDF5 file and compares it with
the SEG-Y sample values, so a bad conversion fails the run step and is never ingested.
"""
import os
import sys
import time

import h5py
import numpy as np


def ibm2ieee(u):
  u = u.astype(np.uint32)
  sign = np.where(u >> 31, -1.0, 1.0)
  exp = ((u >> 24) & 0x7F).astype(np.int32) - 64
  frac = (u & 0x00FFFFFF).astype(np.float64) / float(1 << 24)
  return (sign * frac * np.power(16.0, exp)).astype(np.float32)


def main(src, out):
  t0 = time.perf_counter()
  ilb = int(os.environ.get("SGY_IL_BYTE", "17"))
  xlb = int(os.environ.get("SGY_XL_BYTE", "25"))
  chunks = tuple(int(c) for c in os.environ.get("SGY_CHUNKS", "8,256,64").split(","))
  with open(src, "rb") as f:
    text = f.read(3200)
    binh = f.read(400)
  ns = int.from_bytes(binh[20:22], "big")
  dt_us = int.from_bytes(binh[16:18], "big")
  fmt = int.from_bytes(binh[24:26], "big")
  if fmt != 1:
    sys.exit(f"sgy2h5: sample format {fmt} is not IBM float (1)")
  tb = 240 + 4 * ns
  nt = (os.path.getsize(src) - 3600) // tb
  raw = np.fromfile(src, dtype=np.uint8, offset=3600, count=nt * tb).reshape(nt, tb)
  hdr = raw[:, :240].copy()
  il = hdr[:, ilb - 1:ilb + 3].copy().view(">i4").ravel().astype(np.int32)
  xl = hdr[:, xlb - 1:xlb + 3].copy().view(">i4").ravel().astype(np.int32)
  data = ibm2ieee(raw[:, 240:].copy().view(">u4"))
  del raw
  il0, xl0 = int(il.min()), int(xl.min())
  ni, nx = int(il.max()) - il0 + 1, int(xl.max()) - xl0 + 1
  ii, xx = il - il0, xl - xl0
  if len(set(zip(ii.tolist(), xx.tolist()))) != nt:
    sys.exit("sgy2h5: two traces share a grid cell; check SGY_IL_BYTE/SGY_XL_BYTE")
  cube = np.full((ni, nx, ns), np.nan, np.float32)
  cube[ii, xx] = data
  live = np.zeros((ni, nx), np.uint8)
  live[ii, xx] = 1
  chunks = tuple(min(c, n) for c, n in zip(chunks, cube.shape))
  gz = dict(compression="gzip", compression_opts=4, shuffle=True)
  tmp = out + ".tmp"
  with h5py.File(tmp, "w") as h:
    v = h.create_dataset("volume", data=cube, chunks=chunks, fillvalue=np.nan, **gz)
    v.dims[0].label, v.dims[1].label, v.dims[2].label = "inline", "crossline", "sample"
    h.create_dataset("live", data=live, chunks=True, **gz)
    h.create_dataset("trace_headers", data=hdr, chunks=(min(nt, 4096), 240), **gz)
    h.create_dataset("inline", data=il, chunks=True, **gz)
    h.create_dataset("crossline", data=xl, chunks=True, **gz)
    h.attrs["source_file"] = os.path.basename(src)
    h.attrs["segy_text_header"] = text.decode("cp500", errors="replace")
    h.attrs["segy_binary_header"] = np.frombuffer(binh, np.uint8)
    h.attrs["sample_interval_us"] = dt_us
    h.attrs["samples_per_trace"] = ns
    h.attrs["inline_origin"] = il0
    h.attrs["crossline_origin"] = xl0
    h.attrs["inline_byte"] = ilb
    h.attrs["crossline_byte"] = xlb
  t_write = time.perf_counter() - t0
  # Verify: every trace, read back from the file, equals the SEG-Y samples.
  with h5py.File(tmp, "r") as h:
    back = h["volume"][...]
  got = back[ii, xx]
  if not np.array_equal(got, data):
    bad = int(np.count_nonzero(np.any(got != data, axis=1)))
    os.remove(tmp)
    sys.exit(f"sgy2h5: verification failed, {bad} trace(s) differ")
  if np.count_nonzero(~np.isnan(back)) != data.size - np.count_nonzero(np.isnan(data)):
    os.remove(tmp)
    sys.exit("sgy2h5: verification failed, values outside the live traces")
  os.replace(tmp, out)
  print(f"sgy2h5: {os.path.basename(src)} {os.path.getsize(src)/1e9:.2f} GB -> "
        f"{os.path.basename(out)} {os.path.getsize(out)/1e9:.3f} GB "
        f"({os.path.getsize(src)/os.path.getsize(out):.1f}x); {nt} traces on a "
        f"{ni} x {nx} x {ns} grid, chunks {chunks}; converted in {t_write:.0f} s, "
        f"all {nt} traces verified", flush=True)


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
