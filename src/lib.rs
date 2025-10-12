mod courses;

use crate::courses::Courses;
use ignore::gitignore::{Gitignore, GitignoreBuilder};
use pyo3::prelude::*;
use sha3::{Digest, Sha3_256};
use std::fs::{self, File};
use std::io::Read;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[pyfunction]
fn init_object_dir(repo_path: &str) -> PyResult<()> {
    let obj_dir: std::path::PathBuf = Path::new(repo_path).join(".dock").join("objects");
    fs::create_dir_all(&obj_dir)?;
    Ok(())
}

#[pyfunction]
fn save_blob(repo_path: &str, file_path: &str) -> PyResult<String> {
    let full_path = Path::new(repo_path).join(file_path);
    let mut file = File::open(&full_path)?;
    let mut contents = Vec::new();
    file.read_to_end(&mut contents)?;

    // Hash the contents
    let mut hasher = Sha3_256::new();
    hasher.update(&contents);
    let hash = format!("{:x}", hasher.finalize());

    let (subdir, filename) = hash.split_at(2);
    let obj_path = Path::new(repo_path).join(".dock").join("objects");
    let dir_path = Path::new(&obj_path).join(subdir);
    fs::create_dir_all(&dir_path)?;
    let file_path = dir_path.join(filename);

    // Write to objects directory
    fs::write(file_path, contents)?;

    Ok(hash)
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
fn read_blob(repo_path: &str, hash: &str) -> PyResult<Vec<u8>> {
    let (subdir, filename) = hash.split_at(2);
    let obj_path = Path::new(repo_path).join(".dock").join("objects");
    let file_path = Path::new(&obj_path).join(subdir).join(filename);
    let contents = fs::read(file_path)?;
    Ok(contents)
}

#[pyfunction]
fn find_dock_root(start_path: Option<String>) -> PyResult<Option<String>> {
    let mut current = match start_path {
        Some(path) => PathBuf::from(path),
        None => std::env::current_dir().unwrap(),
    };

    loop {
        if current.join(".dock").exists() {
            return Ok(Some(current.to_string_lossy().to_string()));
        }

        if !current.pop() {
            break;
        }
    }
    Ok(None)
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
fn get_dockignore_matcher() -> Option<Gitignore> {
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
fn is_ignored(path: &Path, matcher: &Option<Gitignore>) -> bool {
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

/// A Python module implemented in Rust.
#[pymodule]
fn ruxpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_object_dir, m)?)?;
    m.add_function(wrap_pyfunction!(save_blob, m)?)?;
    m.add_function(wrap_pyfunction!(read_blob, m)?)?;
    m.add_function(wrap_pyfunction!(save_starlog, m)?)?;
    m.add_function(wrap_pyfunction!(find_dock_root, m)?)?;
    m.add_function(wrap_pyfunction!(list_all_files, m)?)?;
    m.add_function(wrap_pyfunction!(filter_ignored_files, m)?)?;
    m.add_class::<Courses>()?;
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
