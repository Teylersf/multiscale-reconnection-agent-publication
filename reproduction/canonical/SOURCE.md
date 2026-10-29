# Source editions and evidence scope

The audited preprint is A. Velberg, A. Stanier, X. Li, F. Guo, W. Daughton and N. F. Loureiro, *Effects of Multi-scale Coupling on Particle Acceleration and Energy Partition in Magnetic Reconnection*, [arXiv:2511.15988v1](https://arxiv.org/abs/2511.15988v1), submitted 20 November 2025.

The supplied PDF and the [official versioned PDF](https://arxiv.org/pdf/2511.15988v1) are byte-identical: 11 pages, 14,578,512 bytes, SHA-256 `c2648dcac8e67dc1136dc4f6339166cb475ebe44a7415508a97e34f0056a5b48`. The official [source archive](https://arxiv.org/src/2511.15988v1) is 43,836,123 bytes, SHA-256 `20c0cd402c0f1ebb88d944255aaf52c7f0059af06c5005668434c2667f3da4f4`. All pages, captions, supplemental text, references and the source TeX were read; the relevant rendered equations and plots were checked directly.

As checked on 29 October 2026, the official arXiv record lists only v1 and gives no journal reference. Bounded primary-source metadata checks did not identify a journal edition or erratum. This is not a proof that no other version exists. The scientific claims in this audit are tied to the identified preprint and specific public code/data versions.

## Author-associated code and data

Alexander Velberg's [OSF project EPWTU](https://osf.io/epwtu/), DOI [10.17605/OSF.IO/EPWTU](https://doi.org/10.17605/OSF.IO/EPWTU), identifies itself as accompanying this study and declares CC0 1.0 Universal. It includes example inputs, custom diagnostic includes, postprocessing code and figure data. Its complete inventory contains 182 files, approximately 11.21 GB. A selected 127-file subset totaling 6,751,167 bytes was downloaded serially and checked against advertised sizes and hashes. Large grid and full trajectory batches were not required for the present bounded tests.

The two analyzed example decks were posted as version 1 on 5 December 2025. The analyzed `tracer_functions.py` was posted as version 1 on 6 December 2025. The README and some additional diagnostic files have July 2026 updates, and the project has later changes. Project-level metadata or changed figure numbering is therefore not treated as proof that every deposited artifact belongs to the exact preprint execution.

The particle-analysis file SHA-256 is `3f93e1685dd9664e279f8b14535d4ebc6ba2946442e4831f4eaf24db315d61ba`. Its exact function excerpt, lines 344-403, is preserved under [data/upstream-cc0](data/upstream-cc0/README.md), with the parent checksum and stable source identifiers. Four numeric-only converted trajectory fixtures preserve all arrays from the selected original object-dictionary files. Per-array byte digests and conversion details are recorded in their provenance file. The source routine reproduces all eight current-sheet/downstream labels in preprint Figs.8-11 to two decimal places. This identifies the illustrative calculations; it does not identify the original full-cohort execution or make the four selections statistically representative.

## Positive controls and claim boundaries

The printed initial field contains `sinh(x/L)` where the divergence-free field requires `sinh(z/L)`. The posted decks implement the corrected unperturbed base field and separately add the documented triggering perturbation. They also implement the spatially varying force-free guide profile, resolving the ambiguity of the short benchmark description. The run information explains the approximate grid-spacing language and particle count. These observations support a text correction, not an allegation that the initialization was implemented incorrectly.

The released proxy arrays require plotting transformations before comparison with the preprint. The reproduced published cumulative curves use raw time divided by 5 and cumulative values divided by 25. The instantaneous curve uses independently reconstructed smoothing and time normalization. The resulting coordinate matches provide a positive validation; untransformed arrays do not establish a published normalization error. Regional shares are invariant under the common rescaling.

The main methods finding is that a chronological first-passage partition is not a general time-local regional energy partition. Exact total-gain closure cannot distinguish them. Synthetic tests establish this point without boundary-allocation ambiguity, while real selected traces expose finite-cadence sensitivity. No full-cohort bias, sign of a population correction, uniquely corrected continuous partition or reversal of the source's main downstream trend is claimed.

## Rights and reproducibility

The upstream function excerpt and selected OSF fixtures retain their CC0 provenance. Small attributed numerical curve-coordinate references are derived from the source preprint and are documented separately from the CC0 dataset. Original source PDFs, full TeX and large simulation outputs remain at their official origins. The audit's MIT and CC BY grants cover its original contributions and do not relicense other material.

Only repository-local fixtures are needed for the default scientific checks. Machine-readable source and reference metadata identify public URLs, versions and checksums without private cache paths or signed download URLs. Working extraction logs, preliminary hypotheses and private publishing credentials are excluded from the public repository.
