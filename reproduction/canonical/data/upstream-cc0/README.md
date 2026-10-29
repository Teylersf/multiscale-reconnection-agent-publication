# Pinned upstream evidence for the particle-attribution check

These files derive from Alexander Velberg's author-associated OSF project,
*Effects of Multi-scale Coupling on Particle Acceleration and Energy Partition
in Magnetic Reconnection*, DOI https://doi.org/10.17605/OSF.IO/EPWTU . The project
declares **CC0 1.0 Universal**. Attribution and exact source URLs, file IDs,
version-1 dates, original checksums and transformations are recorded in
[provenance.json](provenance.json).

- `trajectory_sf2.npz` through `trajectory_sf5.npz` retain all four numeric
  arrays (`gamma`, `xx`, `zz`, `regiondata`) from the corresponding deposited
  object-dictionary NPY files. Shapes, dtypes and values are preserved, and each
  array's C-order byte digest is recorded. The portable NPZ files contain no
  object arrays and are read with `allow_pickle=False`.
- `first_passage_function.py` is an exact byte excerpt of lines 344-403 of the
  pinned `tracer_functions.py` (parent SHA-256
  `3f93e1685dd9664e279f8b14535d4ebc6ba2946442e4831f4eaf24db315d61ba`). It contains
  only `get_energy_by_region_w_bands`, excluding original imports, unrelated
  functions and top-level filesystem/plotting operations. It is upstream code,
  not a new function attributed to Taylor Kalin.

The original four trajectory files were posted in December 2025, after the
November 2025 preprint. Applying the pinned function reproduces all eight CS/DS
values printed in its Figs.8-11 to two decimal places. This correspondence does
not identify an exact historical full-cohort execution or make the four
illustrative selections a representative statistical sample.

Default reproduction is:

```text
python experiments/verify_first_passage.py
```

It requires Python, NumPy and Matplotlib and uses only repository-local inputs.
`--no-figure` runs the numeric checks with NumPy alone. The one-time conversion
used a restricted NumPy-only unpickler; provenance records the original file
and converted-array hashes. Default reproduction does not load the original
object/pickle files or depend on the author's or user's filesystem.

The project's CC0 declaration does not replace separately applicable licenses
of other upstream software. No VPIC simulator source, entire original paper,
or uninspected large trajectory batch is redistributed here.
