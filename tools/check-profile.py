"""Validate the public organization profile without network or runtime state."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profile/README.md"


def main() -> None:
    text = PROFILE.read_text(encoding="utf-8")
    if not text.startswith("# NDDev Platform\n"):
        raise SystemExit("profile: the organization introduction must name NDDev Platform")
    tracked = set(
        subprocess.check_output(
            ["git", "ls-files", "-z", "--", "profile"], cwd=ROOT
        ).decode().split("\0")
    )
    links = re.findall(r"(!?)\[[^\]]*\]\(([^)\s]+)\)", text)
    if not links:
        raise SystemExit("profile: the introduction has no links")
    assets = 0
    for image, target in links:
        url = urlsplit(target)
        if url.scheme == "mailto" and url.path:
            continue
        if url.scheme or url.netloc:
            if url.scheme != "https" or url.hostname != "nddev.ai" or url.username or url.password:
                raise SystemExit(f"profile: website link must use https://nddev.ai: {target}")
            continue
        asset = PROFILE.parent / unquote(url.path)
        resolved = asset.resolve()
        if not resolved.is_relative_to(ROOT) or resolved.relative_to(ROOT).as_posix() not in tracked:
            raise SystemExit(f"profile: local asset must be tracked inside this repository: {target}")
        if asset.is_symlink() or not asset.is_file():
            raise SystemExit(f"profile: local asset is not a regular file: {target}")
        if asset.suffix.lower() == ".png":
            with asset.open("rb") as stream:
                if stream.read(8) != b"\x89PNG\r\n\x1a\n":
                    raise SystemExit(f"profile: local PNG has an invalid signature: {target}")
        if image:
            assets += 1
    if assets == 0:
        raise SystemExit("profile: the introduction has no local cover asset")
    print(f"profile: identity, {len(links)} links and {assets} local asset(s) pass")


if __name__ == "__main__":
    main()
