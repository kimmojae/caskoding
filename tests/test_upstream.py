import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from caskoding.upstream import Source, extract, fetch


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_tar_xz(path: Path, files: dict[str, bytes]) -> Path:
    with tarfile.open(path, "w:xz") as tar:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


def _make_zip(path: Path, files: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return path


def _source(archive: Path, sha256: str | None = None, members=("*",)) -> Source:
    return Source(
        url=archive.as_uri(),
        sha256=sha256 or _sha256(archive),
        members=members,
        subdir="out",
    )


def test_fetch_downloads_and_verifies(tmp_path):
    archive = _make_tar_xz(tmp_path / "src.tar.xz", {"a.ttf": b"font"})
    cache = tmp_path / "cache"

    result = fetch(_source(archive), cache)

    assert result == cache / "src.tar.xz"
    assert result.read_bytes() == archive.read_bytes()


def test_fetch_redownloads_corrupt_archive(tmp_path):
    archive = _make_tar_xz(tmp_path / "src.tar.xz", {"a.ttf": b"font"})
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "src.tar.xz").write_bytes(b"half a download")

    result = fetch(_source(archive), cache)

    assert result.read_bytes() == archive.read_bytes()


def test_fetch_rejects_checksum_mismatch(tmp_path):
    archive = _make_tar_xz(tmp_path / "src.tar.xz", {"a.ttf": b"font"})

    with pytest.raises(ValueError, match="sha256"):
        fetch(_source(archive, sha256="0" * 64), tmp_path / "cache")


def test_extract_tar_and_zip_flattens_matching_members(tmp_path):
    tar = _make_tar_xz(
        tmp_path / "c.tar.xz",
        {"a/X-1.ttf": b"x", "LICENSE": b"l", "skip.txt": b"s"},
    )
    zf = _make_zip(
        tmp_path / "d.zip",
        {"D2Coding/Y.ttf": b"y", "OFL.txt": b"o", "Other/Z.ttf": b"z"},
    )

    tar_dir = extract(_source(tar, members=("*X-*.ttf", "LICENSE")), tar, tmp_path / "up1")
    zip_dir = extract(_source(zf, members=("D2Coding/*.ttf", "OFL.txt")), zf, tmp_path / "up2")

    assert sorted(p.name for p in tar_dir.iterdir()) == ["LICENSE", "X-1.ttf"]
    assert sorted(p.name for p in zip_dir.iterdir()) == ["OFL.txt", "Y.ttf"]
    assert (tar_dir / "X-1.ttf").read_bytes() == b"x"
