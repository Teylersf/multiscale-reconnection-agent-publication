## Source provenance and positive proxy-curve validation

The audit fixes its scientific target to the eleven-page arXiv:2511.15988v1
preprint by Velberg and collaborators. The supplied PDF is byte-identical to
the official versioned download, with SHA-256
c2648dcac8e67dc1136dc4f6339166cb475ebe44a7415508a97e34f0056a5b48.
The official record, checked on October 29, 2026, lists one version,
submitted November 20, 2025. The PDF's November 21 typesetting date does
not establish another scientific revision: its source uses a current-date
typesetting command. We read the complete PDF and TeX, including the
supplementary material. The bounded primary-metadata checks did not
identify a journal article or erratum. This is an edition-specific audit,
not a claim that no later publication can exist.
[Velberg et al., arXiv:2511.15988v1](https://arxiv.org/abs/2511.15988v1).

The associated OSF deposit materially improves what can be checked.
Its exact title, Alexander Velberg's creator record, and author-naming
project wiki establish the association. The deposit has a registered DOI,
10.17605/OSF.IO/EPWTU, and supplies example VPIC decks, custom diagnostic
includes, postprocessing programs, processed arrays and selected particle
histories. The project was created December 5, 2025; its current README
is marked July 20, 2026. These dates postdate the audited preprint.
The README also uses a later figure layout: its cumulative-proxy “Figure
4” data correspond to preprint Fig. 3, its instantaneous-proxy “Figure 3”
data to preprint Fig. 4, and its particle-fraction “Figure 5 Bottom” topic
to preprint Fig. 6. The additional global-energy and regional $\mathbf J\cdot\mathbf E$ material
is assigned other later figure numbers. This mapping is recorded explicitly;
the deposit is not silently treated as a hash-identified snapshot of every
program that produced v1.
[Velberg, OSF EPWTU](https://doi.org/10.17605/OSF.IO/EPWTU).

The frozen inventory contains 182 files. To bound transfer while examining
the relevant methods, we retrieved and verified the 127 files no larger
than two megabytes individually. These include the input decks and
postprocessing needed here. Large field outputs and the full particle
population were not retrieved. The project describes its much larger
underlying dataset and offers additional data on request. Consequently,
the audit distinguishes a reproduced calculation on available files from
a complete rerun of the approximately forty-billion-particle simulation.
The numeric OSF fixtures are preserved under the project's CC0 license;
that license does not replace independently applicable upstream software
licenses. Coordinates derived from the preprint's figures are separately
attributed under its CC BY 4.0 terms.

The input evidence resolves two apparent physical inconsistencies in a
favorable direction. The printed Eq. (1) gives
$B_x=B_0\sinh(x/L)/F(x,z)$ while its denominator contains
$\cosh(z/L)$. The deposited island deck instead initializes
$B_x=B_0\sinh(z/L)/F(x,z)$, with the corresponding printed expressions
for the other components. The corrected field is the appropriate
solenoidal equilibrium. The source therefore supports a coordinate typo
in the displayed formula rather than evidence that the simulation used
the inconsistent field. An example deck is not, by itself, a certificate
of the historical executable, but it is direct implementation evidence
that must constrain the criticism.

Likewise, reading the force-free-current-sheet footnote as literally
replacing its transverse equilibrium field by a constant guide field would
leave a pressure-balance problem for the stated uniform plasma. The
deposited comparison deck uses $\epsilon=0$, $L/d_e=6$ and $b_g=1$,
with

$$
B_x=B_0\tanh(z/L),\qquad
B_y=B_0\sqrt{\operatorname{sech}^2(z/L)+b_g^2},
\qquad B_z=0.
$$

Its field magnitude satisfies $B_x^2+B_y^2=B_0^2(1+b_g^2)$.
Thus the implementation retains the force-free profile while adding the
external guide contribution in quadrature. The footnote should state this
profile explicitly, but its shorthand does not substantiate an invalid
force-free comparison. The information file also gives
$\Delta x/d_e=0.2454369$ for the large run, consistent with the stated
approximately four cells per skin depth rather than an exact grid-count
contradiction.

The proxy arrays require the same care. Their raw L320 time series has
122 entries ending at 23.16347, while its raw cumulative total reaches
0.357089. Directly comparing those raw numbers with the preprint axes or
with global magnetic-energy loss would suggest a large discrepancy.
We therefore extracted numerical line coordinates from the original
vector figures in the official v1 source archive and calibrated their
axes. This checks the displayed data rather than guessing the missing
plotting convention.

All five cumulative L320 curves in preprint Fig. 3 are reproduced by
the first 116 deposited samples using

$$
\left(t/t_A\right)_{\rm display}
=t_{\rm raw}/5,\qquad
\mathcal D_{i,\rm display}
=\mathcal D_{i,\rm raw}/25.
$$

The island curve uses the sum of the two deposited island arrays.
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
