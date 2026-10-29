## A reproducible population reanalysis

Section 5 executes the paired ledger comparison on all available posted
histories and reports both estimands after common band selection. The
remaining extension is to a completely identified historical Figure 6
cohort, with its run, endpoint, sampling design and physical weights. The
following protocol specifies that extension and the separate validation
of continuous electric work; it is not presented as an additional
population calculation already completed here.

The demonstrated method discrepancy can be addressed without changing the
underlying particle-in-cell calculation. The primary empirical question is how
much the chosen regional statistic changes when the same cohort is analyzed
with its full recorded region histories. Answering that question requires a
matched comparison. Changing the cohort, energy cutoffs or masks at the same
time would confound the attribution change with a different analysis selection.

The first step is to freeze the intended cohort. The report should identify
the run, the final physical time associated with the chosen reconnected-flux
fraction, the particle identifiers and the final-energy band. The source
thresholds are stated in terms of $\gamma-1$, whereas the deposited routine
accepts $\gamma$; its intermediate-band inputs 5.77 and 16.40 correspond to
4.77 and 15.40 in the printed convention. The initialization tag, inclusion
probability and macro-particle weight should be retained for each selected
trajectory. A larger number of tracked samples alone does not establish that
their distribution represents the entire target population.

The second step is to retain time and region information together. For each
particle, record a monotone time vector, its energy samples and its region at
each sample. Discontinuities arising from restarts, repeated output steps,
particle sorting or chunk concatenation should be resolved explicitly rather
than treated as physical acceleration. The full-history calculation should
record the source of region labels and the mask update cadence, which may
differ from the particle-output cadence. Where available, electric fields and
velocities at the particle permit a separate electric-work quadrature check.
That check should use the same units and temporal alignment as the energy
record; it should not be replaced by an unrelated fluid-frame proxy.

Both the first-passage and full-history estimates can then be evaluated on
exactly the same selected histories. The chronological estimate remains useful
as an explicitly labeled transit-phase diagnostic. The full-history ledger
should retain the two islands, top/bottom, primary sheet and downstream entries
separately before forming any pooled quantity. This prevents a pooled
sheet-plus-islands statistic from being interpreted as the primary sheet alone.
Signed gains and losses should remain signed. Negative regional work, or a
regional net contribution larger than the particle's total net gain, need not
indicate failed energy conservation when another region supplies a loss.

Three validation levels should be distinguished. Algebraic closure checks
whether all recorded increments have been assigned exactly once. Controlled
one-pass and re-entry tests check the intended attribution semantics. Cadence
and crossing tests assess how the recorded approximation approaches a physical
work integral. Passing the first level cannot replace either of the others.
The counterexamples in this audit are useful tests precisely because their
total budgets close while their chronological and spatial meanings differ.

For a fixed sampling, reporting left, right and symmetric endpoint allocations
exposes an important part of the observable ambiguity. The sum of absolute
energy increments at changed endpoint labels gives a sensitivity budget for
that restricted family of net-increment allocations. It does not cover hidden
recrossings or work with cancelling signs inside an interval. A physical
uncertainty claim therefore also needs finer sampling or directly integrated
work with adequately resolved crossing information. The large convention
differences in some selected examples motivate this check; they do not select
one endpoint rule as the correct physical answer.

Finally, report the chosen population estimands and their denominators. The
particle mean of regional fractions and the weighted fraction of total energy
should be shown separately when both interpretations matter. If uncertainties
are estimated, the sampling scheme and the correlations among particles in a
common structure must be considered. Repeating a large number of correlated
particle observations from one run is not equivalent to repeating independent
simulation realizations. Sensitivity to the classifier's mixing threshold,
sheet-width parameter and spatial expansion can be assessed as a separate
postprocessing study, provided the necessary fields and tags are retained.

These steps define a concrete repair and comparison protocol. They do not
predetermine whether the population-level correction will be small, large or
of a particular sign. In particular, the separate positive reconstruction of
the source's regional nonideal-work curves remains evidence for downstream
activity under that diagnostic, regardless of the outcome of a particle-ledger
reanalysis.
