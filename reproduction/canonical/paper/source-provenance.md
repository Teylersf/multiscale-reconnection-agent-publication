## Source provenance and available particle data

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
postprocessing needed here. We also examine the complete publicly posted
intermediate-energy p008 and high-energy p000 batches, with their paired
trajectory and region time chunks. These are documented example batches,
not the entire simulation population or an established probability sample. The project describes its much larger
underlying dataset and offers additional data on request. Consequently,
the audit distinguishes a reproduced calculation on available files from
a complete rerun of the approximately forty-billion-particle simulation.
The numeric OSF fixtures are preserved under the project's CC0 license;
that license does not replace independently applicable upstream software
licenses. Coordinates derived from the preprint's figures are separately
attributed under its CC BY 4.0 terms.



The manuscript distinguishes three provenance claims. The December 2025
routine is directly inspectable and explicitly identifies the relevant
particle-energy figure in its comments. Its outputs on the four released
illustrations reproduce the eight v1 annotations. Neither this agreement nor
the later figure-generation comments establish a hash-identified November
2025 executable or the exact Figure 6 cohort. The new batch comparison holds
each released history fixed while changing only the attribution ledger; it
does not silently identify those batches with the complete v1 population.

The source and software DOIs are registered by DataCite. Public DataCite
metadata, the doi.org registration-authority service and anonymous downloads
were checked directly; absence from a Crossref lookup is not absence from
the DOI system. Direct source access is https://osf.io/epwtu/ and the original
software record is https://zenodo.org/records/23774456 . Public verification
receipts preserve the registry URLs, metadata and downloaded-file checksums.
The full pinned routine is printed in Appendix D. Positive field and proxy
checks are retained in Appendices B and C so they remain independently
reviewable without displacing the particle-attribution result.
