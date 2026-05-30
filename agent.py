#!/usr/bin/env python3
import subprocess
import os
import sys
import tempfile
import shutil

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 agent.py <git_repository_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    tmp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository (shallow clone)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmp_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error cloning repository: {result.stderr}")
            return

        # Analyze the repository
        analysis = analyze_repository(tmp_dir, repo_url)
        print(analysis)
    except subprocess.TimeoutExpired:
        print("Error: Repository clone timed out.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        print('finally')
        shutil.rmtree(tmp_dir, ignore_errors=True)

def analyze_repository(path, repo_url):
    # Look for README
    readme_files = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md', 'readme']
    readme_content = None
    for readme in readme_files:
        readme_path = os.path.join(path, readme)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    readme_content = f.read(2000)  # First 2000 chars
                break
            except:
                pass

    # Look for package/manifest files
    manifest_files = [
        'package.json', 'setup.py', 'requirements.txt', 'Pipfile', 'pyproject.toml',
        'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod', 'composer.json',
        '.csproj', '.sln', 'Makefile', 'CMakeLists.txt'
    ]
    manifests = {}
    for manifest in manifest_files:
        manifest_path = os.path.join(path, manifest)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                    manifests[manifest] = f.read(500)  # First 500 chars
            except:
                pass

    # Look for source code directories to guess language
    src_dirs = ['src', 'lib', 'app', 'main']
    source_hints = []
    for d in src_dirs:
        if os.path.isdir(os.path.join(path, d)):
            source_hints.append(d)

    # Look for common config files
    config_files = ['.gitignore', '.gitattributes', 'Dockerfile', 'docker-compose.yml', '.env.example']
    configs = []
    for c in config_files:
        if os.path.exists(os.path.join(path, c)):
            configs.append(c)

    # Build analysis
    lines = []
    lines.append("=== Repository Analysis ===")
    lines.append(f"Repository: {repo_url}")
    lines.append("")

    if readme_content:
        lines.append("README Preview:")
        lines.append(readme_content)
        lines.append("")
    else:
        lines.append("No README file found.")
        lines.append("")

    if manifests:
        lines.append("Manifest/Package Files Found:")
        for name, content in manifests.items():
            lines.append(f"  {name}:")
            lines.append(f"    {content}")
            lines.append("")
    else:
        lines.append("No manifest/package files found.")
        lines.append("")

    if source_hints:
        lines.append("Source Directories Found: " + ", ".join(source_hints))
    else:
        lines.append("No standard source directories (src, lib, app, main) found.")

    if configs:
        lines.append("Config Files Found: " + ", ".join(configs))

    lines.append("")
    lines.append("=== Learning Points ===")
    lines.append("1. Check README for project purpose and setup instructions")
    lines.append("2. Examine manifest files to understand dependencies and build system")
    lines.append("3. Look at source directory structure to understand code organization")
    lines.append("4. Check config files for deployment and environment details")
    lines.append("5. Consider language-specific conventions (e.g., package.json for Node.js, pom.xml for Java)")

    return "\n".join(lines)

if __name__ == "__main__":
    main()