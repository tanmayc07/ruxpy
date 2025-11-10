use pyo3::types::PyDict;
use pyo3::{exceptions::PyRuntimeError, prelude::*};
use serde_json::{Map, Value};
use sha3::{Digest, Sha3_256};
use std::fs;
use std::path::Path;
use walkdir::WalkDir;

#[pyclass]
pub struct RuxpyTree;

fn hash_bytes(data: &[u8]) -> String {
    let mut h = Sha3_256::new();
    h.update(data);
    let hash = format!("{:x}", h.finalize());
    hash
}

// fn repo_join(repo: &Path, parts: &str) -> PathBuf {
//     repo.join(parts)
// }

#[pymethods]
impl RuxpyTree {
    /// Returns Tree JSON mapping relative paths -> Blob hash for "repo_path"
    #[staticmethod]
    pub fn build_tree(repo_path: &str) -> PyResult<String> {
        let repo = Path::new(repo_path);
        if !repo.exists() || !repo.is_dir() {
            return Err(PyRuntimeError::new_err(
                "repo_path does not exist or is not a directory",
            ));
        }

        let mut tree = Map::new();

        for entry in WalkDir::new(repo).into_iter().filter_map(|e| e.ok()) {
            let p = entry.path();
            if p.is_file() {
                // todo: integrate with .gitignore
                if p.starts_with(repo.join(".dock")) {
                    continue;
                }

                let rel = match p.strip_prefix(repo) {
                    Ok(r) => r,
                    Err(_) => continue,
                };
                let rel_str = rel
                    .to_string_lossy()
                    .replace(std::path::MAIN_SEPARATOR, "/");

                let bytes = match fs::read(p) {
                    Ok(b) => b,
                    Err(e) => {
                        return Err(PyRuntimeError::new_err(format!(
                            "Failed to read file {}: {}",
                            p.display(),
                            e
                        )))
                    }
                };

                let blob_hash = hash_bytes(&bytes);
                tree.insert(rel_str, Value::String(blob_hash));
            }
        }

        serde_json::to_string(&Value::Object(tree))
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to serialize tree: {}", e)))
    }

    #[staticmethod]
    pub fn build_tree_from_staged(staged_files: PyObject, repo_path: &str) -> PyResult<String> {
        let repo = Path::new(repo_path);
        if !repo.exists() || !repo.is_dir() {
            return Err(PyRuntimeError::new_err(
                "repo_path does not exist or is not a directory",
            ));
        }

        Python::with_gil(|py| {
            let mut tree = Map::new();

            let dict = staged_files.downcast_bound::<PyDict>(py)?;

            for (key, value) in dict.iter() {
                let file: String = key.extract()?;
                let blob: String = value.extract()?;
                tree.insert(file, Value::String(blob));
            }

            serde_json::to_string(&Value::Object(tree))
                .map_err(|e| PyRuntimeError::new_err(format!("Failed to serialize tree: {}", e)))
        })
    }

    /// Write tree JSON (string) into the object store
    #[staticmethod]
    pub fn write_tree_object(tree_json: &str, repo_path: &str) -> PyResult<String> {
        let repo = Path::new(repo_path);
        if !repo.exists() || !repo.is_dir() {
            return Err(PyRuntimeError::new_err(
                "repo_path does not exist or is not a directory",
            ));
        }

        let tree_hash = hash_bytes(tree_json.as_bytes());

        let objects_dir = repo.join(".dock").join("objects");
        let (prefix, rest) = tree_hash.split_at(2);
        let object_dir = objects_dir.join(prefix);
        let object_path = object_dir.join(rest);

        if let Err(e) = fs::create_dir_all(&object_dir) {
            return Err(PyRuntimeError::new_err(format!(
                "Failed to create objects dir: {}",
                e
            )));
        }

        if let Err(e) = fs::write(&object_path, tree_json) {
            return Err(PyRuntimeError::new_err(format!(
                "Failed to write tree object: {}",
                e
            )));
        }

        Ok(tree_hash)
    }
}

mod tests {
    #[allow(unused_imports)]
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    /// Creates a mock repo/spacedock with ".dock/objects" ready
    fn _setup_repo() -> TempDir {
        let dir = tempfile::tempdir().unwrap();
        fs::create_dir_all(dir.path().join(".dock/objects")).unwrap();
        let file_path = dir.path().join("sample.txt");
        fs::write(&file_path, b"hello world").unwrap();

        fs::write(dir.path().join("file1.txt"), b"hello").unwrap();
        fs::create_dir_all(dir.path().join("src")).unwrap();
        fs::write(dir.path().join("src/main.rs"), b"fn main() {}").unwrap();
        dir
    }

    #[test]
    fn test_build_tree() {
        let repo = _setup_repo();
        let repo_path = repo.path();

        let tree_json = RuxpyTree::build_tree(repo_path.to_str().unwrap()).unwrap();

        let parsed: Value = serde_json::from_str(&tree_json).unwrap();
        let obj = parsed.as_object().unwrap();

        assert!(obj.contains_key("file1.txt"));
        assert!(obj.contains_key("src/main.rs"));

        let file_bytes = fs::read(repo_path.join("file1.txt")).unwrap();
        let expected_hash = {
            use sha3::{Digest, Sha3_256};
            let mut h = Sha3_256::new();
            h.update(&file_bytes);
            let hash = format!("{:x}", h.finalize());
            hash
        };

        let actual_hash = obj.get("file1.txt").unwrap().as_str().unwrap();
        assert_eq!(actual_hash, expected_hash);
    }

    #[test]
    fn test_build_tree_from_staged() {
        pyo3::prepare_freethreaded_python();
        let repo = _setup_repo();
        let repo_path = repo.path();

        Python::with_gil(|py| {
            let staged_files = PyDict::new(py);
            staged_files.set_item("file1.txt", "abc123").unwrap();
            staged_files.set_item("src/main.rs", "def456").unwrap();

            let staged_obj: Py<PyAny> = staged_files.into();

            let tree_json =
                RuxpyTree::build_tree_from_staged(staged_obj, repo_path.to_str().unwrap()).unwrap();

            let parsed: serde_json::Value = serde_json::from_str(&tree_json).unwrap();
            let obj = parsed.as_object().unwrap();

            assert_eq!(obj.get("file1.txt").unwrap().as_str().unwrap(), "abc123");
            assert_eq!(obj.get("src/main.rs").unwrap().as_str().unwrap(), "def456");
        });
    }

    #[test]
    fn test_write_tree_object() {
        let repo = _setup_repo();
        let repo_path = repo.path();

        let tree_json = RuxpyTree::build_tree(repo_path.to_str().unwrap()).unwrap();
        let tree_hash =
            RuxpyTree::write_tree_object(tree_json.as_str(), repo_path.to_str().unwrap()).unwrap();

        use sha3::{Digest, Sha3_256};
        let mut h = Sha3_256::new();
        h.update(tree_json.as_bytes());
        let expected_hash = format!("{:x}", h.finalize());
        assert_eq!(
            tree_hash, expected_hash,
            "tree hash should match expected SHA3_256"
        );

        let (prefix, rest) = tree_hash.split_at(2);
        let object_path = repo_path
            .join(".dock")
            .join("objects")
            .join(prefix)
            .join(rest);
        assert!(object_path.exists(), "tree object file should exist");

        let stored_contents = std::fs::read_to_string(&object_path).unwrap();
        assert_eq!(
            stored_contents, tree_json,
            "stored tree object contents should match original JSON"
        );
    }
}
