from pathlib import Path

class ProjectManager:
    # Initialize project root
    def __init__(self, root):
        self.root = Path(root).resolve()

    # Assure path exists and if it's a directory
    def validate_project(self):
        return self.root.exists() and self.root.is_dir()

    # Find and return files within dir
    def list_files(self):
        if not self.validate_project():
            raise ValueError("Invalid project directory")
        files = [
            file for file in self.root.rglob('*')
                if file.is_file()
        ]
        return files

    # Read text within a file
    def read_file(self, file_path):
        file_path = Path(file_path).resolve()
        # Assert file exists in project directory
        try:
            file_path.relative_to(self.root)
        except ValueError:
            raise ValueError("Invalid file path: {}".format(file_path))
        # File exists and is a file
        if not file_path.exists() or not file_path.is_file():
            raise ValueError("Invalid file path")

        return file_path.read_text()

    def get_project_summary(self):
        if not self.validate_project():
            raise ValueError("Invalid project directory")

        # Get all files
        files = self.list_files()
        total_files = len(files)

        # Get all directories
        directories = [
            directory for directory in self.root.rglob('*')
                if directory.is_dir()
        ]

        # Get each file type and its count
        file_types = {}
        for file in files:
            suf = file.suffix
            if suf not in file_types:
                file_types[suf] = 1
            else:
                file_types[suf] += 1

        return {
            "total_files": total_files,
            "total_directories": len(directories),
            "file_types": file_types,
        }

