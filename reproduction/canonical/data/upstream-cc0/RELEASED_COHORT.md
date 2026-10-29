# Released OSF trajectory batches

The public project [OSF EPWTU](https://doi.org/10.17605/OSF.IO/EPWTU)
contains 32 numeric NPY files under `Figure 5 Bottom`: eight time chunks
of `tracer` and `region` arrays for `inter_energy/p008` and
`high_energy/p000`. Their total uncompressed transfer is **3,107,362,288
bytes**. The source identifies these as example batches and does not
provide their archive-selection probabilities. These are larger,
multi-particle files. Three illustrative NPZ fixtures in this directory
are exact subhistories of the released high-energy staging batch; the
fourth was not found in either posted batch. The full-value comparison
is recorded in `data/batch-example-link-verification.json`.

`released-cohort-inventory.json` records every file's public ID, version,
date, download URL, size, SHA256 and MD5 from the source inventory. The
source project applies CC0. Preserve this provenance when redistributing
the upstream arrays; this audit's new code has its separate MIT license.

Choose a cache **outside this repository**, replace `COHORT_DIRECTORY`
below with that directory, and run from the repository root:

```text
python experiments/fetch_public_batches.py --output-dir COHORT_DIRECTORY
python experiments/analyze_public_batches.py --cohort-dir COHORT_DIRECTORY
```

The fetcher uses public OSF URLs and normal redirects, downloads serially,
and verifies each complete file before starting the next. Its receipt is
saved in the chosen cache. It never prints signed redirect URLs or needs
an OSF credential. A prefix is resumed only after checking its saved local
hash and the pinned strong remote ETag. Existing final files are skipped
only when their entire SHA256 and size agree. The analyzer independently
rechecks the 32 complete input files and uses read-only memory maps.

Small offline algorithm checks require no raw download:

```text
python experiments/analyze_public_batches.py --self-test
```

The actual tracer array shape is `(17, time, particle)`; region arrays
have shape `(time, particle)`. This order is established by the posted
producer and loader and checked against the NPY headers, rather than the
README's swapped dimension description. Channel 3 stores a particle ID,
not its physical charge or statistical weight. The 17 channels do not
include timestamps. Concatenation follows the posted filename-order
convention; tag stability does not independently prove physical timestamp
continuity.

The analyzer first checks that the two batches have disjoint IDs, pools
their individual histories, and then applies the source's strict cuts
`5.77 < final_gamma < 16.40` and `final_gamma > 16.40`. Folder names are
staging labels, not these final analysis bands. Counts of every posted
particle, exclusions and boundary values remain in the output. All five
local region labels are retained, including top/bottom. The source's
chronological residual is not silently renamed local-island work.

Results use unit empirical weights. Under the posted constant-weight
example deck, these equal the within-batch physical number weighting;
they do not supply inverse-inclusion probabilities or a representative
full-population estimate. Signed regional gains, zero/nonfinite
denominator behavior and left/right/symmetric endpoint conventions are
reported explicitly. Endpoint sensitivity is not a confidence interval
or a continuous-trajectory work-error bound.

Outputs are `results/public-batch-checks.json`, compact numeric-only
`results/public-batch-per-particle.npz`, a corresponding CSV, and
`figures/public-batch-comparison.png`. Raw gigabyte arrays are deliberately
kept outside the code archive.
