## Matched attribution on the released particle batches

### Available cohort and paired analysis

The public deposit permits a larger empirical comparison than the four
illustrative traces. We retrieved all 32 files in its two released
trajectory batches, verifying each file's source SHA256 and byte count
before starting the next transfer. These comprise 517 histories in
`inter_energy/p008` and 486 in `high_energy/p000`, each with 40,764 saved
samples. The batches have stable, unique integer tracer IDs in the same
order across all eight time chunks, and their ID sets are disjoint.
The 17-channel tracer arrays have shape `(17, time, particle)`; the
separate region arrays have shape `(time, particle)`. Their region
values are integer labels 1--5 stored in float64 arrays. The ID channel
is not a charge or statistical weight.

We concatenate the individual histories before applying the source's
strict final-$\gamma$ cuts, as its analysis driver does. The folder
names are staging groups, not the final physical energy bands. Of the
1,003 released histories, 667 satisfy $5.77<\gamma_N<16.40$ and 84 satisfy
$\gamma_N>16.40$; the remaining 252 lie below the lower cutoff. None
equals either boundary. The intermediate staging folder contributes
265 intermediate-band histories and 252 exclusions; the high staging
folder contributes 402 intermediate-band histories and all 84 high-band
histories. Folder averages are not averaged together.

The primary weights are explicitly unit empirical weights. The example
island deck assigns the same physical macro-particle `weight = Np/Ne`
to all tagged electron species, so those weights would cancel in the
within-batch fractions under that posted setup. Neither this fact nor
the filename batch indices establish archive inclusion probabilities.
The deposited driver loads intermediate batches 0--14 and high batch 0;
only intermediate batch 8 is publicly provided. The released union is
therefore an available subcohort, not an asserted probability sample or
a reconstruction of the entire Fig. 6 population. It contains
all eight time chunks of the released high staging `p000` selected by
that posted driver. Its completeness relative to the historical
high-energy cohort is not established.

Every comparison uses the same selected IDs and the same denominator
$A_p=\gamma_{p,N}-\gamma_{p,0}$. The source first-passage calculation
preserves the stored float32 values and its native arithmetic; the
full-history left, right and symmetric calculations subtract and
accumulate those same stored values in float64. They do not recompute
the underlying Lorentz factors. On a fixed systematic selection of 32
histories per staging batch, the streaming first-passage outputs agree
exactly with the pinned original function. Randomized branch/boundary
checks, four source-linked fixtures and independent small-sequence
checks additionally test the implementation. The largest source-arithmetic
closure residual is $3.10\times10^{-6}$; the left and right ledgers have
zero closure residual at the reported numerical precision.

The example linkage is also directly testable. All 40,764
stored $\gamma,x,z$ and region values of the source's Figs. 9--11 match
three columns of the high staging batch exactly, including their
canonical-array digests. The Fig. 8 history was not found in either
released batch. This ties the available files to three published
examples; it does not identify all the historical plotting inputs.
The arrays contain no timestamp channel. Filename ordering follows the
posted loader, rather than independently verified physical time vectors.

### Paired regional fractions and energy shares

For each convention we report both the mean particle fraction
$\langle G_{p,DS}/A_p\rangle$ and the fraction of the selected histories'
total net gain $\sum_pG_{p,DS}/\sum_pA_p$. All 751 selected histories
have positive, finite, nonzero $A_p$; no denominator filter is active.
Signed regional terms are retained. The JSON also records the original
source's unfiltered denominator convention, in which three
float32-derived phase terms stored in float64 arrays are summed; its small rounding differences do not
change the table at six decimals.

| Available band | Convention | Mean particle DS fraction | DS share of total net gain |
|---|---|---:|---:|
| Intermediate ($n=667$) | First passage | 0.722947 | 0.679606 |
| Intermediate ($n=667$) | Left endpoint | 0.652728 | 0.597338 |
| Intermediate ($n=667$) | Symmetric | 0.690281 | 0.622373 |
| Intermediate ($n=667$) | Right endpoint | 0.727834 | 0.647409 |
| High ($n=84$) | First passage | 0.500318 | 0.490959 |
| High ($n=84$) | Left endpoint | 0.370742 | 0.377414 |
| High ($n=84$) | Symmetric | 0.370129 | 0.393724 |
| High ($n=84$) | Right endpoint | 0.369515 | 0.410033 |

![Matched downstream fractions in the pooled available histories. The two curves compare a particle mean and a ratio of total signed gains on identical selected IDs. The four categorical positions are distinct attribution conventions; the connecting lines do not describe a time evolution. Panel ordinate scales differ. Unit empirical weights are used. There are no population confidence intervals, and endpoint sensitivity is not a continuous-work uncertainty bound.](../figures/public-batch-comparison.png)

For the available intermediate histories, downstream remains larger
than its signed non-downstream complement under every displayed
convention. The empirical changes are nevertheless material: the mean
fraction moves from 0.722947 to 0.652728 under the left rule, while the
right rule gives 0.727834. Thus even the sign of the first-passage versus
local difference depends on the declared sampling convention here.

For the 84 available high-band histories, the first-passage particle
mean is only just above one half; all three full-history endpoint
conventions give approximately 0.37. The aggregate energy-share
estimand is already below one half for first passage, and ranges from
0.377414 to 0.410033 for the local conventions. The difference between
the two estimands is therefore consequential even before attribution
is changed. These are measured available-subcohort results, not a
claim that the preprint's full-cohort ordering has been reversed.

The available intermediate first-passage mean, 0.722947, does not
reproduce the preprint's displayed $L/d_e=320$ intermediate point
(approximately 0.681). The available high-band first-passage mean
agrees with the displayed high-band point at three decimals (0.500),
which is useful consistency evidence but does not identify an exact
historical cohort. We therefore distinguish the measured available
union from a complete reconstruction of Fig. 6.

The full-history calculation retains IS1, IS2, top/bottom, downstream
and primary sheet separately. Its actual CS+IS1+IS2 pool excludes
top/bottom. The latter has a small signed intermediate-band mean
fraction, from $-4.77\times10^{-5}$ for the left rule to
$5.95\times10^{-5}$ for the right rule, and zero in the available high
band. The separately reported all-non-downstream complement includes
top/bottom. Neither pool is silently identified with the source's
CS+chronological-residual phase quantity.

### Returns, signed increments and limits

Among the selected histories, 187 of 667 intermediate particles and
40 of 84 high-band particles visit the primary sheet after their first
downstream sample following first sheet entry. There are respectively
743 and 89 subsequent sheet-entry events. The total numbers of recorded
region transitions are 51,156 and 6,976, and the sums of absolute net
increments on label-changing intervals are 10,974.343544 and
2,264.209734. These are discrete transition diagnostics, not bounds on
unresolved continuous work.

Negative regional net gains are not discarded: the left rule gives
79 intermediate and 18 high histories with negative downstream net
gain. Fractions above one also occur because a different region can
supply a loss. Both features are compatible with total-gain closure;
clipping them would change the estimands. Per-particle arrays, gross
positive/negative recorded increments and all per-folder subsets are
retained in the accompanying numeric outputs.

This comparison quantifies the attribution difference on every released
history that meets the source cuts, rather than on a newly selected
illustrative set. The omitted intermediate batches, uncertain archive
selection, coarse region sampling and absent timestamps still prevent
a certified full-population correction or a unique continuous-work
partition. A physical convergence study requires more information than
the small endpoint-convention differences in one band. The repository
provides an explicit public fetch command, the 32-file hash inventory,
a memory-bounded analyzer and compact NPZ/CSV results; the 3.11 GB raw
files remain outside the code archive.
