"""Chunk-shape sweep: one IBM-float SEG-Y volume to HDF5 (zstd3+shuffle) with several chunk shapes.

Usage: python -I h5eval.py <in.sgy> <outdir> <il_byte> <xl_byte>
  il_byte/xl_byte: 1-based trace-header byte positions of the inline/crossline ints.
"""
import os
import sys
import time

import h5py
import hdf5plugin
import numpy as np


def ibm2ieee(u):
  """IBM System/360 single precision (big-endian uint32) to float32."""
  u = u.astype(np.uint32)
  sign = np.where(u >> 31, -1.0, 1.0)
  exp = ((u >> 24) & 0x7F).astype(np.int32) - 64
  frac = (u & 0x00FFFFFF).astype(np.float64) / float(1 << 24)
  return (sign * frac * np.power(16.0, exp)).astype(np.float32)


def drop_cache(path):
  fd = os.open(path, os.O_RDONLY)
  try:
    os.fsync(fd)
  except OSError:
    pass
  os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
  os.close(fd)


def timed(fn, path, reps=3):
  best = 1e9
  for _ in range(reps):
    drop_cache(path)
    t = time.perf_counter()
    fn()
    best = min(best, time.perf_counter() - t)
  return best


src, out, ilb, xlb = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(out, exist_ok=True)
with open(src, "rb") as f:
  head = f.read(3600)
ns = int.from_bytes(head[3220:3222], "big")
tb = 240 + 4 * ns
size = os.path.getsize(src)
nt = (size - 3600) // tb

drop_cache(src)
t = time.perf_counter()
raw = np.fromfile(src, dtype=np.uint8, offset=3600, count=nt * tb).reshape(nt, tb)
t_read = time.perf_counter() - t
hdr = raw[:, :240]
il = hdr[:, ilb - 1:ilb + 3].copy().view(">i4").ravel()
xl = hdr[:, xlb - 1:xlb + 3].copy().view(">i4").ravel()
data = ibm2ieee(raw[:, 240:].copy().view(">u4"))
del raw
il0, xl0 = il.min(), xl.min()
ni, nx = il.max() - il0 + 1, xl.max() - xl0 + 1
cube = np.zeros((ni, nx, ns), np.float32)
cube[il - il0, xl - xl0] = data
fill = nt / (ni * nx)
print(f"{os.path.basename(src)}: {size/1e9:.2f} GB, {nt} traces x {ns} samples; grid "
      f"{ni} x {nx} ({fill:.0%} filled); sequential read {size/1e9/t_read:.2f} GB/s")
nz = data[data != 0]
print(f"  values: min {data.min():.4g} max {data.max():.4g} std {nz.std():.4g}; "
      f"zeros {1 - nz.size/data.size:.1%}")
std = float(nz.std()) if nz.size else 1.0
del data

CHUNKS = [(64, 64, 64), (8, 256, 64), (16, 64, 64), (32, 32, 128), (16, 16, 1451), (4, 512, 32)]
variants = {"zstd3+shuffle %s" % "x".join(map(str, c)): dict(chunks=tuple(min(a, b) for a, b in zip(c, cube.shape)), **hdf5plugin.Zstd(clevel=3), shuffle=True) for c in CHUNKS}
mi, mx, mz = ni // 2, nx // 2, ns // 2


# SEG-Y access patterns via memmap (best case: regular, sorted trace layout).
def segy_trace_index(i, j):
  return np.nonzero((il == il0 + i) & (xl == xl0 + j))[0]


order = np.lexsort((xl, il))
sorted_by_il = np.all(np.diff(order) >= 0)
mm = np.memmap(src, dtype=np.uint8, mode="r", offset=3600, shape=(nt, tb))
idx_inline = np.nonzero(il == il0 + mi)[0]
idx_xline = np.nonzero(xl == xl0 + mx)[0]


def segy_inline():
  ibm2ieee(np.asarray(mm[idx_inline, 240:]).copy().view(">u4"))


def segy_xline():
  ibm2ieee(np.asarray(mm[idx_xline, 240:]).copy().view(">u4"))


def segy_zslice():
  # One sample per trace: SEG-Y has to be read end to end. A single sequential read
  # is the fastest way to do that (memmap page faults on Lustre are far slower).
  b = np.fromfile(src, dtype=np.uint8, offset=3600, count=nt * tb).reshape(nt, tb)
  off = 240 + 4 * mz
  ibm2ieee(b[:, off:off + 4].copy().view(">u4"))


print(f"  traces sorted by inline: {sorted_by_il}")
res = [("SEG-Y (as is)", size, None,
        timed(segy_inline, src), timed(segy_xline, src), timed(segy_zslice, src, reps=1))]

for name, kw in variants.items():
  path = os.path.join(out, name.replace("+", "_").replace(" ", "_") + ".h5")
  t = time.perf_counter()
  with h5py.File(path, "w") as h:
    h.create_dataset("amplitude", data=cube, **kw)
    h.create_dataset("trace_headers", data=hdr, chunks=True, compression="gzip",
                     compression_opts=4, shuffle=True)
  t_w = time.perf_counter() - t
  fsz = os.path.getsize(path)
  err = ""
  if "zfp" in name:
    with h5py.File(path, "r") as h:
      back = h["amplitude"][...]
    d = back - cube
    err = (f"max err {np.abs(d).max()/std:.2e} std, "
           f"SNR {10*np.log10((cube**2).mean()/max((d**2).mean(), 1e-30)):.0f} dB")
    del back, d

  def rd(sel):
    def f():
      with h5py.File(path, "r") as h:
        h["amplitude"][sel]
    return f
  res.append((name, fsz, t_w,
              timed(rd(np.s_[mi, :, :]), path), timed(rd(np.s_[:, mx, :]), path),
              timed(rd(np.s_[:, :, mz]), path)))
  print(f"  wrote {name}: {fsz/1e9:.2f} GB in {t_w:.1f} s {err}")

print(f"\n  {'format':30s} {'size GB':>8s} {'vs SEG-Y':>8s} {'inline s':>9s} "
      f"{'xline s':>8s} {'z-slice s':>9s}")
for name, fsz, t_w, a, b, c in res:
  print(f"  {name:30s} {fsz/1e9:8.2f} {fsz/size:8.0%} {a:9.3f} {b:8.3f} {c:9.3f}")
