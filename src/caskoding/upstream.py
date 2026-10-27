"""Download and unpack the pinned upstream fonts."""

import hashlib
import shutil
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from caskoding.variants import VARIANTS


@dataclass(frozen=True)
class Source:
    url: str
    sha256: str
    members: tuple[str, ...]  # glob patterns over full archive paths
    subdir: str


CASCADIA = Source(
    url="https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/CascadiaMono.tar.xz",
    sha256="e4fe0248bbe2558e907d26b55ed287403972f946239a4ea3f7a8afd3365ad6ba",
    members=(*(v.latin_file for v in VARIANTS), "LICENSE"),
    subdir="cascadia",
)

D2CODING = Source(
    url="https://github.com/naver/d2-coding-font/releases/download/VER1.4.0/D2Coding-Ver1.4.0-20261003.zip",
    sha256="17e2da5e2879006eb725b87943f7988736ef8b6c9f8b84bc8e3bdbcb8dd46744",
    members=("D2Coding/*.ttf", "OFL.txt"),
    subdir="d2coding",
)

JULIAMONO = Source(
    url="https://github.com/cormullion/juliamono/releases/download/v0.63.2/JuliaMono-ttf.zip",
    sha256="bc7140ccf1cbd84ee66a4c00a41628ee0a531a241e521773bad25a10c5066795",
    members=(*(v.symbols_file for v in VARIANTS), "LICENSE"),
    subdir="juliamono",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(source: Source, cache_dir: Path) -> Path:
    """Download the archive unless a copy with the right checksum is cached."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / source.url.rsplit("/", 1)[-1]
    if archive.exists() and _sha256(archive) == source.sha256:
        return archive

    archive.unlink(missing_ok=True)
    urllib.request.urlretrieve(source.url, archive)
    actual = _sha256(archive)
    if actual != source.sha256:
        archive.unlink()
        raise ValueError(f"sha256 mismatch for {source.url}: expected {source.sha256}, got {actual}")
    return archive


def extract(source: Source, archive: Path, upstream_dir: Path) -> Path:
    """Unpack matching members, flattened, into a fresh upstream_dir/subdir."""
    out = upstream_dir / source.subdir
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    def wanted(name: str) -> bool:
        return any(fnmatch(name, pattern) for pattern in source.members)

    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            for name in zf.namelist():
                if not name.endswith("/") and wanted(name):
                    (out / Path(name).name).write_bytes(zf.read(name))
    else:
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                if member.isfile() and wanted(member.name):
                    (out / Path(member.name).name).write_bytes(tar.extractfile(member).read())
    return out


def ensure_upstream(upstream_dir: Path = Path("upstream")) -> tuple[Path, Path, Path]:
    """Fetch and unpack the upstream fonts; return (cascadia_dir, d2coding_dir, juliamono_dir)."""
    cache = upstream_dir / "archives"
    cascadia, d2coding, juliamono = (
        extract(source, fetch(source, cache), upstream_dir)
        for source in (CASCADIA, D2CODING, JULIAMONO)
    )
    return cascadia, d2coding, juliamono
