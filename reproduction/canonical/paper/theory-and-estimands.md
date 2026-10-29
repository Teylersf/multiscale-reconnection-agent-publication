## Appendix: estimator identities and sampling limits

This appendix supplies self-contained proofs for the estimands used in the
main comparison. Acceleration after downstream entry and acceleration while
downstream coincide for a one-pass history, but need not coincide after
re-entry. These are elementary bookkeeping identities, not new particle
dynamics or new general dissipation laws.

### First-passage epochs

Consider one particle with saved Lorentz factors
$\gamma_0,\ldots,\gamma_N$ and mutually exclusive region labels
$r_0,\ldots,r_N$. Let $C$ denote the primary current sheet and $D$ the
downstream region. If a sheet visit is followed by a downstream visit, define

$$
a=\min\{k:r_k=C\},\qquad
b=\min\{k>a:r_k=D\}.
$$

The deposited function returns

$$
G_C^{\mathrm{FP}}=\gamma_b-\gamma_a,\qquad
G_D^{\mathrm{FP}}=\gamma_N-\gamma_b,\qquad
G_I^{\mathrm{FP}}=\gamma_a-\gamma_0.
$$

Here $I$ is the routine's residual contribution, called islands in the code;
the formula does not itself test whether every contributing sample is in an
island. Band selection acts on the final energy and does not change these
per-particle identities.

**Proposition 1 (epoch interpretation).** Put
$\delta\gamma_k=\gamma_{k+1}-\gamma_k$. The first-passage outputs are precisely
the sums of $\delta\gamma_k$ over the chronological intervals
$[a,b)$, $[b,N)$ and $[0,a)$, respectively. They therefore sum to
$\gamma_N-\gamma_0$, independently of the labels between the selected entries.

**Proof.** The three sums telescope to their stated endpoint differences.
Their index intervals partition $\{0,\ldots,N-1\}$, so their sum telescopes
again to the total change. No intermediate region indicator occurs. $\square$

In the other source branches, a particle that never visits $C$ is assigned a
downstream epoch beginning at its first $D$ sample. If $C$ is visited but no
later $D$ sample occurs, the sheet epoch runs from first to last $C$ sample,
with the remainder assigned to $I$. These are also chronological partitions;
they need not follow each intervening region visit.

The first-passage calculation is a valid *phase* statistic. For a strictly
ordered history whose saved labels remain in islands before $a$, in $C$ from
$a$ through $b-1$, and in $D$ thereafter, it also equals a left-endpoint
regional-increment sum. That is a sufficient condition, not a necessary
condition: accidental cancellations can yield agreement for other histories.
Total-gain closure alone cannot establish the condition.

### Counterexample family and exact attribution discrepancy

Let $A>0$ be the gain in a first sheet visit, $B>0$ the gain downstream and
$C_*>0$ the gain in a later sheet visit, with zero gains on the intervening
transitions and no initial-phase gain. Such a history has saved labels
$(I,C,C,D,D,C,C,D)$; starting at $\gamma_0$, its energies are
$(\gamma_0,\gamma_0,\gamma_0+A,\gamma_0+A,
\gamma_0+A+B,\gamma_0+A+B,\gamma_0+A+B+C_*,\gamma_0+A+B+C_*)$.
The first-passage and visit-local pairs are

$$
(G_C^{\mathrm{FP}},G_D^{\mathrm{FP}})=(A,B+C_*),\qquad
(G_C,G_D)=(A+C_*,B).
$$

Their downstream-share difference is $C_*/(A+B+C_*)$. It approaches one as
$C_*$ grows with $A,B$ fixed. For $A=B=1$ and $C_*=100$, the outputs are
$(1,101)$ and $(101,1)$, both closing to 102. Left and right endpoint rules
agree because every transition increment is zero. Smooth gain episodes
supported inside constant-region visits give the same result, so the reversal
does not depend on crossing-time tie breaking. It does not estimate the
source cohort's error.

For an arbitrary saved history with downstream epoch beginning at $b$, write
$L_D=G_D^L$ for the left-endpoint regional sum defined below. Its exact
discrepancy is

