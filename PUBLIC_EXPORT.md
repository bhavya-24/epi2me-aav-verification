# Public evidence copy

Prepared 2026-09-12 from the local project; no GitHub publication is implied.

The original execution evidence is retained unchanged in the private working
project. This copy replaces the workstation's project-directory prefix with
`<PROJECT_ROOT>`, the Windows home prefix with `<LOCAL_USER_HOME>` and, if
present, the HPC account identifier with `<HPC_USER>`.
Both plain-text and JSON-escaped paths are handled. There are 24
changed files. The replacement map deliberately omits the private values.

Numeric results, exit codes, timestamps, diagnostics apart from their path
prefixes, and source/input/output hash fields are unchanged. The included
upstream source and licence bytes are unchanged. Public receipts are redacted
copies, not byte-identical originals or signed attestations. Their command
paths are provenance placeholders; use LOCAL_START.md to reproduce the runs.

PUBLIC_EXPORT_MANIFEST.json lists original and public SHA256 values and the
replacement count for each copied file. It records additional generated files
separately and excludes itself from its own hashes. .gitattributes disables
Git line-ending conversion to preserve the bytes checked by these manifests.

Large data, caches, virtual environments, work directories, personal machine
setup files and unrelated application documents are excluded. The runnable
synthetic fixtures, test evidence, documentation and case study are included.

The original run is dated 2026-09-11. CI, the full Nextflow workflow, external
file tools and applicant/peer review remain pending as described in README.md.
Future runs must retain their own dates and statuses.
