use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::{env, path::Path};

pub enum PathKind {
    File,
    Dir,
}

impl PathKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            PathKind::Dir => "Dir",
            PathKind::File => "File",
        }
    }
}

pub struct PathInfo {
    pub key: &'static str,
    pub path: &'static str,
    pub kind: PathKind,
}

pub const PATHS: &[PathInfo] = &[
    PathInfo {
        key: "dock",
        path: ".dock",
        kind: PathKind::Dir,
    },
    PathInfo {
        key: "objects",
        path: ".dock/objects",
        kind: PathKind::Dir,
    },
    PathInfo {
        key: "links",
        path: ".dock/links",
        kind: PathKind::Dir,
    },
    PathInfo {
        key: "helm_d",
        path: ".dock/links/helm",
        kind: PathKind::Dir,
    },
    PathInfo {
        key: "stage",
        path: ".dock/stage",
        kind: PathKind::File,
    },
    PathInfo {
        key: "helm_f",
        path: ".dock/HELM",
        kind: PathKind::File,
    },
    PathInfo {
        key: "core",
        path: ".dock/links/helm/core",
        kind: PathKind::File,
    },
    PathInfo {
        key: "config",
        path: ".dock/config.toml",
        kind: PathKind::File,
    },
];

#[pyclass]
pub struct Spacedock;

impl Spacedock {
    pub fn get_repo_dir_internal() -> String {
        env::current_dir()
            .expect("Failed to get the current working directory")
            .to_string_lossy()
            .to_string()
    }

    pub fn get_path_info_internal(key: &str) -> Option<&'static PathInfo> {
        PATHS.iter().find(|info| info.key == key)
    }
}

#[pymethods]
impl Spacedock {
    #[staticmethod]
    pub fn get_repo_dir() -> String {
        Spacedock::get_repo_dir_internal()
    }

    #[staticmethod]
    pub fn get_path_info(key: &str) -> PyResult<String> {
        if let Some(path_info) = Spacedock::get_path_info_internal(key) {
            Ok(path_info.path.to_string())
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Not a valid key for path",
            ))
        }
    }

    #[staticmethod]
    pub fn get_path_kind(key: &str) -> Option<String> {
        Spacedock::get_path_info_internal(key).map(|path_info| path_info.kind.as_str().to_string())
    }

    #[staticmethod]
    pub fn get_paths_dict(py: Python, base_path: &str) -> PyResult<PyObject> {
        let dict = PyDict::new(py);

        for info in PATHS.iter() {
            let full_path = match info.key {
                "repo" => Path::new(base_path).to_path_buf(),
                "dock" => Path::new(base_path).join(".dock"),
                "links" => Path::new(base_path).join(".dock").join("links"),
                "core" => Path::new(base_path)
                    .join(".dock")
                    .join("links")
                    .join("helm")
                    .join("core"),
                _ => Path::new(base_path).join(info.path),
            };
            dict.set_item(info.key, full_path.to_str().unwrap())?;
        }

        Ok(dict.into())
    }
}
