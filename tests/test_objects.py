import os
from ruxpy import init_object_dir, save_blob, read_blob


def test_object_store(tmp_path):
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)

    file_path = repo_path / "file1.txt"
    file_path.write_text("hello world")

    init_object_dir(str(repo_path))

    hash = save_blob(str(repo_path), "file1.txt")

    obj_path = repo_path / ".dock" / "objects" / hash[:2] / hash[2:]
    assert obj_path.exists()

    contents = read_blob(str(repo_path), hash)
    assert contents == b"hello world"

    try:
        read_blob(str(repo_path), "nonexistenthash")
        assert False, "Should have raised an error"
    except Exception:
        pass
