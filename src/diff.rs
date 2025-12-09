use std::collections::{HashMap, HashSet};
use std::io::Read;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::fs::File;
use std::path::Path;

use crate::spacedock::Spacedock;
use crate::starlog::Starlog;
use crate::Blob;
use crate::{get_dockignore_matcher, get_tracked_files, is_ignored};

#[pyclass]
pub struct Diff;

impl Diff {
    fn search_new_files() -> Result<Vec<String>, String> {
        let current_dir_file_list = Spacedock::get_repository_files()?;

        // Staged files + Latest starlog object files
        let tracked_files = get_tracked_files().map_err(|e| format!("{}", e))?;

        let dockignore_matcher = get_dockignore_matcher();

        // Ignore files based on .dockignore and internal dir
        let new_files: Vec<String> = current_dir_file_list
            .into_iter()
            .filter(|path_str| {
                let path = std::path::Path::new(path_str);

                if path_str.contains(".dock") {
                    return false;
                }

                if is_ignored(path, &dockignore_matcher) {
                    return false;
                }

                if tracked_files.contains(path_str) {
                    return false;
                }

                true
            })
            .collect();

        Ok(new_files)
    }

    fn search_renamed_files() -> Result<Vec<String>, String> {
        let repo_path = Spacedock::find_dock_root(None).unwrap();
        // Get the new files list
        let new_files_list = Diff::search_new_files()?;
        let deleted_files_list: HashSet<String> =
            Diff::search_deleted_files()?.into_iter().collect();

        let latest_hash = Starlog::get_latest_starlog_hash_internal()?;
        let starlog_files_list = Starlog::load_starlog_files(&repo_path, &latest_hash)?;

        let deleted_hashes: HashMap<String, String> = starlog_files_list
            .into_iter()
            .filter(|(filename, _value)| deleted_files_list.contains(filename))
            .map(|(filename, value)| {
                let hash_string: String = value.as_str().unwrap().to_owned();
                (hash_string, filename)
            })
            .collect();

        let mut renamed_files = Vec::new();

        for new_path in new_files_list {
            let full_path = Path::new(&repo_path).join(&new_path);
            let mut file = File::open(&full_path).map_err(|e| format!("{}", e))?;
            let mut contents = Vec::new();
            file.read_to_end(&mut contents)
                .map_err(|e| format!("{}", e))?;

            let current_hash = Blob::hash_contents(&contents);

            if let Some(original_path) = deleted_hashes.get(&current_hash) {
                renamed_files.push(format!("{} -> {}", original_path, new_path));
            }
        }

        Ok(renamed_files)
    }

    fn search_deleted_files() -> Result<Vec<String>, String> {
        let current_dir_file_list = Spacedock::get_repository_files()?;

        let tracked_file_list = get_tracked_files().map_err(|e| format!("{}", e))?;

        let deleted_file_list = tracked_file_list
            .into_iter()
            .filter(|file| !current_dir_file_list.contains(file))
            .collect();

        Ok(deleted_file_list)
    }

    fn search_modified_files() -> Result<Vec<String>, String> {
        let repo_path = Spacedock::find_dock_root(None).unwrap();

        let tracked_files = get_tracked_files().map_err(|e| format!("{}", e))?;

        let latest_hash = Starlog::get_latest_starlog_hash_internal()?;
        let starlog_files_list = Starlog::load_starlog_files(&repo_path, &latest_hash)?;

        let mut modified_files = Vec::new();

        for path_str in tracked_files {
            let full_path = Path::new(&repo_path).join(&path_str);
            if !full_path.exists() {
                // The file is deleted, skip it
                // search_deleted_files() handles this case
                continue;
            }

            let recorded_hash = match starlog_files_list.get(&path_str) {
                Some(value) => value.as_str().unwrap().to_owned(),
                None => continue,
            };

            let mut file = File::open(&full_path).map_err(|e| format!("{}", e))?;
            let mut contents = Vec::new();
            file.read_to_end(&mut contents)
                .map_err(|e| format!("Failed to read: {}\n{}", path_str, e))?;

            let current_hash = Blob::hash_contents(&contents);

            if recorded_hash != current_hash {
                modified_files.push(path_str);
            }
        }

        Ok(modified_files)
    }
}

#[pymethods]
impl Diff {
    #[staticmethod]
    pub fn get_new_files() -> PyResult<Vec<String>> {
        let files = Diff::search_new_files()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get stage files: {}", e)))?;
        Ok(files)
    }

    #[staticmethod]
    pub fn get_renamed_files() -> PyResult<Vec<String>> {
        let files = Diff::search_renamed_files()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get renamed files: {}", e)))?;
        Ok(files)
    }

    #[staticmethod]
    pub fn get_deleted_files() -> PyResult<Vec<String>> {
        let files = Diff::search_deleted_files()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get deleted files: {}", e)))?;
        Ok(files)
    }

    #[staticmethod]
    pub fn get_modified_files() -> PyResult<Vec<String>> {
        let files = Diff::search_modified_files()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get modified files: {}", e)))?;
        Ok(files)
    }

    #[staticmethod]
    pub fn get_diff_between_two_starlogs() -> PyResult<()> {
        todo!()
    }

    #[staticmethod]
    pub fn get_diff_between_current_and_latest_starlog() -> PyResult<()> {
        todo!()
    }
}