$$
G_D^{\mathrm{FP}}-G_D^L
=\sum_{k=b}^{N-1}\bigl(1-\mathbf1\{r_k=D\}\bigr)\delta\gamma_k
 -\sum_{k=0}^{b-1}\mathbf1\{r_k=D\}\delta\gamma_k.
$$

Thus non-downstream gains after first downstream entry and downstream gains
before that entry contribute with opposite signs. With losses, island
excursions and re-entry, there is no universal sign of the bias.

### Full-history estimators and closure

For continuous collisionless Lorentz dynamics without additional forces,
$d\gamma_p/dt=q_p\mathbf v_p\cdot\mathbf E/(m_pc^2)$. A regional net-work
target is therefore

$$
G_{p,R}=\int_{t_0}^{t_N}
 \chi_R(\mathbf x_p(t),t)
 \frac{q_p\mathbf v_p(t)\cdot\mathbf E(\mathbf x_p(t),t)}{m_pc^2}\,dt
=\int_{t_0}^{t_N}\chi_R\,d\gamma_p.
$$

The masks may move. This target describes changes in a particle's energy
while in a region; it is not the energy carried into that region or stored
there at the final time. If $\sum_R\chi_R=1$, summing over regions gives the
total particle-energy change.

An explicit finite-cadence convention is

$$
G_{p,R}^{L}=\sum_{k=0}^{N-1}
 \mathbf1\{r_{p,k}=R\}\delta\gamma_{p,k}.
$$

This uses every visit. A right-endpoint version uses $r_{p,k+1}$ instead.
Both retain signed changes and all regions, including the two islands and
top/bottom region even when some are later pooled for presentation.
For one particle, the main text writes these two values as $L_R$ and $U_R$;
the latter symbol denotes a right-endpoint rule, not an upper bound.

**Proposition 2 (discrete closure).** For any interval-allocation weights
$\alpha_{p,R,k}$ satisfying $\sum_R\alpha_{p,R,k}=1$, define
$G_{p,R}^{\alpha}=\sum_k\alpha_{p,R,k}\delta\gamma_{p,k}$. Then

$$
\sum_R G_{p,R}^{\alpha}=\gamma_{p,N}-\gamma_{p,0}.
$$

**Proof.** Interchange the finite sums, insert the unit sum of weights and
telescope the increments. $\square$

Nonnegative allocation weights support the interpretation of assigning each
interval to regions; the closure identity itself only requires their unit
sum. A useful conservative output assigns intervals with equal endpoint
labels to that label and places label-changing intervals in an explicit
unclassified-transition category. The category must remain in the closure
sum. Equal endpoint labels still do not exclude an unresolved exit and
return within the interval.

### Endpoint sensitivity is not a continuous-work error bound

For $0\leq\theta_k\leq1$, consider the endpoint-allocation family

$$
G_R^{\theta}=\sum_k
\left[(1-\theta_k)\mathbf1\{r_k=R\}
 +\theta_k\mathbf1\{r_{k+1}=R\}\right]\delta\gamma_k.
$$

It contains left, right and symmetric endpoint assignments. These weights
are bookkeeping choices, not inferred fractions of time spent in a region.
Define the endpoint transition diagnostic

$$
T_{\mathrm{end}}=\sum_{k:r_{k+1}\ne r_k}|\delta\gamma_k|.
$$

**Proposition 3 (allocation sensitivity).** For any two members of this
family and any region,

$$
|G_R^{\theta}-G_R^{\phi}|\leq T_{\mathrm{end}},\qquad
\sum_R|G_R^{\theta}-G_R^{\phi}|\leq2T_{\mathrm{end}}.
$$

**Proof.** Their per-interval difference is
$(\theta_k-\phi_k)
(\mathbf1\{r_{k+1}=R\}-\mathbf1\{r_k=R\})\delta\gamma_k$.
It vanishes when the labels agree. Otherwise its absolute value for one
region is at most $|\delta\gamma_k|$, and its sum over region absolute values
is at most $2|\delta\gamma_k|$. Apply the triangle inequality and sum.
$\square$

