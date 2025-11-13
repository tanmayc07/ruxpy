use pyo3::types::PyDict;
use pyo3::{exceptions::PyRuntimeError, prelude::*};
use serde_json::{Map, Value};
use sha3::{Digest, Sha3_256};
use std::collections::HashSet;
use std::fs;
use std::path::Path;
use walkdir::WalkDir;

use crate::starlog::Starlog;

#[pyclass]
pub struct RuxpyTree;

fn hash_bytes(data: &[u8]) -> String {
    let mut h = Sha3_256::new();
    h.update(data);
    let hash = format!("{:x}", h.finalize());
    hash
}

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

    /// Returns tree JSON mapping but only for files that are staged
    #[staticmethod]
    pub fn build_tree_from_staged(
        staged_files: PyObject,
        starlog_hash: Option<String>,
        repo_path: &str,
    ) -> PyResult<String> {
        let repo = Path::new(repo_path);
        if !repo.exists() || !repo.is_dir() {
            return Err(PyRuntimeError::new_err(
                "repo_path does not exist or is not a directory",
            ));
        }

        Python::with_gil(|py| {
            let mut tree = Map::new();

            let staged = staged_files.downcast_bound::<PyDict>(py)?;

            // insert latest starlog's files first
            if let Some(hash) = starlog_hash {
                let parent_starlog_obj =
                    Starlog::load_starlog_object(&hash).map_err(PyRuntimeError::new_err)?;

                let parent_hash = parent_starlog_obj
                    .as_object()
                    .and_then(|obj| obj.get("parent"))
                    .and_then(|v| v.as_str());

                let parent_files = Starlog::load_parent_starlog_files(parent_hash)
                    .map_err(PyRuntimeError::new_err)?;

                if let Some(file_map) = parent_files.as_object() {
                    for (key, value) in file_map.iter() {
                        tree.insert(key.to_owned(), Value::String(value.to_string()));
                    }
                }
            }

            for (key, value) in staged.iter() {
                let file: String = key.extract()?;
                let blob: String = value.extract()?;
                tree.insert(file, Value::String(blob));
            }

            serde_json::to_string(&Value::Object(tree))
                .map_err(|e| PyRuntimeError::new_err(format!("Failed to serialize tree: {}", e)))
        })
    }

    /// Load a tree object by hash from the object store and return its JSON string.
    #[staticmethod]
    pub fn load_tree(tree_hash: &str, repo_path: &str) -> PyResult<String> {
        if tree_hash.len() < 3 {
            return Err(PyRuntimeError::new_err("Invalid tree hash"));
        }

        let repo = Path::new(repo_path);
        let objects_dir = repo.join(".dock").join("objects");
        let (prefix, rest) = tree_hash.split_at(2);
        let object_path = objects_dir.join(prefix).join(rest);

        let contents = fs::read_to_string(&object_path)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to read tree object: {}", e)))?;

        Ok(contents)
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

    /// Perform warp to course from tree perspective - create/remove files and dirs to sync the project state
    #[staticmethod]
    pub fn warp_to_course(tree_hash: &str, repo_path: &str) -> PyResult<()> {
        let tree_json = RuxpyTree::load_tree(tree_hash, repo_path)?;
        let parsed: Value = serde_json::from_str(&tree_json)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse tree JSON: {}", e)))?;

        let repo = Path::new(repo_path);

        let obj = parsed
            .as_object()
            .ok_or_else(|| PyRuntimeError::new_err("Tree JSON is not an object"))?;

        let mut tree_paths: HashSet<String> = HashSet::new();
        for (rel_path, v) in obj.iter() {
            if v.is_string() {
                let normalized = rel_path.replace(std::path::MAIN_SEPARATOR, "/");
                tree_paths.insert(normalized);
            }
        }

        // remove files in working dir that are NOT present in tree
        for entry in WalkDir::new(repo).into_iter().filter_map(|e| e.ok()) {
            let p = entry.path();
            if p.is_file() {
                // todo: extend to also check .gitignore paths
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
                if !tree_paths.contains(&rel_str) {
                    fs::remove_file(p).map_err(|e| {
                        PyRuntimeError::new_err(format!(
                            "Failed to remove file {}: {}",
                            p.display(),
                            e
                        ))
                    })?;
                }
            }
        }

        // Remove empty directories
        let mut dirs: Vec<std::path::PathBuf> = WalkDir::new(repo)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_dir())
            .map(|e| e.into_path())
            .collect();
        dirs.sort_by_key(|p| std::cmp::Reverse(p.components().count()));
        for dir in dirs {
            if dir == repo.join(".dock") || dir.starts_with(repo.join(".dock")) {
                continue;
            }
            if dir == repo {
                continue;
            }
            if let Ok(mut rd) = fs::read_dir(&dir) {
                if rd.next().is_none() {
                    let _ = fs::remove_dir(&dir);
                }
            }
        }

        // create files from tree
        for (rel_path, v) in obj.iter() {
            if let Some(blob_hash) = v.as_str() {
                let prefix = &blob_hash[..2];
                let rest = &blob_hash[2..];
                let blob_path = repo.join(".dock").join("objects").join(prefix).join(rest);

                if !blob_path.exists() {
                    return Err(PyRuntimeError::new_err(format!(
                        "Blob {} missing in object store",
                        blob_hash
                    )));
                }

                let dest = repo.join(rel_path);
                if let Some(parent) = dest.parent() {
                    if let Err(e) = fs::create_dir_all(parent) {
                        return Err(PyRuntimeError::new_err(format!(
                            "Failed to create parent dir {}: {}",
                            parent.display(),
                            e
                        )));
                    }
                }

                let data = fs::read(&blob_path).map_err(|e| {
                    PyRuntimeError::new_err(format!("Failed to read blob {}: {}", blob_hash, e))
                })?;
                fs::write(&dest, &data).map_err(|e| {
                    PyRuntimeError::new_err(format!(
                        "Failed to write file {}: {}",
                        dest.display(),
                        e
                    ))
                })?;
            }
        }

        Ok(())
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
                RuxpyTree::build_tree_from_staged(staged_obj, None, repo_path.to_str().unwrap())
                    .unwrap();

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
