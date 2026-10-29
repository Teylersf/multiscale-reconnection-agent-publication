# Computational reproduction

Taylor Kalin's original audit code is MIT licensed; original text and figures
are CC BY 4.0. Attributed source fixtures retain their separately recorded
CC0 provenance. This computational package does not include a new PIC run or
the original paper's complete simulation output.

Install `requirements.txt` in a Python environment. The recorded runtime is
Python 3.12.14 with NumPy 2.3.5 and Matplotlib 3.11.2.

The original small-input checks need no network or GPU:

```text
python experiments/verify_first_passage.py
python experiments/verify_analytic_checks.py
python experiments/verify_proxy_curves.py
```

The revised batch algorithm and compact exported summaries can also be
checked without downloading the raw trajectory arrays:

```text
python experiments/analyze_public_batches.py --self-test
python experiments/verify_public_batch_summary.py
```

The latter independently recomputes summary metrics from the compact
per-particle NPZ and CSV. It does not independently reconstruct their input
trajectories or validate continuous electric work.

To reproduce the larger paired comparison, choose an external cache with
enough free space for **3,107,362,288 bytes** of pinned source arrays, plus
temporary download and analysis overhead. Replace `COHORT_DIRECTORY` below
with that cache directory. Acquisition is explicit and serialized:

```text
python experiments/fetch_public_batches.py --output-dir COHORT_DIRECTORY
python experiments/analyze_public_batches.py --cohort-dir COHORT_DIRECTORY
```

See [the released-cohort documentation](data/upstream-cc0/RELEASED_COHORT.md)
for file provenance, resumption, weighting, staging-versus-final-band cuts
and missing timestamp limitations. Existing downloads are skipped only
after size and complete SHA-256 verification. Raw gigabyte files are not
included in this archive or committed to Git.

The released union has 1,003 histories; its strict final-energy cuts retain
667 intermediate and 84 high-energy histories. Numerical results retain
signed gains and separately report two averaging estimands. The batches'
release probabilities and the complete historical Figure 6 execution are
not established. These results do not claim a population-unbiased
correction or a unique continuous-work partition.

Run the snapshot-bound compact-summary verifier before regenerating outputs.
The large-input analyzer writes fresh reports and execution metadata, so
regeneration can invalidate a historical receipt's byte hash even when the
scientific arrays agree. Frozen output hashes identify the archived run;
compare numeric arrays and estimator values separately when assessing a new
execution. The analyzer also performs its own source-function, input and
ledger consistency checks during that execution.
The typeset paper and its source are separately available in the public
[canonical repository](https://github.com/Teylersf/multiscale-reconnection-audit).
