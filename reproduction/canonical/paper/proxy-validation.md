## Positive proxy and inferred display reconstruction checks

The proxy arrays require the same care. Their raw L320 time series has
122 entries ending at 23.16347, while its raw cumulative total reaches
0.357089. Directly comparing those raw numbers with the preprint axes or
with global magnetic-energy loss would suggest a large discrepancy.
We therefore extracted numerical line coordinates from the original
vector figures in the official v1 source archive and calibrated their
axes. This checks the displayed data rather than guessing the missing
plotting convention.

The following display factors and filter are inferred reconstruction conventions,
not independently identified historical plotting instructions. All five
cumulative L320 curves in preprint Fig. 3 are reproduced by
the first 116 deposited samples using

$$
\left(t/t_A\right)_{\rm display}
=t_{\rm raw}/5,\qquad
\mathcal D_{i,\rm display}
=\mathcal D_{i,\rm raw}/25.
$$

The island curve uses the sum of the two deposited island arrays.
There is source-code unit corroboration for these two scale factors,
independent of the coordinate fit. The posted tracer plotting driver uses
$\omega_{pe}/\omega_{ce}=0.2$ and $m_i/m_e=1$, hence
$\omega_{ci}=5$ in its plasma-frequency convention, and explicitly divides
its cyclotron-clock intervals by $\omega_{ci}t_A$. The dissipation producer
instead records its raw cyclotron clock divided by $t_A$. Conversion to
the stated plasma clock supplies the factor $1/5$. For the nominal L320
output interval its raw cumulative multiplier is 4000, while the
corresponding plasma-time interval is 160, giving $4000/160=25$.
The scripts and exact line locators for this dimensional check are
recorded in `data/source-claim-evidence.json`. This corroborates the
scale conversion under the posted conventions; it still does not recover
a hash-identified original plotting execution. No matching posted
instruction for the Gaussian width below has been found.

At the common endpoint the reconstructed total is 0.0139557484 at
$t/t_A=4.40297382$, matching the published curve rather than the raw
0.357089 endpoint outside that window. Across the five cumulative
paths and the rate reconstruction below, the largest coordinate
residual is 0.000555 PDF point, smaller than the declared 0.002-point
rounding tolerance. The original artwork is not redistributed; the
portable artifact preserves attributed numeric coordinates and their
source hashes.

The instantaneous and cumulative files are also coherent. Their stored
increments obey
$\Delta\mathcal D_{\rm raw}=4000\,D_{\rm raw}^{\rm inst}$
with maximum absolute residual $1.483\times10^{-9}$, consistent with
float32 storage of the instantaneous array. The paper's relativistic
Alfvén definition gives $t_A=4178.993735$ in plasma-time units for this
case. Taking the first 115 instantaneous samples, applying a Gaussian
filter of width 1.5 samples with half-sample symmetric boundary handling,
and multiplying by $t_A$ reproduces the Fig. 4 blue rate path. The
corresponding times are $t_{\rm raw}[1{:}116]/5$.
This is an independently verified display reconstruction; it does not
claim recovery of an unavailable historical plotting revision.

The common cumulative scale factor cancels in every regional share.
At the displayed endpoint the downstream fraction is 0.664435 and the
primary-sheet fraction 0.266235; the islands and top/bottom contribute
0.0586225 and 0.0107092. Those values are unchanged by the factor of
25. Thus the deposited curves positively preserve the preprint's
downstream-dominant ordering of this proxy. They provide no basis for
alleging that its published integral is too large by that factor.
The independently generated reconstruction figure and executable check
make this positive result reviewable.

The global-energy file supplies a bounded cross-check, not an identity
between the proxy and magnetic-energy conversion. Its 2618 rows contain
102 repeated restart steps. Keeping either the first or last value at
each recorded step gives identical data at the reported precision and
2516 uniformly spaced unique records. Matching the L320 timing
conditionally, the endpoint of the published window gives an
electromagnetic-energy loss of approximately $0.020190\,M_0$ and a
rescaled $\mathbf J\cdot\mathbf E$ integral of $0.020792\,M_0$. These comparable values involve
different averaging and output cadences and do not prove complete run
identity or exact energy closure. The same conditional comparison gives a
particle kinetic-energy gain of $0.022510\,M_0$ and a total recorded-energy
change of $+0.002320\,M_0$. We report that residual without diagnosing its
cause or claiming complete conservation from the comparison. The diagnostic spacing inferred from
409 simulation steps, five output intervals and the recorded timestep
is 159.70949 plasma-time units; the displayed convention uses the
nominal value 160, a 0.1819% difference. We record that distinction
without converting it into an unsupported scientific-error claim.

Finally, this successful reconstruction does not identify
$\int D_e\,dV\,dt$ with a magnetic-energy decrease or particle-energy
gain. The electron-frame quantity is a useful proxy whose relationship
to those budgets requires the appropriate work and transport terms.
The narrower diagnostic-interpretation question remains legitimate,
as do the separately tested particle-attribution questions. The
published proxy normalization, however, is consistent with the
available source arrays after their explicit display transformations.


The coordinate agreement tests whether the released arrays can reproduce
the published paths under these explicit transformations. It does not
uniquely identify why the original plot used a given scale, which revision
of the plotting program was executed, or whether an equivalent historical
pipeline used different intermediate units. In particular, the factor
25 is not reported as a discovered normalization error, and the inferred
Gaussian filter is not presented as a documented instruction by the source
authors. The dimensionless regional shares are invariant to a common
positive cumulative scale. The numerical reconstruction is sufficient for
that positive comparison; stronger producer provenance is a separate claim.
