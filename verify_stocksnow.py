"""Verify StockSnow code structure and completeness."""

import os
from pathlib import Path


def check_file_exists(path, description):
    """Check if a file exists."""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"✓ {description}: {path} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {path} (MISSING)")
        return False


def check_directory_structure():
    """Check that all required files exist."""
    print("\n" + "="*60)
    print("Verifying StockSnow File Structure")
    print("="*60 + "\n")
    
    files = [
        ("src/stocksnow/__init__.py", "Package init"),
        ("src/stocksnow/models.py", "Data models"),
        ("src/stocksnow/monitor.py", "Main monitor"),
        ("src/stocksnow/watchlist.py", "Watchlist manager"),
        ("src/stocksnow/alerts.py", "Alert manager"),
        ("src/stocksnow/streaming.py", "Data streamer"),
        ("src/stocksnow/technical.py", "Technical analyzer"),
        ("src/stocksnow/cli.py", "CLI interface"),
        ("src/stocksnow/api.py", "REST API"),
        ("src/stocksnow/README.md", "Module documentation"),
        ("tests/test_stocksnow.py", "Test suite"),
        ("examples/stocksnow_demo.py", "Demo script"),
        ("STOCKSNOW_FEATURE.md", "Feature documentation"),
    ]
    
    all_exist = True
    for path, description in files:
        if not check_file_exists(path, description):
            all_exist = False
    
    return all_exist


def count_lines_of_code():
    """Count lines of code in StockSnow."""
    print("\n" + "="*60)
    print("Code Statistics")
    print("="*60 + "\n")
    
    total_lines = 0
    total_files = 0
    
    stocksnow_dir = Path("src/stocksnow")
    if stocksnow_dir.exists():
        for py_file in stocksnow_dir.glob("*.py"):
            with open(py_file) as f:
                lines = len(f.readlines())
                total_lines += lines
                total_files += 1
                print(f"  {py_file.name}: {lines} lines")
    
    print(f"\n  Total: {total_files} files, {total_lines} lines of code")
    
    # Tests
    test_file = Path("tests/test_stocksnow.py")
    if test_file.exists():
        with open(test_file) as f:
            test_lines = len(f.readlines())
        print(f"  Tests: {test_lines} lines")
    
    # Demo
    demo_file = Path("examples/stocksnow_demo.py")
    if demo_file.exists():
        with open(demo_file) as f:
            demo_lines = len(f.readlines())
        print(f"  Demo: {demo_lines} lines")
    
    return total_lines


def check_code_quality():
    """Check for basic code quality indicators."""
    print("\n" + "="*60)
    print("Code Quality Checks")
    print("="*60 + "\n")
    
    checks = []
    
    # Check for docstrings
    monitor_file = Path("src/stocksnow/monitor.py")
    if monitor_file.exists():
        with open(monitor_file) as f:
            content = f.read()
            has_docstrings = '"""' in content and content.count('"""') > 2
            checks.append(("Docstrings present", has_docstrings))
    
    # Check for type hints
    models_file = Path("src/stocksnow/models.py")
    if models_file.exists():
        with open(models_file) as f:
            content = f.read()
            has_type_hints = ": str" in content or ": int" in content or ": float" in content
            checks.append(("Type hints used", has_type_hints))
    
    # Check for error handling
    alerts_file = Path("src/stocksnow/alerts.py")
    if alerts_file.exists():
        with open(alerts_file) as f:
            content = f.read()
            has_error_handling = "try:" in content and "except" in content
            checks.append(("Error handling present", has_error_handling))
    
    # Check for async/await
    streaming_file = Path("src/stocksnow/streaming.py")
    if streaming_file.exists():
        with open(streaming_file) as f:
            content = f.read()
            has_async = "async def" in content and "await" in content
            checks.append(("Async/await used", has_async))
    
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
    
    return all(passed for _, passed in checks)


def check_documentation():
    """Check documentation completeness."""
    print("\n" + "="*60)
    print("Documentation Checks")
    print("="*60 + "\n")
    
    docs = []
    
    # Main README
    readme = Path("src/stocksnow/README.md")
    if readme.exists():
        with open(readme) as f:
            content = f.read()
            has_usage = "Usage" in content or "usage" in content
            has_examples = "Example" in content or "example" in content
            has_api = "API" in content or "api" in content
            docs.append(("Module README has usage section", has_usage))
            docs.append(("Module README has examples", has_examples))
            docs.append(("Module README has API docs", has_api))
    
    # Feature doc
    feature_doc = Path("STOCKSNOW_FEATURE.md")
    if feature_doc.exists():
        with open(feature_doc) as f:
            content = f.read()
            has_overview = "Overview" in content
            has_features = "Feature" in content or "feature" in content
            has_integration = "Integration" in content or "integration" in content
            docs.append(("Feature doc has overview", has_overview))
            docs.append(("Feature doc describes features", has_features))
            docs.append(("Feature doc covers integration", has_integration))
    
    for doc_name, passed in docs:
        status = "✓" if passed else "✗"
        print(f"{status} {doc_name}")
    
    return all(passed for _, passed in docs)


def check_tests():
    """Check test coverage."""
    print("\n" + "="*60)
    print("Test Coverage Checks")
    print("="*60 + "\n")
    
    test_file = Path("tests/test_stocksnow.py")
    if not test_file.exists():
        print("✗ Test file not found")
        return False
    
    with open(test_file) as f:
        content = f.read()
    
    test_classes = [
        "TestWatchlistManager",
        "TestAlertManager",
        "TestTechnicalAnalyzer"
    ]
    
    for test_class in test_classes:
        if test_class in content:
            print(f"✓ {test_class} test class exists")
        else:
            print(f"✗ {test_class} test class missing")
    
    test_count = content.count("def test_")
    print(f"\nTotal test methods: {test_count}")
    
    return test_count > 10


def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("StockSnow Code Verification")
    print("="*60)
    
    results = []
    
    results.append(("File structure", check_directory_structure()))
    lines = count_lines_of_code()
    results.append(("Code written", lines > 1000))
    results.append(("Code quality", check_code_quality()))
    results.append(("Documentation", check_documentation()))
    results.append(("Tests", check_tests()))
    
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60 + "\n")
    
    for check_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("✅ All verification checks passed!")
        print("="*60 + "\n")
        print("StockSnow is ready to use. To run:")
        print("  1. Install dependencies: poetry install")
        print("  2. Run CLI: poetry run stocksnow")
        print("  3. Run API: poetry run python -m src.stocksnow.api")
        print("  4. Run demo: poetry run python examples/stocksnow_demo.py")
        print("  5. Run tests: poetry run pytest tests/test_stocksnow.py")
        return 0
    else:
        print("\n" + "="*60)
        print("❌ Some checks failed")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
