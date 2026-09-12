# Evidence provenance

The local component evidence was generated on 2026-09-11. This distributed
copy uses anonymised path prefixes: `<PROJECT_ROOT>` for the project location,
`<LOCAL_USER_HOME>` for the Windows home directory and, where needed,
`<HPC_USER>` for the HPC account identifier. The original private evidence is
retained unchanged. The initial path substitutions affected 24 copied files.

Documentation was revised on 2026-09-12. Review labels in the historical summary
and run metadata now use neutral technical-review terminology. Review remains
pending; no execution date, test assessment, numeric result, input/output hash
or upstream source byte was changed. The technical report was regenerated.

The historical run's `project_files_sha256` identifies the code used for that
run at repository revision `428d22b8ee46b8064e61a2e9814728b927711392`.
Subsequent changes to report wording and the deliberate unknown-parameter name
are recorded in Git. Historical code hashes are not rewritten to match newer
files. New executions record the code hashes they actually use.

`PUBLIC_EXPORT_MANIFEST.json` inventories the current distributed files,
records their SHA256 values and retains original local hashes where available.
It identifies files revised since the initial distribution and excludes itself
from its own hashes. Original hashes do not mean the current file is identical
to its original; compare `original_sha256` with `public_sha256`.
`.gitattributes` disables Git line-ending conversion to preserve hashed bytes.

Copied receipts are local provenance records, not signed attestations. Their
anonymised command paths are placeholders; use LOCAL_START.md to reproduce a
run. Large data, caches, virtual environments, work directories and private
machine settings are excluded from version control.

Dated local reports retain the status of the recorded environment. Later
GitHub Actions runs have their own commit IDs, logs and artifacts. Independent
technical review and the complete Nextflow workflow remain pending.
