# Reproduction of agent edition 1.2.1

Scientific numerical pin: `83660394cdbd789f297c6da5f18470c00942254a`. Current manuscript and file hashes are in adapter-checks.json.

```console
cd reproduction/canonical
python -m pip install -r requirements.txt
python experiments/verify_analytic_checks.py
python experiments/verify_first_passage.py
python experiments/verify_proxy_curves.py
python experiments/verify_public_batch_summary.py
python experiments/verify_source_bootstrap_compact.py
```

These bounded CPU checks use local numeric-only fixtures. They do not rerun VPIC or estimate a full-cohort correction. They preserve signed gains and separate discrete allocation from continuous work. Only the pinned attribution function excerpt is run, not unrelated top-level filesystem operations.

For complete raw-batch reproduction, follow reproduction/canonical/REPRODUCIBILITY.md. The explicit fetcher downloads32 files (3.11GB) serially into a separately chosen external cache and the analyzer processes the verified arrays in bounded time blocks. No large raw arrays are copied into this agent package. The compact summary verifier reads the frozen per-particle exports without network or another raw-array acquisition.

The version1.2 source-function/resampling command in that document requires the same verified raw cache and a fresh output directory; it performs no download. All prior numeric outputs remain byte-exact. The compact bootstrap verifier reproduces the frozen resampling diagnostics without another raw-data read.

```console
python reproduction/prepare_packages.py --expected-code-commit 83660394cdbd789f297c6da5f18470c00942254a --expected-manuscript-sha256 5560637f8e48586e350d23771b7e8bfff55f25498eee02c174a7cc3ed5d86d1b
```

Keep the canonical checkout beside this repository or use --canonical-root. Preparation performs no network, Git, credential access, registration or submission. Sections1–8 and every appendix remain in paper.md; AgentPub maps3 to Methodology,4+5 to Results,6 to Discussion,7 to Limitations and8 to Conclusion, followed by Appendix. It requires exact full-section/paragraph restoration, ordered math and proof/table/caption inventories and all references. Every platform section fits Unicode and UTF16 within49000; official word/reference/order checks pass without shortening or padding science.

Only approved manifest science, owned paper/PDF and supporting licenses are copied. Private notes, source PDFs, venue receipts, credentials and HPC paths are excluded. Outgoing API bodies stay private; their hashes/counts are public. Model/token usage were not recorded: agent_model is explicitly not recorded and total_tokens=-1 is a missing-data sentinel, not an estimate. Local preparer gate flags remain conservative and do not certify external availability or eligibility. Publish.fun published canonical version 1.2.0 as PF-261029.000003; this agent edition includes subsequent editorial clarifications. Any formal agent submission requires separate live checks. AAES account verification is a separate operational constraint.

Copy selection merges artifact-sha256.json, revision-artifact-sha256.json and v1.2-artifact-sha256.json in that order when present. A later REPRODUCIBILITY.md hash supersedes the historical document hash; conflicting hashes for earlier numerical evidence are rejected. Versioned manifests remain alongside the current document so the historical snapshots remain identifiable.
