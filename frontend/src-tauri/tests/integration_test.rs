
#[cfg(test)]
mod tests {
    use super::*;
    use tauri::test::{mock_builder, MockRuntime};
    use std::process::Command;

    #[test]
    fn test_greet() {
        let builder = mock_builder()
            .invoke_handler(|invoke| {
                let mut cmd = Command::new("echo");
                cmd.arg("Hello, World!");
                let output = cmd.output().expect("failed to execute process");
                let stdout = String::from_utf8(output.stdout).unwrap();
                invoke.resolver.resolve(stdout).unwrap();
            });

        let app = tauri::test::mock_app(builder);
        let window = app.get_window("main").unwrap();

        // This is a placeholder for a real command execution test
        window.eval("window.__TAURI_INVOKE__('greet', { name: 'World' })").unwrap();
    }
}
