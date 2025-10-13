use crate::spacedock::{HELM_DIR, HELM_FILE};
use crate::starlog::Starlog;
use pyo3::prelude::*;
use std::{fs, path::PathBuf};
use walkdir::WalkDir;

#[pyclass]
pub struct Courses;

impl Courses {
    pub fn current_internal(path: &str) -> String {
        let contents = fs::read_to_string(path).expect("Failed to read current course file");
        let mut parts = contents.splitn(2, ':');
        let current_course = parts.nth(1).unwrap();
        let current_course_name = current_course.trim().rsplit('/').next().unwrap();
        current_course_name.to_string()
    }
}

#[pymethods]
impl Courses {
    #[staticmethod]
    pub fn list_all(dir_path: &str) -> Vec<String> {
        let files = WalkDir::new(dir_path)
            .min_depth(1)
            .max_depth(1)
            .into_iter()
            .filter_map(|entry| {
                entry.ok().and_then(|e| {
                    if e.file_type().is_file() {
                        e.file_name().to_str().map(|s| s.to_string())
                    } else {
                        None
                    }
                })
            })
            .collect();
        files
    }

    #[staticmethod]
    pub fn current(path: &str) -> String {
        Courses::current_internal(path)
    }

    #[staticmethod]
    pub fn get_courses_and_current(
        helm_path: &str,
        current_course_path: &str,
    ) -> PyResult<(Vec<String>, String)> {
        let courses = Courses::list_all(helm_path);
        let current = Courses::current(current_course_path);
        Ok((courses, current))
    }

    #[staticmethod]
    pub fn create_course(name: &str) -> PyResult<()> {
        let course_path = PathBuf::from(HELM_DIR).join(name);
        match Starlog::get_latest_starlog_hash_internal() {
            Ok(latest_starlog_hash) => {
                fs::write(course_path, latest_starlog_hash)?;
                Ok(())
            }
            Err(msg) => Err(pyo3::exceptions::PyRuntimeError::new_err(msg)),
        }
    }

    #[staticmethod]
    pub fn delete_course(name: &str) -> PyResult<()> {
        let current_course = Courses::current_internal(HELM_FILE);
        if current_course == name {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Warp to a different course first",
            ));
        }
        if name == "core" {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cannot delete course core",
            ));
        }
        // delete name course
        match fs::remove_file(PathBuf::from(HELM_DIR).join(name)) {
            Ok(()) => Ok(()),
            Err(msg) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "{:?}",
                msg
            ))),
        }
    }
}
