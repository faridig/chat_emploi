#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

// --- Imports ---
use tauri::{
    command, AppHandle, Manager, State, Window,
    plugin::{Builder, TauriPlugin},
    RunEvent, Runtime,
};
use std::collections::HashMap;
use std::process::{Command, Stdio, Child};
use std::sync::Mutex;
use std::io::{BufReader, BufRead, Write};

// --- State Management ---
pub struct SharedState {
    // We use a mutex to ensure thread-safe access to the sidecar process
    sidecar: Mutex<Option<Child>>,
}

// --- Tauri Commands ---
#[command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[command]
async fn call_backend(
    state: State<'_, SharedState>,
    window: Window,
    method: String,
    params: serde_json::Value,
) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().unwrap();
    if let Some(child) = sidecar.as_mut() {
        let stdin = child.stdin.as_mut().ok_or("Failed to open stdin")?;
        let mut stdout = BufReader::new(child.stdout.as_mut().ok_or("Failed to open stdout")?);

        let request = serde_json::json!({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        });

        // Send request to backend
        stdin.write_all(request.to_string().as_bytes()).map_err(|e| e.to_string())?;
        stdin.write_all(b"\n").map_err(|e| e.to_string())?; // Ensure the line is sent

        // Read response from backend
        let mut line = String::new();
        stdout.read_line(&mut line).map_err(|e| e.to_string())?;

        let response: serde_json::Value = serde_json::from_str(&line).map_err(|e| e.to_string())?;

        Ok(response)
    } else {
        Err("Sidecar process not running".to_string())
    }
}

// --- Plugin Definition ---
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("python-sidecar")
        .setup(|app_handle| {
            let state = SharedState {
                sidecar: Mutex::new(None),
            };
            app_handle.manage(state);
            Ok(())
        })
        .build()
}

// --- Main Application Setup ---
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(init())
        .invoke_handler(tauri::generate_handler![greet, call_backend])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            let state: State<SharedState> = app.state();
            let mut sidecar = state.sidecar.lock().unwrap();

            // TODO: Use a relative path from the app's resource directory
            let child = Command::new("python")
                .arg("../backend/src/main.py")
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spawn()
                .expect("Failed to start sidecar");

            *sidecar = Some(child);

            window.on_window_event(move |event| {
                if let tauri::WindowEvent::Destroyed = event {
                    let mut sidecar = state.sidecar.lock().unwrap();
                    if let Some(child) = sidecar.as_mut() {
                        child.kill().expect("Failed to kill sidecar");
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
