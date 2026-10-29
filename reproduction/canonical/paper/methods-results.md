## Particle attribution: first-passage phases and full region histories

The principal reproducible methods issue concerns the meaning of the regional
particle-energy gains. The preprint describes tracing nonthermal particles and
computing their energy gain by the current-sheet and downstream regions, with
region membership changing in time. Its Fig.6 averages the resulting fractions
over particles. The publicly deposited `tracer_functions.py` states that it
analyzes the corresponding figure and supplementary trajectories. Its function
`get_energy_by_region_w_bands` instead divides each history into phases defined
by first entry into the primary sheet and the first subsequent downstream
entry. This distinction can matter for a particle that returns to an earlier
region or visits downstream before first entering the sheet.

The relevant regional interpretation is stated in the source's particle-
acceleration paragraph on page 4 and its Fig. 6 caption on page 5. The
Fig. 8 caption on page 9 also connects the panel annotations to the
time-dependent region labels. We found no explicit first-passage formula
in that inspected text. These locators support the stated distinction;
they do not establish an author's unexpressed intent. The deposited
script's header identifies Fig. 6 and the supplemental trajectories as its
purpose, and its L320 driver loads the larger intermediate batch set before
printing particle-mean downstream and pooled sheet-plus-phase fractions.

The audit pins the December 6, 2025 version-1 source file, whose SHA-256 is
`3f93e1685dd9664e279f8b14535d4ebc6ba2946442e4831f4eaf24db315d61ba`,
and preserves its exact lines 344-403. The function is attributed to Alexander
Velberg and obtained from the CC0 OSF project, DOI
https://doi.org/10.17605/OSF.IO/EPWTU . Four selected deposited trajectories
provide a direct bridge to the preprint: the function reproduces every CS/DS
value printed in its Figs.8-11 to the reported two decimal places. The source
and data versions were deposited after the preprint, so this correspondence is evidence for the
illustrative calculations rather than a hash-identified historical execution of
the entire Fig.6 cohort.

The live file history lists only the December version. No earlier source
revision, execution receipt or correspondence has established that these
exact bytes generated the November preprint. The claim audited here is
therefore the semantics of the posted routine, supported by the separate
annotation agreement and the matched released-batch calculation below.

### What the deposited function computes

Let a recorded particle history have Lorentz factors
$\gamma_0,\ldots,\gamma_N$ and region labels $r_0,\ldots,r_N$. Suppose the first
recorded primary-sheet entry is $a$, and the first downstream entry after that
sheet entry is $b>a$. In this case the deposited function returns

$$
G_{\mathrm{CS}}^{\mathrm{FP}}=\gamma_b-\gamma_a,\qquad
G_{\mathrm{DS}}^{\mathrm{FP}}=\gamma_N-\gamma_b,\qquad
G_{\mathrm{I}}^{\mathrm{FP}}=\gamma_a-\gamma_0.
$$

Here FP denotes first-passage phases, and I names the residual initial phase
called `islands` by the function. The three differences telescope:

$$
G_{\mathrm{I}}^{\mathrm{FP}}+G_{\mathrm{CS}}^{\mathrm{FP}}
+G_{\mathrm{DS}}^{\mathrm{FP}}=\gamma_N-\gamma_0.
$$

Thus exact total-gain closure does not establish time-local regional
attribution. In particular, after $b$ the returned downstream term includes all
later gain and loss, even when later labels identify the particle as being in
the primary sheet or an island. Before $a$, all gain and loss enters the
initial-phase term even if a downstream visit has already occurred. The
function also handles particles that never enter the sheet and particles with
no subsequent downstream entry; those cases use analogous endpoint
differences.

A first-passage partition is a meaningful diagnostic in its own right. It
answers how net gain is divided among successive transit phases. It agrees
with a left-endpoint recorded-region partition when the history has the ordered
phase structure I, then CS, then DS, with no later returns. The objection is to
identifying it with regional work for general histories without stating this
additional structure or changing the estimator.

### A counterexample inside the reported intermediate band

Consider the following recorded trace:

$$
\begin{aligned}
(r_0,\ldots,r_7)&=(\mathrm{I},\mathrm{CS},\mathrm{CS},\mathrm{DS},
 \mathrm{DS},\mathrm{CS},\mathrm{CS},\mathrm{DS}),\\
