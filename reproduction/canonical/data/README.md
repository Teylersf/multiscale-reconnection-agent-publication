# Numeric fixtures and attribution

The two small archives support the positive proxy-curve reconstruction in
experiments/verify_proxy_curves.py. Both contain only numeric NumPy arrays
and are opened with allow_pickle=False. No original figure PDF or bitmap
is redistributed here.

upstream.npz contains selected processed arrays and the global-energy
table from Alexander Velberg's associated OSF project,
[DOI 10.17605/OSF.IO/EPWTU](https://doi.org/10.17605/OSF.IO/EPWTU).
The deposited data are CC0 1.0. Exact public download/API URLs, file versions,
modification dates and upstream hashes are recorded in
proxy-reconstruction-provenance.json.

published-vector-coordinates.npz contains numerical point coordinates
extracted from the line paths in Figs. 3 and 4 of A. Velberg et al.,
“Effects of Multi-scale Coupling on Particle Acceleration and Energy
Partition in Magnetic Reconnection,”
[arXiv:2511.15988v1](https://arxiv.org/abs/2511.15988v1), 2025,
CC BY 4.0. The coordinates are an attributed numerical extraction,
separate from the CC0 data. Source-member hashes, axis calibration,
extraction indexing and the rounding tolerance accompany the fixtures.

The current OSF README is dated July 20, 2026 and has different figure
numbering from the audited November 2025 preprint. The successful numeric
mapping is recorded explicitly; it does not prove the revision of the
historical plotting program or complete simulation-run identity.

The OSF project's CC0 designation does not displace independently
applicable upstream software licenses. Auxiliary input/postprocessing
code is cited in the provenance manifest and is not redistributed in
these numeric fixtures.
