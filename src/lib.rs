mod blob;
mod courses;
mod diff;
mod ruxpy_tree;
mod spacedock;
mod starlog;

use crate::blob::Blob;
use crate::courses::Courses;
use crate::diff::Diff;
use crate::ruxpy_tree::RuxpyTree;
use crate::spacedock::Spacedock;
use crate::spacedock::PATHS;
use crate::starlog::Starlog;

use ignore::gitignore::{Gitignore, GitignoreBuilder};
use pyo3::prelude::*;
use sha3::{Digest, Sha3_256};
use std::collections::HashSet;
use std::fs;
use std::path::Path;
use walkdir::WalkDir;

#[pyfunction]
fn init_object_dir(repo_path: &str) -> PyResult<()> {
    let obj_dir: std::path::PathBuf = Path::new(repo_path).join(".dock").join("objects");
    fs::create_dir_all(&obj_dir)?;
    Ok(())
}

#[pyfunction]
fn save_starlog(repo_path: &str, starlog_bytes: Vec<u8>) -> PyResult<String> {
    let mut hasher = Sha3_256::new();
    hasher.update(&starlog_bytes);
    let hash = format!("{:x}", hasher.finalize());

    let (subdir, filename) = hash.split_at(2);
    let starlog_dir = Path::new(repo_path)
        .join(".dock")
        .join("starlogs")
        .join(subdir);
    fs::create_dir_all(&starlog_dir)?;
    let starlog_path = starlog_dir.join(filename);

    fs::write(starlog_path, &starlog_bytes)?;

    Ok(hash)
}

#[pyfunction]
fn list_all_files(working_dir: &str) -> PyResult<Vec<String>> {
    let matcher = get_dockignore_matcher();
    let base = Path::new(working_dir);
    let files = WalkDir::new(base)
        .into_iter()
        .filter_map(|entry| {
            entry.ok().and_then(|e| {
                let path = e.path();
                // Skip internal directories
                let path_str = path.to_string_lossy();
                if path_str.contains(".dock")
                    || path_str.contains("__pycache__")
                    || path_str.contains(".git")
                {
                    return None;
                }

                if e.file_type().is_file() {
                    // Get relative path
                    if let Ok(rel_path) = path.strip_prefix(base) {
                        if is_ignored(rel_path, &matcher) {
                            return None;
                        }
                        return Some(rel_path.to_string_lossy().to_string());
                    }
                    None
                } else {
                    None
                }
            })
        })
        .collect();
    Ok(files)
}

/// Reads .dockignore from the current directory and returns a matcher.
pub fn get_dockignore_matcher() -> Option<Gitignore> {
    let dockignore_path = Path::new(".dockignore");
    if dockignore_path.exists() {
        let mut builder = GitignoreBuilder::new(".");
        builder.add(dockignore_path);
        let gitignore = builder
            .build()
            .map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to parse .dockignore: {e}"))
            })
            .ok()?;
        Some(gitignore)
    } else {
        None
    }
}

/// Check if path should be ignored
pub fn is_ignored(path: &Path, matcher: &Option<Gitignore>) -> bool {
    if let Some(gitignore) = matcher {
        gitignore.matched(path, false).is_ignore()
    } else {
        false
    }
}

#[pyfunction]
fn filter_ignored_files(files: Vec<String>) -> PyResult<Vec<String>> {
    let matcher = get_dockignore_matcher();
    let mut result = Vec::new();
    for path_str in files.iter() {
        let path = std::path::Path::new(&path_str);
        if !is_ignored(path, &matcher) {
            result.push(path_str.to_string());
        }
    }
    Ok(result)
}

#[pyfunction]
pub fn get_tracked_files() -> PyResult<HashSet<String>> {
    // Helpful closure for error handling
    let map_err_to_py = |e: String| pyo3::exceptions::PyIOError::new_err(e);

    // Get staged files as list
    let stage_path = PATHS
        .iter()
        .find(|&x| x.key == "stage")
        .ok_or_else(|| pyo3::exceptions::PyIOError::new_err("Stage path not found in PATHS."))?;
    let stage_file_list = Courses::load_stage_files(stage_path.path).map_err(map_err_to_py)?;

    // Get latest starlog object files as list
    let latest_starlog_hash = Starlog::get_latest_starlog_hash_internal().map_err(map_err_to_py)?;
    let starlog_object_map =
        Starlog::load_starlog_files(".", &latest_starlog_hash).map_err(map_err_to_py)?;
    let starlog_file_list: Vec<String> = starlog_object_map.into_keys().collect();

    // Combine staged files and latest starlog object files as list
    let tracked_files: HashSet<String> = stage_file_list
        .into_iter()
        .chain(starlog_file_list)
        .collect();

    Ok(tracked_files)
}

/// A Python module implemented in Rust.
#[pymodule]
fn ruxpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_object_dir, m)?)?;
    m.add_function(wrap_pyfunction!(save_starlog, m)?)?;
    m.add_function(wrap_pyfunction!(list_all_files, m)?)?;
    m.add_function(wrap_pyfunction!(filter_ignored_files, m)?)?;
    m.add_class::<Spacedock>()?;
    m.add_class::<Courses>()?;
    m.add_class::<Blob>()?;
    m.add_class::<Starlog>()?;
    m.add_class::<RuxpyTree>()?;
    m.add_class::<Diff>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_list_course_names() {
        // Setup
        let temp_dir = tempfile::tempdir().unwrap();
        let helm_dir = temp_dir.path().join("links/helm");
        fs::create_dir_all(&helm_dir).unwrap();

        // create course files
        let courses = vec!["main", "core", "feat-x", "bugfix", "feat-y"];
        for course in &courses {
            let course_path = helm_dir.join(course);
            fs::write(&course_path, "dummyhash").unwrap();
        }

        let result = Courses::list_all(&helm_dir.to_string_lossy());

        for course in &courses {
            assert!(result.contains(&course.to_string()));
        }
        assert_eq!(result.len(), courses.len())
    }
}
