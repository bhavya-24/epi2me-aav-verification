"""Download the locked native SeqKit binary. No system installation or PATH edit."""
import hashlib
import json
import os
from pathlib import Path
import platform
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "Windows": ("seqkit_windows_amd64.exe.tar.gz", "seqkit.exe",
                "789a11df5306ae9d8cc0ccc9a11b76b6b8f44c31e6cc3ba3e4bc13db5819b1dd"),
    "Linux": ("seqkit_linux_amd64.tar.gz", "seqkit",
              "7d686de448464fada1b1988e2e07d693bec68768312da62846bc0e2b502bfc46"),
}


def main():
    if platform.machine().lower() not in ("amd64", "x86_64"):
        raise SystemExit("This setup locks x86-64 assets only.")
    asset, executable, expected = ASSETS[platform.system()]
    directory = ROOT / "cache" / "component-tools"
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / asset
    url = f"https://github.com/shenwei356/seqkit/releases/download/v2.13.0/{asset}"
    if not archive.exists():
        partial = directory / (asset + ".download")
        urllib.request.urlretrieve(url, partial)
        if hashlib.sha256(partial.read_bytes()).hexdigest() != expected:
            raise SystemExit("SeqKit checksum mismatch; download retained for investigation.")
        partial.rename(archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise SystemExit("Existing SeqKit archive checksum mismatch.")
    with tarfile.open(archive, "r:gz") as tar:
        candidates = [m for m in tar.getmembers() if Path(m.name).name == executable and m.isfile()]
        if len(candidates) != 1:
            raise SystemExit("Unexpected archive contents.")
        binary = tar.extractfile(candidates[0]).read()
    target = directory / executable
    if target.exists() and target.read_bytes() != binary:
        raise SystemExit("Existing SeqKit executable differs; investigate instead of replacing it.")
    target.write_bytes(binary)
    if os.name != "nt":
        target.chmod(0o755)
    receipt = {"version": "2.13.0", "url": url, "archive_sha256": expected,
               "digest_source": "GitHub release asset metadata, checked 2026-09-11",
               "executable_sha256": hashlib.sha256(binary).hexdigest()}
    (directory / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {target}")


if __name__ == "__main__":
    main()
