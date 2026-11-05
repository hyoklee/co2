"""Pack SEG-2 event files into one HDF5 file; compare size and open/read time.

Usage: python -I sg2eval.py <dir with .sg2 files> <out.h5>
"""
import glob
import os
import struct
import sys
import time

import h5py
import hdf5plugin
import numpy as np

DT = {1: "i2", 2: "i4", 4: "f4", 5: "f8"}


def drop_cache(path):
  fd = os.open(path, os.O_RDONLY)
  os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
  os.close(fd)


def read_sg2(path):
  b = open(path, "rb").read()
  bo = "<" if b[0:2] == b"\x55\x3a" else ">"
  ptr_size, ntr = struct.unpack(bo + "HH", b[4:8])
  ptrs = struct.unpack(bo + "%dI" % ntr, b[32:32 + 4 * ntr])
  tr = []
  for p in ptrs:
    blk, = struct.unpack(bo + "H", b[p + 2:p + 4])
    nbytes, ns = struct.unpack(bo + "II", b[p + 4:p + 12])
    code = b[p + 12]
    if code not in DT:
      raise ValueError(f"{path}: data format code {code}")
    tr.append(np.frombuffer(b, dtype=bo + DT[code], count=ns, offset=p + blk))
  return np.stack(tr)


files = sorted(glob.glob(os.path.join(sys.argv[1], "*.sg2")))
tot = sum(os.path.getsize(f) for f in files)
for f in files:
  drop_cache(f)
t = time.perf_counter()
ev = [read_sg2(f) for f in files]
t_sg2 = time.perf_counter() - t
shapes = {e.shape for e in ev}
dtypes = {e.dtype.str for e in ev}
print(f"{len(files)} SEG-2 files, {tot/1e6:.1f} MB; shapes {sorted(shapes)[:4]}; dtypes {dtypes}")
print(f"read all ({len(files)} opens) with Python parser: {t_sg2:.2f} s")
out = sys.argv[2]
for name, kw in (("none", {}), ("gzip4+shuffle", dict(compression="gzip", compression_opts=4, shuffle=True)),
                 ("zstd3+shuffle", dict(**hdf5plugin.Zstd(clevel=3), shuffle=True)),
                 ("blosc-zstd+bitshuffle", dict(**hdf5plugin.Blosc(cname="zstd", clevel=5, shuffle=hdf5plugin.Blosc.BITSHUFFLE)))):
  if os.path.exists(out):
    os.remove(out)
  with h5py.File(out, "w") as h:
    for f, e in zip(files, ev):
      h.create_dataset(os.path.basename(f)[:-4], data=e,
                       chunks=e.shape if kw else None, **kw)
  sz = os.path.getsize(out)
  drop_cache(out)
  t = time.perf_counter()
  with h5py.File(out, "r") as h:
    for k in h:
      h[k][...]
  t_h5 = time.perf_counter() - t
  print(f"HDF5 {name:22s} {sz/1e6:7.1f} MB ({sz/tot:.0%} of SEG-2), read all {t_h5:.2f} s")
