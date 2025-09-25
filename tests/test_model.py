import os, json, pytest
from pathlib import Path

import defs, model

class FakeScandir:
    def __init__(self, entries):
        self._entries = entries

    def __enter__(self):
        res = []
        for entry_path in self._entries:
            p = Path(entry_path)
            parent = str(p.parent)
            found = False
            for de in os.scandir(parent):
                if de.name == p.name:
                    res.append(de)
                    found = True
                    break
            if not found:
                raise FileNotFoundError(f"scandir could not find {entry_path}")
        return res

    def __exit__(self, exc_type, exc, tb):
        return False

class FakeTag:
    SUPPORTED_FILE_EXTENSIONS = {".mp3", ".flac"}

    def __init__(self, artist, album, title):
        self.artist = artist
        self.album = album
        self.title = title

    @classmethod
    def get(cls, path):
        stem = Path(path).stem
        return FakeTag(artist="ArtistX", album="AlbumA", title=stem)

@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    # ensure defs globals are initialized and basepath points to tmp_path
    defs.basepath           = str(tmp_path)
    defs.percent_complete   = 0
    defs.cancel_request     = False
    
    model.music.clear()

    # monkeypatch replace to emulate os.replace semantics and handle backslashes
    def fake_replace(src, dst):
        src_path = Path(src)
        dst_path = Path(str(dst).replace("\\", os.sep))
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.replace(dst_path)

    monkeypatch.setattr(model, "replace", fake_replace)
    yield
    # teardown
    defs.cancel_request = False
    defs.confiriming_quit = False
    model.music.clear()

def test_index_files_and_structure(tmp_path, monkeypatch):
    f1 = tmp_path / "song1.mp3"
    f2 = tmp_path / "song2.flac"
    f3 = tmp_path / "ignore.txt"
    f1.write_text("a")
    f2.write_text("b")
    f3.write_text("c")

    entries = [str(f1), str(f2), str(f3)]

    monkeypatch.setattr(model, "scandir", lambda base: FakeScandir(entries))
    monkeypatch.setattr(model, "TinyTag", FakeTag)

    indexed = model.index_files()

    assert indexed == 2
    assert "ArtistX" in model.music
    assert "AlbumA" in model.music["ArtistX"]
    names = [t["name"] for t in model.music["ArtistX"]["AlbumA"]]
    assert set(names) == {"song1", "song2"}
    assert pytest.approx(defs.percent_complete, rel=1e-3) == 0.333

def test_move_files_moves_and_updates_progress(tmp_path, monkeypatch):
    f1 = tmp_path / "s1.mp3"
    f2 = tmp_path / "s2.flac"
    f1.write_text("x")
    f2.write_text("y")
    entries = [str(f1), str(f2)]

    monkeypatch.setattr(model, "scandir", lambda base: FakeScandir(entries))
    monkeypatch.setattr(model, "TinyTag", FakeTag)

    num = model.index_files()
    assert num == 2

    model.move_files(num)

    dest1 = Path(defs.basepath) / "ArtistX" / "AlbumA" / "s1.mp3"
    dest2 = Path(defs.basepath) / "ArtistX" / "AlbumA" / "s2.flac"

    assert dest1.exists()
    assert dest2.exists()
    assert pytest.approx(defs.percent_complete, rel=1e-3) == 0.999

def test_output_json_writes_expected_index(tmp_path, monkeypatch):
    f1 = tmp_path / "one.mp3"
    f2 = tmp_path / "two.flac"
    f1.write_text("x")
    f2.write_text("y")
    entries = [str(f1), str(f2)]

    monkeypatch.setattr(model, "scandir", lambda base: FakeScandir(entries))
    monkeypatch.setattr(model, "TinyTag", FakeTag)

    model.index_files()
    defs.json_out = True

    model.output_json()

    json_path = Path(defs.basepath) / "music_index.json"
    assert json_path.exists()

    data = json.loads(json_path.read_text())
    assert "ArtistX" in data
    assert "AlbumA" in data["ArtistX"]
    assert set(data["ArtistX"]["AlbumA"]) == {"one", "two"}

def test_check_canceled_raises_on_cancel():
    defs.cancel_request = True
    with pytest.raises(SystemExit):
        model.check_canceled("test cancel")