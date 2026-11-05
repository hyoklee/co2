#!/bin/sh
# CAE OMNI run: step: SEG-Y -> HDF5.  $1 = SEG-Y path, $2 = HDF5 file to write.
exec /home/hyoklee/miniconda3/envs/miv/bin/python -I -c "import sys; sys.path.insert(0, '/lus/flare/projects/IOWarp/hyoklee/h5eval/tools/pylib'); sys.argv = sys.argv[1:]; exec(open(sys.argv[0]).read())" /lus/flare/projects/IOWarp/hyoklee/h5eval/tools/sgy2h5.py "$1" "$2"
