"""Install samtools/bcftools into a project-local Linux environment without containers."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0/micromamba-linux-64"
DIGEST = "366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3"


def main():
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise SystemExit("This installer targets Eddie/Linux x86-64, not Windows.")
    if not os.environ.get("JOB_ID"):
        raise SystemExit("Run inside an allocated Eddie interactive session (qlogin), not the login node.")
    cache = ROOT / "cache"
    cache.mkdir(exist_ok=True)
    binary = cache / "micromamba-linux-64"
    if not binary.exists():
        partial = binary.with_suffix(".download")
        urllib.request.urlretrieve(URL, partial)
        if hashlib.sha256(partial.read_bytes()).hexdigest() != DIGEST:
            raise SystemExit("Micromamba checksum mismatch; retained download for investigation.")
        partial.rename(binary)
    if hashlib.sha256(binary.read_bytes()).hexdigest() != DIGEST:
        raise SystemExit("Existing Micromamba binary checksum mismatch.")
    binary.chmod(0o755)
    prefix = cache / "file-tools-env"
    env = os.environ.copy()
    env["MAMBA_ROOT_PREFIX"] = str(cache / "micromamba-root")
    common = [str(binary), "--no-rc", "-r", env["MAMBA_ROOT_PREFIX"]]
    if not all((prefix / "bin" / name).exists() for name in ("samtools", "bcftools")):
        operation = "install" if (prefix / "conda-meta").is_dir() else "create"
        subprocess.run(common + [operation, "-y", "-p", str(prefix), "--override-channels",
                       "--strict-channel-priority", "-c", "conda-forge", "-c", "bioconda",
                       "samtools=1.22", "bcftools=1.22"], env=env, check=True)
    versions = {}
    for name in ("samtools", "bcftools"):
        result = subprocess.run([str(prefix / "bin" / name), "--version"], capture_output=True, text=True, check=True)
        if result.stdout.splitlines()[0] != f"{name} 1.22":
            raise SystemExit(f"Unexpected {name} version; investigate before changing the environment.")
        versions[name] = result.stdout
        print(result.stdout.splitlines()[0])
    exported = subprocess.run(common + ["list", "-p", str(prefix), "--explicit"], env=env,
                              capture_output=True, text=True, check=True)
    (cache / "file-tools-explicit.txt").write_text(exported.stdout, encoding="utf-8")
    (cache / "file-tools-setup.json").write_text(json.dumps({"micromamba_url": URL,
        "micromamba_sha256": DIGEST, "versions": versions, "environment": str(prefix)}, indent=2) + "\n", encoding="utf-8")
    print("Preparation finished. Exit the interactive session, then submit qsub hpc/file-checks.qsub from the project root.")


if __name__ == "__main__":
    main()
