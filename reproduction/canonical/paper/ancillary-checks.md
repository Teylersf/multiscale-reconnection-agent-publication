## Ancillary source and diagnostic checks

These checks separate local source-description issues from the regional
attribution finding. They do not establish an erroneous VPIC evolution.

### Printed equilibrium and the correctly posted field

Equation (1) of the preprint [1] prints
$B_x=B_0\sinh(x/L)/F$, while
$F=\cosh(z/L)+\epsilon\cos(x/L)$ and
$B_z=B_0\epsilon\sin(x/L)/F$. Direct differentiation gives

$$
\frac{L}{B_0}\nabla\cdot\mathbf B
=\frac{\cosh(x/L)}F+
\frac{\epsilon\sin(x/L)[\sinh(x/L)-\sinh(z/L)]}{F^2}.
$$

At the origin this is $1/(1+\epsilon)=5/7$ for $\epsilon=0.4$, so the printed
field is not solenoidal. Replacing the numerator by $\sinh(z/L)$ restores
the intended force-free modification of the Fadeev geometry [1,4]. In fact, with
$A_y=-B_0L\log F$,

$$
B_x=-\partial_zA_y,\qquad B_z=\partial_xA_y,\qquad
B_y=\frac{B_0\sqrt{1-\epsilon^2}}F,
\qquad
\nabla\times\mathbf B=
\frac{\sqrt{1-\epsilon^2}}{LF}\mathbf B.
$$

The first two identities make the divergence zero; differentiating $B_y$
and the in-plane components gives the last identity, so
$(\nabla\times\mathbf B)\times\mathbf B=0$.
Force-free does not imply constant $B^2$ for this curved equilibrium:
$B^2/B_0^2=[\cosh(z/L)-\epsilon\cos(x/L)]/F$.

Both currently deposited example decks [2] use the corrected $z$ numerator
for their unperturbed base field. The coalescence initialization also adds the
documented triggering perturbation; the equilibrium identities above refer to
the base field, not to that intentionally perturbed state.
Their common guide-field prescription is

$$
B_y=B_0\sqrt{(1-\epsilon^2)/F^2+g^2}.
$$

The coalescence example has $g=0$. The force-free current-sheet example has
$\epsilon=0$ and $g=1$, hence
$B_y=B_0\sqrt{\operatorname{sech}^2(z/L)+1}$.
This is genuinely force-free with $B_x=B_0\tanh(z/L)$; its total $B^2$ is
$2B_0^2$. The preprint's footnote [32] describes replacing the out-of-plane
field by an external guide. Read literally as a *uniform* replacement,
$B_y=gB_0$, it would instead give

$$
(\nabla\times\mathbf B)\times\mathbf B
=-\frac{B_0^2}{L}\operatorname{sech}^2(z/L)
\tanh(z/L)\,\hat{\mathbf z},
$$

which is nonzero. The posted profile resolves that description; it provides
a positive code check rather than evidence of a force-free implementation
failure. Present deposited examples and metadata do not independently identify
the exact historical binary and inputs for every reported run.

### Spectral caption

The body and inset of Fig. 5 in [1] specify a power-law index near 3.3, while
the caption specifies 3. The caption should identify the plotted guide
consistently. This local discrepancy does not establish a different fitted
exponent, invalidate the ankle, or reproduce the spectral fitting procedure.

### Electron-frame nonideal work and laboratory energy

The electron-frame measure used in [1] is the established relativistic
nonideal-work diagnostic [3]. Once the physical electron flow is specified,
$D_e$ is Lorentz invariant; it should not be described as observer-frame
dependent. Its relation to the laboratory work rate is the standard identity,
in dimensional Gaussian units,

$$
D_e=\gamma_e\left[
\mathbf J\cdot\left(\mathbf E+
\frac{\mathbf V_e\times\mathbf B}{c}\right)
-\rho_c\mathbf V_e\cdot\mathbf E\right],
\qquad
\mathbf J\cdot\mathbf E=
\frac{D_e}{\gamma_e}+
\frac{\mathbf V_e\cdot(\mathbf J\times\mathbf B)}c
+\rho_c\mathbf V_e\cdot\mathbf E.
$$

The second equality follows by the scalar triple-product identity. It is not
a new dissipation law. Poynting's theorem instead gives

$$
\partial_t\frac{E^2+B^2}{8\pi}
+\nabla\cdot\frac{c\mathbf E\times\mathbf B}{4\pi}
=-\mathbf J\cdot\mathbf E.
$$

Thus an integral of $D_e$ normalized by initial magnetic energy is a
normalized nonideal-work diagnostic, not by itself an exact magnetic-energy
loss or irreversible heating fraction [3,8]. The paper explicitly calls it a
proxy. Its reported regional ordering is not disproved by this distinction.
The posted Python expression is consistent with the normalized $c=1$
convention. This dimensional identity does not identify a unit error in the
published diagnostic outputs.

A portable exact check illustrates the distinction. In normalized
$m=e=c=\epsilon_0=n_+=n_-=1$ units, homogeneous cold counterstreaming beams
with momenta $\pm p$ satisfy $\dot p=E$ and
$\dot E=-2p/\sqrt{1+p^2}$. A parallel constant magnetic field does no work and
does not change. The conserved electric-plus-particle energy is
$E^2/2+2(\sqrt{1+p^2}-1)$. From $p=0,E=1$ to the first $E=0$,
$p=0.75$, the laboratory field-energy loss and particle-energy gain are both
0.5, whereas
$\int D_e\,dt=\int2p\dot p\,dt=0.5625$.
This checks the lack of a general equality; it is not a reconnection
simulation or an estimate of the diagnostic bias in [1].

Finally, implementation requires the physical definition and producer of any
input velocity/momentum files and the order of temporal averaging. Variable
names alone do not establish that a mean particle proper momentum is the
four-velocity of the number-flow mean. Those semantics remain a
reproducibility limitation here; no unverified velocity-file bug is claimed.
