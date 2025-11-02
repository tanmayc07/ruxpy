use pyo3::conversion::IntoPyObjectExt;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde_json::Value;
use std::path::{Path, PathBuf};
use std::str;
use std::{collections::HashMap, fs};

use crate::spacedock::{Spacedock, PATHS};

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

    pub fn load_starlog_files(
        base_path: &str,
        starlog_hash: &str,
    ) -> Result<HashMap<String, Value>, String> {
        let dock_path = PATHS
            .iter()
            .find(|info| info.key == "dock")
            .map(|info| Path::new(base_path).join(info.path))
            .ok_or_else(|| "Dock path not found in PATHS".to_string())?;

        let obj_file = dock_path
            .join("starlogs")
            .join(&starlog_hash[0..2])
            .join(&starlog_hash[2..]);

        if !obj_file.is_file() {
            return Err("FileNotFound Error".to_string());
        }

        let file_content =
            fs::read_to_string(&obj_file).map_err(|e| format!("Failed to read file: {}", e))?;
        let starlog_obj: Value = serde_json::from_str(&file_content)
            .map_err(|e| format!("Failed to parse JSON: {}", e))?;

        match starlog_obj.get("files") {
            Some(files) if files.is_object() => {
                Ok(files.as_object().unwrap().clone().into_iter().collect())
            }
            _ => Ok(HashMap::new()),
        }
    }
}

#[pymethods]
impl Starlog {
    #[staticmethod]
    fn get_latest_starlog_hash() -> PyResult<String> {
        Starlog::get_latest_starlog_hash_internal()
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    #[staticmethod]
    fn load_starlog_files_py(
        py: Python,
        base_path: &str,
        starlog_hash: &str,
    ) -> PyResult<PyObject> {
        let files_map = Starlog::load_starlog_files(base_path, starlog_hash)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)?;

        let py_dict = PyDict::new(py);
        for (key, value) in files_map {
            // Convert serde_json::Value to Python object
            let py_value = serde_json_to_pyobject(py, &value)?;
            py_dict.set_item(key, py_value)?;
        }
        Ok(py_dict.into())
    }
}

fn serde_json_to_pyobject(py: Python, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(b.into_py_any(py)?),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_py_any(py)?)
            } else if let Some(u) = n.as_u64() {
                Ok(u.into_py_any(py)?)
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_py_any(py)?)
            } else {
                Err(pyo3::exceptions::PyTypeError::new_err("Invalid number"))
            }
        }
        Value::String(s) => Ok(s.into_py_any(py)?),
        Value::Array(arr) => {
            let py_list = pyo3::types::PyList::empty(py);
            for v in arr {
                py_list.append(serde_json_to_pyobject(py, v)?)?;
            }
            Ok(py_list.into())
        }
        Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (k, v) in obj {
                py_dict.set_item(k, serde_json_to_pyobject(py, v)?)?;
            }
            Ok(py_dict.into())
        }
    }
}
