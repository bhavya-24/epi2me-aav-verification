"""Run the unmodified upstream CLI from the vendored, hash-checked source subset."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "upstream" / "bin"))
from workflow_glue import cli

if __name__ == "__main__":
    cli()
