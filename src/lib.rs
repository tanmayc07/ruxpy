use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::Path;
use sha3::{Digest, Sha3_256};
use pyo3::prelude::*;


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
fn read_blob(repo_path: &str, hash: &str) -> PyResult<Vec<u8>> {
    let (subdir, filename) = hash.split_at(2);
    let obj_path = Path::new(repo_path).join(".dock").join("objects");
    let file_path = Path::new(&obj_path).join(subdir).join(filename);
    let contents = fs::read(file_path)?;
    Ok(contents)
}

/// A Python module implemented in Rust.
#[pymodule]
fn ruxpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_object_dir, m)?)?;
    m.add_function(wrap_pyfunction!(save_blob, m)?)?;
    m.add_function(wrap_pyfunction!(read_blob, m)?)?;
    Ok(())
}
