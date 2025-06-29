#!/usr/bin/env python3
"""
Automated Documentation Update Script

This script integrates with the build process to automatically update documentation
when the codebase changes. Can be run as part of CI/CD or pre-commit hooks.
"""

import subprocess
import sys
from pathlib import Path
import shutil


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(f"Output: {result.stdout.strip()}")
    
    return result


def main():
    """Main automation workflow."""
    print("🚀 Starting automated documentation update process...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Must be run from project root directory")
        sys.exit(1)
    
    # Step 1: Generate API documentation
    print("\n📚 Step 1: Generating API documentation...")
    run_command("python scripts/generate_api_docs.py")
    
    # Step 2: Update main documentation if needed
    print("\n📝 Step 2: Checking documentation currency...")
    
    # Check if generated docs should be copied to main docs
    generated_api = Path("docs/generated/api_reference.md")
    main_api = Path("docs/api.md")
    
    if generated_api.exists():
        if not main_api.exists() or generated_api.stat().st_mtime > main_api.stat().st_mtime:
            print("  📄 Updating main API documentation...")
            shutil.copy2(generated_api, main_api)
            print("  ✅ Main API documentation updated")
        else:
            print("  ✅ Main API documentation is current")
    
    # Step 3: Validate documentation
    print("\n🔍 Step 3: Validating documentation...")
    
    # Check for broken links (if markdown-link-check is available)
    link_check = run_command("markdown-link-check --version", check=False)
    if link_check.returncode == 0:
        run_command("markdown-link-check docs/*.md", check=False)
    else:
        print("  ⚠️  markdown-link-check not available, skipping link validation")
    
    # Step 4: Generate changelog summary
    print("\n📋 Step 4: Documentation summary...")
    
    docs_dir = Path("docs")
    generated_dir = Path("docs/generated")
    
    doc_files = list(docs_dir.glob("*.md"))
    generated_files = list(generated_dir.glob("*"))
    
    print(f"  📁 Main documentation files: {len(doc_files)}")
    for doc_file in doc_files:
        print(f"    - {doc_file.name}")
    
    print(f"  🤖 Generated documentation files: {len(generated_files)}")
    for gen_file in generated_files:
        print(f"    - {gen_file.name}")
    
    # Step 5: Suggest next actions
    print("\n✅ Automated documentation update completed!")
    print("\n💡 Suggested next actions:")
    print("  1. Review generated documentation in docs/generated/")
    print("  2. Update CHANGELOG.md if API changes were made")
    print("  3. Commit documentation updates if appropriate")
    print("  4. Consider running tests to validate changes")
    
    print("\n🔧 Integration options:")
    print("  - Add to .pre-commit-config.yaml for automatic updates")
    print("  - Include in CI/CD pipeline for documentation validation")
    print("  - Run before releases to ensure documentation currency")


if __name__ == "__main__":
    main()
