use pyo3::prelude::*;
use std::env;

pub const DOCK_DIR: &str = ".dock";
pub const OBJECTS_DIR: &str = ".dock/objects";
pub const LINKS_DIR: &str = ".dock/links";
pub const HELM_DIR: &str = ".dock/links/helm";
pub const STAGE_FILE: &str = ".dock/stage";
pub const HELM_FILE: &str = ".dock/HELM";
pub const CORE_FILE: &str = ".dock/links/helm/core";
pub const CONFIG_FILE: &str = ".dock/config.toml";

#[pyclass]
pub struct Spacedock;

impl Spacedock {
    pub fn get_repo_dir_internal() -> String {
        env::current_dir()
            .expect("Failed to get the current working directory")
            .to_string_lossy()
            .to_string()
    }
}

#[pymethods]
impl Spacedock {
    #[staticmethod]
    pub fn get_repo_dir() -> String {
        Spacedock::get_repo_dir_internal()
    }

    #[staticmethod]
    pub fn get_dock_dir() -> String {
        DOCK_DIR.to_string()
    }

    #[staticmethod]
    pub fn get_objects_dir() -> String {
        OBJECTS_DIR.to_string()
    }

    #[staticmethod]
    pub fn get_links_dir() -> String {
        LINKS_DIR.to_string()
    }

    #[staticmethod]
    pub fn get_helm_dir() -> String {
        HELM_DIR.to_string()
    }

    #[staticmethod]
    pub fn get_stage_file() -> String {
        STAGE_FILE.to_string()
    }

    #[staticmethod]
    pub fn get_helm_file() -> String {
        HELM_FILE.to_string()
    }

    #[staticmethod]
    pub fn get_core_file() -> String {
        CORE_FILE.to_string()
    }

    #[staticmethod]
    pub fn get_config_file() -> String {
        CONFIG_FILE.to_string()
    }
}
