import pytest

from coding_agent.project_manager import ProjectManager

# Test 1: root path is stored as abs path
def test_project_manager_init(tmp_path):
    project_manager = ProjectManager(tmp_path)
    assert project_manager.root == tmp_path.resolve()

# Test 2: Existing dir returns True
def test_validate_project_success(tmp_path):
    project_manager = ProjectManager(tmp_path)
    assert project_manager.validate_project()

# Test 3: Missing dir returns False
def test_validate_project_failure(tmp_path):
    missing_path = tmp_path / "non_existent"
    project_manager = ProjectManager(missing_path)
    assert project_manager.validate_project() is False

# Test 4: Returns only files recursively
def test_list_files(tmp_path):
    d = tmp_path / "scripts"
    d.mkdir()

    # Create files
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hello')")
    readme_file = tmp_path / "README.md"
    readme_file.write_text("# My Project")
    helper_file = d / "helper.py"
    helper_file.write_text("def helper(): pass")

    project_manager = ProjectManager(tmp_path)

    # List project files
    files = project_manager.list_files()

    # Verify exactly three files were found
    assert len(files) == 3
    # Verify all expected filenames are present
    filenames = {file.name for file in files}
    assert filenames == {"main.py", "README.md", "helper.py"}
    # Verify directories aren't returned
    assert all(file.is_file() for file in files)

# Test 5: Reads and returns file contents
def test_read_file_success(tmp_path):
    hello_file = tmp_path / "hello.txt"
    hello_file.write_text("hello world")

    project_manager = ProjectManager(tmp_path)
    result = project_manager.read_file(hello_file)

    assert result == "hello world"

# Test 6: Raise ValueError for file not in project
def test_read_foreign_file(tmp_path):
    project = tmp_path / "project"
    foreign = tmp_path / "main.py"
    project.mkdir()
    foreign.mkdir()

    hello_file = foreign / "hello.txt"
    main_file = project / "main.py"
    hello_file.write_text("hello world")
    main_file.write_text("main file")

    project_manager = ProjectManager(project)

    with pytest.raises(ValueError):
        project_manager.read_file(hello_file)
    assert project_manager.read_file(main_file) == "main file"

# Test 7: Raise ValueError for nonexistent file
def test_read_file_missing(tmp_path):
    test_file = tmp_path / "missing.txt"
    project_manager = ProjectManager(tmp_path)
    with pytest.raises(ValueError):
        project_manager.read_file(test_file)

# Test 8: Raise ValueError when given a dir instead
def test_read_file_directory(tmp_path):
    test_file = tmp_path / "project"
    test_file.mkdir()
    project_manager = ProjectManager(tmp_path)
    with pytest.raises(ValueError):
        project_manager.read_file(test_file)