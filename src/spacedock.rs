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

    #[staticmethod]
    pub fn get_missing_spacedock_items_core(base_path: &str) -> Vec<&'static str> {
        let mut missing = Vec::new();

        for info in PATHS.iter() {
            let full_path = Path::new(base_path).join(info.path);

            if !full_path.exists() {
                missing.push(info.key);
                continue;
            }

            match info.kind {
                PathKind::Dir if !full_path.is_dir() => missing.push(info.key),
                PathKind::File if !full_path.is_file() => missing.push(info.key),
                _ => {}
            }
        }

        missing
    }

    #[staticmethod]
    fn find_dock_root(start_path: Option<String>) -> Option<String> {
        let mut current = match start_path {
            Some(path) => std::path::PathBuf::from(path),
            None => std::env::current_dir().unwrap(),
        };

        loop {
            if current.join(".dock").exists() {
                return Some(current.to_string_lossy().to_string());
            }

            if !current.pop() {
                break;
            }
        }
        None
    }

    #[staticmethod]
    pub fn check_spacedock(path: Option<String>) -> bool {
        let mut base_path = path;

        if base_path.is_none() {
            base_path = Spacedock::find_dock_root(Some(".".to_string()));
            if base_path.is_none() {
                panic!("No spacedock found!");
            }
        }
        let base_path_str = base_path.as_ref().unwrap();
        let missing = Spacedock::get_missing_spacedock_items_core(base_path_str);
        missing.is_empty()
    }
}
