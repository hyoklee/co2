# Illinois Basin – Decatur Project (IBDP)

A carbon capture and storage demonstration at ADM's corn-processing plant in Decatur,
Illinois. It was run by the Midwest Geological Sequestration Consortium (MGSC), led by the
Illinois State Geological Survey (ISGS), with Schlumberger Carbon Services and ADM.
About 1 million tonnes of supercritical CO2 went into the base of the Mt. Simon Sandstone, a
saline sandstone about 500 m thick, from November 2011 to November 2014.
Source: [raw/2026-11-04-ibdp-web-search.md](../raw/2026-11-04-ibdp-web-search.md).
The final IBDP report gives the exact total: 999,215 tonnes, injected from 17 Nov 2011 to
26 Nov 2014. See [[ibdp-injection-and-seismicity]] for the monthly record.

The injection caused microearthquakes, mostly small (about Mw −2 to 1) and mostly in the
basement below the reservoir. See [[ibdp-publications]] for the studies.

## The dataset

- Published on CO2DataShare as the "Illinois Basin – Decatur Project dataset",
  DOI 10.11582/2022.00017:
  https://co2datashare.org/dataset/illinois-basin-decatur-project-dataset
- 8 ZIP files, 67,516,839,498 bytes zipped and about 113 GB unzipped.
- **Licence:** IBDP CO2 Injection Datasets License, which is CC BY 4.0 except that the
  data may not be sold.
  - Credit: ISGS, IBDP CO2 Injection Monitoring Data, April 30, 2021; MGSC Phase III Data
    Sets; DOE Cooperative Agreement No. DE-FC26-05NT42588.
- **Download access:** no account is needed. The download form asks for a country and an
  affiliation and turns them into query parameters on the file URL; without them the site
  answers HTTP 400.

Each ZIP is a BagIt bag with SHA-256 and SHA-512 manifests for every file.
Sizes below are unzipped. Source:
[raw/2026-11-04-ibdp-archive-inventory.txt](../raw/2026-11-04-ibdp-archive-inventory.txt).

| Archive | Unzipped | Main contents |
|---|---|---|
| `ibdp_final_petrel_static_model_2021.zip` | 76.0 GB | 59 GB of ZGY seismic and attribute volumes, a Petrel project (`.ptd`, about 10 GB), property grids, 2 Eclipse/Intersect restart files (`.unrst`) |
| `ibdp_seismic.zip` | 22.0 GB | 13 GB of SEG-Y (6 files), 8.8 GB of borehole geophone data (`.sg2`, 5,399 files), 2,472 SAC waveforms, SEED station metadata |
| `ibdp_gis_data_and_georeferenced_imagery.zip` | 13.5 GB | 5.4 GB of GeoTIFF imagery with overviews, GIS layers |
| `ibdp_well_information.zip` | 1.1 GB | LAS logs for 12 wells, 23 PDF well reports, an Excel table |
| `ibdp_selected_reports.zip` | 372 MB | 28 PDF reports |
| `ibdp_reports.zip` | 307 MB | 24 PDF reports, figures |
| `ibdp_horizons-faults_petrel_2021.zip` | 19 MB | 40 GOCAD `.ts` surfaces (horizons and faults) |
| `seismic-event-catalog.zip` | 12 MB | ISGS microseismic event catalog, 17 Nov 2011 – 2 Jul 2018: 19,579 detected and 5,397 located events, Mw −2.1 to 1.2 (2 Excel files and a `.rdv` file) |

## Copy on Aurora (ALCF)

- **Location:** all 8 ZIPs are in `/lus/flare/projects/IOWarp/hyoklee/co2datashare/ibdp/`.
- **How it was made:** clio-core CAE downloaded them on 2026-11-04 (PBS job 9039039).
  - The run used an OMNI file, `aurora/omni/ibdp_co2datashare.omni.yaml`, and CAE's new
    http(s) source (https://github.com/iowarp/clio-core/pull/1331).
  - The country and affiliation were read from `~/.clio/cae_http_auth.ini`.
- **Checks:** every file matched CKAN's size, and every ZIP member passed its CRC test.
  The BagIt SHA-256 manifests have not been checked yet.
  Source: [raw/2026-11-04-ibdp-archive-inventory.txt](../raw/2026-11-04-ibdp-archive-inventory.txt).

## What it could be used for

These are ideas, not results.

- **Open formats.** Convert SEG-Y, SAC, LAS and the event catalog to HDF5 so the data can
  be used without commercial software.
  - ZGY and Petrel `.ptd` files need OpenZGY or Petrel.
  - SEG-Y, LAS and SAC can be read with open tools such as segyio, lasio and ObsPy.
  - Measured savings and read speeds for SEG-Y and SEG-2 in HDF5 are in [[ibdp-hdf5-storage]].
- **I/O benchmark.** Have CAE read SEG-Y traces and waveforms into CTE blobs. About
  100 GB of real data makes a test case for I/O and compression.
- **Seismicity analysis.** Relate the event catalog to injection in time and depth, or
  re-detect events in the continuous borehole data. Others have done this with ML
  (see [[ibdp-publications]]). A first comparison of monthly injection with event counts is
  in [[ibdp-injection-and-seismicity]].
- **Reservoir and geomechanics.** The static model, wells and fault surfaces are the inputs
  to coupled flow and fault-stress models such as Luu et al. (2022).
- **Integrity check.** Verify every file against its BagIt SHA-256 manifest.

Related: [[ibdp-publications]], [[ibdp-injection-and-seismicity]], [[ibdp-hdf5-storage]].