(\gamma_0,\ldots,\gamma_7)&=(1.1,1.1,1.2,1.2,1.3,1.3,11.3,11.3).
\end{aligned}
$$

Its final Lorentz factor lies in the same intermediate interval used by the
public script, $5.77<\gamma<16.40$. Every interval whose endpoint region labels
differ has zero energy change. Consequently neither a choice of left versus
right endpoint nor interpolation of a nonzero boundary increment explains the
disagreement. The first-passage function returns

$$
(G_{\mathrm{CS}}^{\mathrm{FP}},G_{\mathrm{DS}}^{\mathrm{FP}})=(0.1,10.1),
$$

whereas summing increments over the recorded full region history gives

$$
(G_{\mathrm{CS}}^{\mathrm{hist}},G_{\mathrm{DS}}^{\mathrm{hist}})=(10.1,0.1).
$$

Both have total net gain $10.2$, and all gains are nonnegative. The later sheet
gain is assigned downstream by the first-passage definition. Scaling the
nonzero gains by ten yields the same reversal in the high-energy branch:
$(1,101)$ versus $(101,1)$, with final $\gamma=103.1>16.40$. Two additional
tests put downstream gain before first sheet entry; the function assigns that
gain to its initial-phase term. Monotone I-to-CS-to-DS positive controls pass in
both energy-band branches. These are direct executions of the pinned public
function on constructed inputs, not synthetic data presented as PIC output.

### A recorded-history alternative and what it can certify

For a target region $R$, let $\chi_R(r)$ denote its indicator and
$d_n=\gamma_{n+1}-\gamma_n$. Two transparent recorded-history conventions are

$$
L_R=\sum_{n=0}^{N-1}d_n\chi_R(r_n),\qquad
U_R=\sum_{n=0}^{N-1}d_n\chi_R(r_{n+1}).
$$

The symbols L and U identify left- and right-endpoint rules; U is not being
defined as an upper bound. If the recorded labels form an exhaustive exclusive
partition, then each rule obeys exact net closure:

$$
\sum_R L_R=\sum_R U_R=\gamma_N-\gamma_0.
$$

Their difference is localized to intervals with different endpoint labels:

$$
U_R-L_R=\sum_n a_{n,R},\qquad
a_{n,R}=d_n\{\chi_R(r_{n+1})-\chi_R(r_n)\}.
$$

It follows immediately that

$$
|U_R-L_R|\leq B_R,\qquad
B_R=\sum_n|a_{n,R}|
\leq\sum_{n:r_{n+1}\ne r_n}|d_n|.
$$

For the more specific discrete model that allocates each interval's *net*
increment between its two endpoint regions, write
$H_R=L_R+\sum_n\theta_n a_{n,R}$ with $0\leq\theta_n\leq1$. Then

$$
L_R+\sum_n\min(0,a_{n,R})\leq H_R
\leq L_R+\sum_n\max(0,a_{n,R}).
$$

Equivalently the interval is centered at $(L_R+U_R)/2$ with half-width $B_R/2$.
Because the $\theta_n$ may differ between intervals, the two aggregate endpoint
values alone need not be the extrema of that net-allocation model.

These are algebraic statements about recorded increments, not certified bounds
on continuous physical work. Unrecorded energy gain and loss within an
interval, or visits to another region between equal endpoint labels, cannot be
bounded by endpoint differences alone. To estimate
$\int \chi_R(t)\,q\mathbf E\cdot\mathbf v\,dt/(mc^2)$, one needs a stated
crossing-time prescription and adequately resolved work/region histories, with
a cadence study or independently justified assumptions. Reporting endpoint
alternatives and net-allocation ranges exposes ambiguity; it does not make
either alternative the uniquely corrected physical answer.

### Reproducing the four published examples

The four preserved numeric fixtures contain 40,764 recorded samples each.
They retain the source values, shapes and dtypes, with hashes in
`data/upstream-cc0/provenance.json`, and are loaded without pickle. The pinned
function gives the following results; values in the code columns are shown to
six decimal places, while the printed columns reproduce the original panel annotations.

