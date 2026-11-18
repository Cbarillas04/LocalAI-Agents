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