There is a sharper, attainable per-region range within this allocation
family. Set
$a_{k,R}=\delta\gamma_k(\mathbf1\{r_{k+1}=R\}-\mathbf1\{r_k=R\})$ and
$B_R=\sum_k|a_{k,R}|$. Then

$$
L_R+\sum_k\min(0,a_{k,R})\leq G_R^{\theta}
\leq L_R+\sum_k\max(0,a_{k,R}),
$$

or, equivalently, $(L_R+U_R)/2-B_R/2\leq G_R^{\theta}
\leq(L_R+U_R)/2+B_R/2$. To attain the lower or upper endpoint for this
region, choose each $\theta_k$ as 0 or 1 according to the sign of $a_{k,R}$.
The choices can differ between intervals, so $L_R$ and $U_R$ need not be the
extrema. Different regions' extrema need not occur for the same choices.

These bounds concern only the stated *discrete allocation family*.
$T_{\mathrm{end}}$ cannot generally bound the error relative to continuous
regional work. For example, sample a particle downstream at both ends of one
interval with the same energy. Between samples it can enter the sheet, gain
$A$, return downstream and lose $A$. Its endpoint increment and
$T_{\mathrm{end}}$ are zero, while its regional net gains are $+A$ in the
sheet and $-A$ downstream. Smooth gain/loss episodes can occur away from the
crossings. Sign cancellations create a similar obstruction even in an
interval with different endpoint labels.

For a left-endpoint assignment the continuous discrepancy obeys the standard
inequality

$$
|G_R-G_R^L|\leq\sum_k\int_{t_k}^{t_{k+1}}
 |\chi_R(t)-\mathbf1\{r_k=R\}|\,|\dot\gamma(t)|\,dt.
$$

A useful physical bound needs information about the work rate and crossings
on those intervals. Endpoint net increments do not supply its total
variation. Recovering continuous regional work consequently requires
adequate particle/field/mask cadence or pusher-level diagnostics, resolved
crossings and a convergence check. Electric-work quadrature should also be
compared with the numerical change in particle kinetic energy rather than
assuming an exact identity for a finite-step pusher.

### Particle averages, energy shares and signed gains

For one selected energy band, put $A_p=\Delta\gamma_p$ and
$f_{p,R}=G_{p,R}/A_p$. First suppose $A_p>0$ for every included particle and
their physical weights are equal. A mean particle fraction and a fraction of
the band's total net gain are respectively

$$
\overline f_R=\frac1{N_p}\sum_p f_{p,R},\qquad
f_R^E=\frac{\sum_pG_{p,R}}{\sum_pA_p}.
$$

**Proposition 4 (covariance distinction).** With population covariance
$\operatorname{Cov}(A,f)=N_p^{-1}\sum_p(A_p-\overline A)
(f_p-\overline f)$,

$$
f_R^E=\overline f_R+
\frac{\operatorname{Cov}(A,f_R)}{\overline A}.
$$

**Proof.** Since $G_{p,R}=A_pf_{p,R}$,
$f_R^E=\overline{Af_R}/\overline A$; insert
$\overline{Af_R}=\overline A\,\overline f_R+
\operatorname{Cov}(A,f_R)$. $\square$

The mean particle fraction and energy share answer different questions, as
the main text's within-band example demonstrates. The deposited code [2] explicitly uses
the particle mean and pools current-sheet plus island contributions; that
statistic should not be silently renamed an energy-weighted total partition.
For unequal macroparticle weights $w_p>0$, the same identity holds for the
physical number-weighted mean and covariance defined using
$\langle X\rangle_w=\sum_pw_pX_p/\sum_pw_p$; an unweighted macroparticle mean
then needs separate justification.

Regional net gains can be negative even if $A_p>0$, and individual fractions
can lie outside $[0,1]$. Clipping negative contributions changes both the
estimand and the closure. If $A_p=0$, its per-particle fraction is undefined;
if signed total gains or a near-zero ensemble denominator are included, the
ratios are not probability shares and may be poorly conditioned. Report
these cases explicitly. Gross positive and negative work can be useful
additional quantities, but neither is reconstructed by net endpoint changes
alone. The selected final-energy band, sampling weights and masks must remain
fixed and disclosed when comparing estimators.