| Original figure | Printed CS | Code CS | Printed DS | Code DS |
|---|---:|---:|---:|---:|
| 8 | 2.33 | 2.325038 | 4.26 | 4.257615 |
| 9 | 0.00 | 0.000000 | 14.01 | 14.008444 |
| 10 | 64.49 | 64.494324 | 30.80 | 30.796448 |
| 11 | 3.51 | 3.514739 | 47.34 | 47.344337 |

All eight values agree after rounding to two decimal places. Reentry also
occurs in these data: the histories corresponding to Figs.8, 10 and 11 have 15,
five and 24 sheet-labelled samples after first downstream entry, respectively.
The net increments with both endpoints in the sheet after that entry are
approximately $+0.086713$, $-0.560089$ and $+1.382980$. The first-passage
downstream term includes those later intervals irrespective of their recorded
sheet labels. The sign can be positive or negative, so a direction of
population bias does not follow simply from the function structure.

The following downstream values illustrate the finite-cadence distinction:

| Original figure | First-passage DS | Left endpoint DS | Right endpoint DS |
|---|---:|---:|---:|
| 8 | 4.257615 | 4.176339 | 4.830590 |
| 9 | 14.008444 | 17.062301 | 16.171096 |
| 10 | 30.796448 | 31.566879 | 76.442074 |
| 11 | 47.344337 | 46.764732 | 45.434556 |

These values can exceed a particle's total net gain if another region has net
cooling. Large differences between endpoint rules, especially in the Fig.10
trace, show why a single endpoint convention must not be advertised as a
resolved continuous channel partition. The examples were selected by the
authors for illustration. They neither represent an unbiased cohort sample nor
determine the size or sign of a change to the published population mean.

![Synthetic counterexample and four selected deposited histories. Panel (a) shows an intermediate-band return to the sheet with zero increment at every label transition. Panel (b) compares the same trace's first-passage and full-history allocations; both conserve total net gain. Panel (c) shows downstream net gain divided by total net gain for the four original examples. Left- and right-endpoint markers are alternative sampled conventions, not confidence intervals, and their connecting segments are not certified continuous-work bounds.](../figures/first-passage-attribution.png)

### Particle-mean and energy-weighted fractions

The script confirms a second, separate interpretive distinction. It reports
$\overline f_R=N_p^{-1}\sum_p G_{R,p}/G_p$, where $G_p$ is the particle's total
net gain. This expression is mathematically well-defined when each denominator
is nonzero; the inspected routine does not explicitly filter zero denominators.
It pools sheet plus island contributions in the orange series. This
is a valid particle-mean fraction. It is generally different from the
aggregate energy fraction $F_R=\sum_pG_{R,p}/\sum_pG_p$. For equal statistical
weights and nonzero mean total gain,

$$
F_R-\overline f_R=
\frac{\operatorname{Cov}(G_p,G_{R,p}/G_p)}{\overline G}.
$$

Three equal-weight particles with gains $(5,5,15)$ and downstream fractions
$(1,1,0)$ have a particle mean of $2/3$ but an aggregate downstream energy
fraction of $0.4$. Starting at $\gamma-1=0.1$, their final kinetic energies
$(5.1,5.1,15.1)$ all lie inside the reported intermediate band. This example
does not make the reported mean an incorrect estimator: it delineates which
quantity it estimates. Unequal macro-particle statistical weights require the
corresponding weighted definitions.

### Scope of the correction

The direct reproducible result is a diagnostic-definition mismatch for general
region histories, not a demonstration that downstream acceleration is absent.
The original temporal and spatial dissipation diagnostics provide separate
evidence of downstream activity, and the four particle examples retain
nonzero downstream gains under the displayed alternatives. The public decks
also positively resolve the printed field-coordinate and guide-profile
ambiguities, and the region code explicitly subtracts the expanded sheet mask
from island and downstream masks. Those checks should be credited.

A supported revision would either label the reported particle quantities as
first-passage-phase gains, with a justified connection to the intended regional
claim, or recompute full-history regional work with a documented cadence and
crossing convention. It should distinguish particle-mean fractions from total
energy shares and show the separate island contribution when claiming primary
sheet dominance. The current evidence does not quantify the full-cohort change,
establish a sign for that change, overturn the paper's main downstream trend,
or certify any uniquely corrected continuous physical partition.
