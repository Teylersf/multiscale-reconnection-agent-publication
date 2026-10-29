### Complete-function validation and conditional empirical resampling

We extended the source-function validation from the previous systematic
32-history check per staging batch to every released input history. The new
validation rechecks the sizes and SHA-256 values of all 32 raw files, retains
their filename-ordered time chunks, and assembles only the stored float32
Lorentz factors and losslessly converted integer region labels. These arrays
occupy 204,431,460 bytes. The complete, unchanged 60-line function printed in
Appendix D is then executed once on the pooled 1,003 histories, rather than
only on the 751 histories selected beforehand. Its own strict final-energy
tests select 667 intermediate and 84 high-band histories and exclude the
remaining 252. Both returned index lists and all six returned regional-gain
arrays agree exactly with the streaming results, with zero mismatching values
and zero absolute difference. Thus the reported first-passage values are now
validated by a direct complete-function execution on every selected history.
The original module's unrelated top-level filesystem operations are not run.

The source returns float64 arrays containing differences calculated with the
native float32 input arithmetic. Our comparisons use the common denominator
$A_p=\gamma_{p,N}-\gamma_{p,0}$ evaluated in float64 from those same stored
endpoints. Replacing that denominator by the source's sum of returned phase
terms changes the downstream particle mean by $-6.56\times10^{-11}$ in the
intermediate band and $-3.35\times10^{-9}$ in the high band. These small
denominator effects are reported separately from the attribution differences;
no higher-precision particle history is inferred.

To describe the dispersion under an explicit empirical resampling model, we
also apply a paired history bootstrap [11]. Within each already selected
energy band, each replicate draws the original number of complete history IDs
with replacement and equal empirical probability. The same resampled IDs
are used for first passage, all three full-history conventions and both
estimands. Write
$D_{p}^{(m)}=G_{p,\mathrm{DS}}^{(m)}-G_{p,\mathrm{DS}}^{\mathrm{FP}}$
for $m\in\{L,S,R\}$. For one resampled index list $I_b$, the two paired
differences are

$$
\Delta\overline f_b^{(m)}=
 \frac{1}{n}\sum_{p\in I_b}\frac{D_p^{(m)}}{A_p},\qquad
\Delta F_b^{(m)}=
 \frac{\sum_{p\in I_b}D_p^{(m)}}{\sum_{p\in I_b}A_p}.
$$

Repeated IDs appear with their draw multiplicity. The ratio-of-sums
denominator is recomputed from those same draws, rather than resampling
numerators and denominators independently. All selected $A_p$ are positive;
regional gains and differences remain signed. We use 20,000 replicates per
band, seed 20261029, PCG64 with separately identified band streams, and
2.5th and 97.5th percentiles with NumPy's linear quantile rule. Computation
uses blocks of 256 replicates without changing the resampling unit. The
following values are changes from first passage, in percentage points.

| Available band | Convention | Particle-mean change | Conditional 2.5--97.5 percentile range | Total-net-gain-share change | Conditional 2.5--97.5 percentile range |
|---|---|---:|---:|---:|---:|
| Intermediate ($n=667$) | Left | -7.0218 | [-11.0001, -3.0968] | -8.2268 | [-12.0219, -4.5109] |
| Intermediate ($n=667$) | Symmetric | -3.2665 | [-6.3470, -0.2036] | -5.7232 | [-8.6783, -2.8621] |
| Intermediate ($n=667$) | Right | +0.4888 | [-4.3746, +5.8511] | -3.2197 | [-7.0472, +0.7179] |
| High ($n=84$) | Left | -12.9576 | [-22.0785, -4.4437] | -11.3545 | [-19.4089, -4.4561] |
| High ($n=84$) | Symmetric | -13.0189 | [-20.4864, -6.6663] | -9.7236 | [-17.2950, -3.3956] |
| High ($n=84$) | Right | -13.0803 | [-22.0611, -4.3208] | -8.0927 | [-17.5015, +0.9552] |

These are central 95% **conditional iid empirical bootstrap percentile
ranges**, not population confidence intervals, significance tests or physical
uncertainty bounds. The iid draws describe variation under the empirical
distribution of the available histories. Archive release probabilities are
unknown, so this procedure cannot account for selection into the public
files. Particles from one simulation can also share structures and be
correlated; resampling them as independent histories can understate
uncertainty. Independent-run or defensible structure-cluster replication is
not available here. The ranges do not cover temporal or mask cadence, hidden
recrossings, unresolved electric work, alternative release compositions or
omitted histories. In particular, an interval endpoint's position relative
to zero is not presented as evidence of population-wide statistical
significance. The high-band first-passage energy share was already below
one half; these added diagnostics do not change that estimand distinction.

The portable script is
`experiments/validate_full_source_and_bootstrap.py`. After obtaining the
already documented raw cache, the new calculation is invoked as follows;
the command performs no download:

```text
python experiments/validate_full_source_and_bootstrap.py --cohort-dir COHORT_DIRECTORY --output-dir NEW_DIAGNOSTIC_DIRECTORY
```

Choose a fresh output directory to retain the frozen published results.
The script writes newly named v1.2.0 validation, bootstrap JSON, replicate
NPZ and range-table CSV files, leaving the v1.1 outputs unchanged.
`results/full-source-validation-v1.2.0.json` records the full source execution
and raw-file bindings. `results/paired-history-bootstrap-v1.2.0.json` records
the resampling specification, percentile ranges and the hashes of all
replicate arrays and the full numeric table. Constant-shift, signed scalar
reference and block-size-invariance checks validate the paired implementation.
These remain computational checks, rather than independent human peer review.
