# Reproduction of agent edition 1.1.0

Scientific numerical pin: `a8cb56dadaf6fdf6d07ce6aba0d94b9ad291f9d5`. Current manuscript and file hashes are in adapter-checks.json.

```console
cd reproduction/canonical
python -m pip install -r requirements.txt
python experiments/verify_analytic_checks.py
python experiments/verify_first_passage.py
python experiments/verify_proxy_curves.py
python experiments/verify_public_batch_summary.py
```

These bounded CPU checks use local numeric-only fixtures. They do not rerun VPIC or estimate a full-cohort correction. They preserve signed gains and separate discrete allocation from continuous work. Only the pinned attribution function excerpt is run, not unrelated top-level filesystem operations.

For complete raw-batch reproduction, follow reproduction/canonical/REPRODUCIBILITY.md. The explicit fetcher downloads32 files (3.11GB) serially into a separately chosen external cache and the analyzer processes the verified arrays in bounded time blocks. No large raw arrays are copied into this agent package. The compact summary verifier reads the frozen per-particle exports without network or another raw-array acquisition.

```console
python reproduction/prepare_packages.py --expected-code-commit a8cb56dadaf6fdf6d07ce6aba0d94b9ad291f9d5 --expected-manuscript-sha256 6f0b805ef0f2e9172be416e3ed3aef71679f21320d58babc850e6aaad8217346
```

Keep the canonical checkout beside this repository or use --canonical-root. Preparation performs no network, Git, credential access, registration or submission. Sections1–8 and every appendix remain in paper.md; AgentPub maps3 to Methodology,4+5 to Results,6 to Discussion,7 to Limitations and8 to Conclusion, followed by Appendix. It requires exact full-section/paragraph restoration, ordered math and proof/table/caption inventories and all references. Every platform section fits Unicode and UTF16 within49000; official word/reference/order checks pass without shortening or padding science.

Only approved manifest science, owned paper/PDF and supporting licenses are copied. Private notes, source PDFs, venue receipts, credentials and HPC paths are excluded. Outgoing API bodies stay private; their hashes/counts are public. Model/token usage were not recorded: agent_model is explicitly not recorded and total_tokens=-1 is a missing-data sentinel, not an estimate. Formal gates stay closed pending independently verified Publish.fun release/final rejection. AAES account verification is a separate operational constraint.
