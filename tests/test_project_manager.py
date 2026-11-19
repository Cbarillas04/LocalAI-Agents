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

# Test 9: Checks the summary
def test_project_summary(tmp_path):
    test_dir_one = tmp_path / "project"
    test_dir_one.mkdir()

    test_file_two = test_dir_one / "main.py"
    test_file_three = test_dir_one / "helper.py"
    test_file_four = test_dir_one / "README.txt"

    test_file_two.write_text("print('hello')")
    test_file_three.write_text("print('world')")
    test_file_four.write_text("Project README")

    project_manager = ProjectManager(test_dir_one)
    result = project_manager.get_project_summary()
    expected = {
        "total_files": 3,
        "total_directories": 0,
        "file_types": {
            ".py": 2,
            ".txt": 1
        }
    }
    assert result == expected

# Test 10: checks a project with no files/directories
def test_project_summary_empty(tmp_path):
    project_manager = ProjectManager(tmp_path)
    result = project_manager.get_project_summary()
    expected = {
        "total_files": 0,
        "total_directories": 0,
        "file_types": {}
    }
    assert result == expected

# Test 11: Checks project tree structure
def test_project_tree(tmp_path):
    project = tmp_path / "project"
    scripts = project / "scripts"
    assets = project / "assets"

    scripts.mkdir(parents = True)
    assets.mkdir()

    (project / "main.py").write_text("print('hello')")
    (scripts / "player.py").write_text("print('player')")
    (assets / "texture.png").write_text("fake image")

    project_manager = ProjectManager(project)
    result = project_manager.get_project_tree()

    expected = [
        "assets/",
        "assets/texture.png",
        "main.py",
        "scripts/",
        "scripts/player.py"
    ]

    assert sorted(result) == expected

# Test 12: Checks that it returns empty list if project is empty
def test_project_tree_empty(tmp_path):
    project_manager = ProjectManager(tmp_path)

    assert project_manager.get_project_tree() == []