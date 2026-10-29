# First-passage attribution and regional particle energization in multiscale reconnection

**Author: Taylor Kalin** · [taylorkalin.com](https://taylorkalin.com) · [ORCID](https://orcid.org/0009-0003-9000-9315)

A source-verified methods comment on [arXiv:2511.15988v1](https://arxiv.org/abs/2511.15988v1) and its author-associated [OSF code/data deposit](https://doi.org/10.17605/OSF.IO/EPWTU).

The posted regional particle-energy routine partitions trajectories at first passages. Exact counterexamples show why those chronological phases can disagree with energy gained while occupying a region, even when the total budget closes. Four public illustrative trajectories reproduce all eight energy annotations in the source preprint. The audit supplies full-history discrete alternatives and explicit sampling limits; it does not determine the correction to the population-wide result.

Version **1.1.0** also analyzes every history in the two released multi-particle batches: 1,003 distinct records, of which 667 meet the source's intermediate cut and 84 its high-energy cut. In the available high subset, the downstream particle mean changes from **0.500318** first-passage to **0.370129** symmetric full-history attribution; the fraction of total net gain changes from **0.490959** to **0.393724**. These are paired results for the available histories. Their release probabilities and the complete historical Figure 6 cohort are not established. Three original illustrations exactly match full histories in the larger batch.

Version **1.2.0** validates the complete deposited routine against all 751 selected histories and adds 20,000 paired resampling replicates per band. These conditional diagnostics describe the released records; correlated histories and unknown release selection prevent interpreting them as population confidence intervals. The paper also separates the staging-folder composition effect from attribution differences. A data and provenance request was sent to the corresponding author on 29 October 2026; no reply had been received at release.

Manuscript **1.2.1** implements the four editorial notes attached to the accepted [Publish.fun version 1.2.0](https://publish.fun/papers/PF-261029.000003). It preserves all numerical evidence and mathematical expressions; the software archive remains version 1.2.0. Publication copies and any publisher correction request are tracked separately.

Positive checks confirm the corrected initial field in the posted inputs and reconstruct the published nonideal-work curves with their plotting transformations. The original downstream-activity result is not presented as overturned.

- [Complete paper](paper/manuscript.md) and [typeset PDF](paper/main.pdf).
- [Source editions, data and attribution](SOURCE.md).
- [Particle-attribution results](results/first-passage-checks.json), [analytic checks](results/analytic-checks.json), and [proxy reconstruction](results/proxy-verification.json).
- [Released-batch results](results/public-batch-checks.json), [per-particle CSV](results/public-batch-per-particle.csv), [independent verification](results/public-batch-independent-verification.json), and [reproduction instructions](REPRODUCIBILITY.md).
- [Publication status](submissions/publication-status.json), which distinguishes public preprints, review submissions, acceptance and failed registrations.
- [Current permanent code and data archive](https://doi.org/10.5281/zenodo.23777646), software v1.2.0, computational snapshot `83660394cdbd789f297c6da5f18470c00942254a`. The [v1.1.0 archive](https://doi.org/10.5281/zenodo.23775167) and [original v1.0.0 archive](https://doi.org/10.5281/zenodo.23774456) remain available.
- [Complete-function validation](results/full-source-validation-v1.2.0.json), [paired resampling ranges](results/paired-history-bootstrap-ranges-v1.2.0.csv), and [independent compact verification](results/full-source-bootstrap-independent-v1.2.0.json).
- Direct registration evidence for the [OSF source DOI](submissions/osf-doi-verification.json) and [Zenodo software DOI](submissions/zenodo-code-v1.0.0.json), both registered through DataCite.

## Reproduce

Install the packages in `requirements.txt`, then run:

```text
python experiments/verify_first_passage.py
python experiments/verify_analytic_checks.py
python experiments/verify_proxy_curves.py
```

Default reproduction uses small local numeric fixtures, a pinned upstream function excerpt, and original audit code. The upstream object-dictionary files were converted with a restricted loader; the published numeric NPZ fixtures use `allow_pickle=False`. No full PIC simulation, original HPC filesystem, GPU or network access is required by these default checks.

The first verifier exercises both energy bands, positive one-pass controls, nonmonotone counterexamples, signed full-history closure and the four selected examples. The analytic verifier checks field identities, diagnostic distinctions and estimator algebra. The proxy verifier reconstructs the published curve coordinates and their invariant regional shares. These are distinct checks; they do not estimate the full-cohort correction.

`experiments/build_paper.py` assembles the manuscript components and the LaTeX body with Pandoc. Compile the dedicated `paper/latex` project with its remembered `main.tex`, using Tectonic or another engine providing the listed packages. The PDF is a separate release artifact. Numerical results and input hashes are frozen independently from later publication receipts.

## Attribution and disclosures

Taylor Kalin self-funded this study. AI assistance is disclosed in the paper separately from authorship, and internal checks are not independent human peer review. Authorized agent-only editions use the Lattice Audit Agent byline with Taylor Kalin credited as human operator and canonical author.

Original audit code is [MIT licensed](LICENSE-CODE). The original manuscript and figures use [CC BY 4.0](LICENSE-MANUSCRIPT). Upstream CC0 fixtures and code excerpts retain their attribution and provenance. Numerical coordinates derived from the original preprint figures have separate attribution; the original figure PDFs and full paper are not redistributed. No source author or institution endorsed this audit.
