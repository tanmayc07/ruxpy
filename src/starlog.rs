use pyo3::prelude::*;
use std::fs;
use std::path::PathBuf;
use std::str;

use crate::spacedock::Spacedock;

#[pyclass]
pub struct Starlog;

impl Starlog {
    pub fn get_latest_starlog_hash_internal() -> Result<String, String> {
        let helm_file_path = Spacedock::get_path_info_internal("helm_f")
            .ok_or_else(|| "Cannot get helm file path".to_string())?;
        let helm_file = PathBuf::from(helm_file_path.path);
        let helm_contents =
            fs::read_to_string(helm_file).map_err(|_| "HELM read failed".to_string())?;
        let branch_path = helm_contents.trim();

        if branch_path.starts_with("link:") {
            let course_file = branch_path
                .split("link:")
                .nth(1)
                .ok_or("HELM malformed")?
                .trim();
            let course_path = PathBuf::from(
                Spacedock::get_path_info_internal("dock")
                    .ok_or_else(|| "Cannot get dock dir info".to_string())?
                    .path,
            )
            .join(course_file);

            if course_path.exists() && course_path.is_file() {
                let hash_contents = fs::read_to_string(course_path)
                    .map_err(|_| "course read failed".to_string())?;
                let latest_starlog_hash = hash_contents.trim();

                if latest_starlog_hash.is_empty() {
                    return Err(
                        "No Starlog entry yet. Please use `ruxpy starlog` to make an entry."
                            .to_string(),
                    );
                }

                return Ok(latest_starlog_hash.to_string());
            } else {
                return Err("course does not exist".to_string());
            }
        }
        Err("HELM file does not point to a course".to_string())
    }
}

#[pymethods]
impl Starlog {
    #[staticmethod]
    fn get_latest_starlog_hash() -> PyResult<String> {
        Starlog::get_latest_starlog_hash_internal()
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }
}
