import os
import shutil


class FileManager:

    @staticmethod
    def create_directory(directory, allow_existing=False, allow_non_empty=False):
        # Check if the directory exists
        if os.path.exists(directory):
            if not allow_existing:
                raise ValueError(f"{directory} directory already exists. Please use a different path or set allow_existing to True.")

            # Check if the directory is non-empty (excluding system files)
            non_system_files = [f for f in os.listdir(directory) if not f.startswith('.')]
            if non_system_files and not allow_non_empty:
                raise ValueError(f"{directory} directory exists and is not empty. Please clear the directory or set allow_non_empty to True.")
        else:
            # Create the directory if it does not exist
            os.makedirs(directory)

    @staticmethod
    def get_all_non_system_files(source_dir):
        # Get list of all files
        all_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if not file.startswith('.'):  # Ignore system files
                    all_files.append(os.path.join(root, file))
        return all_files

    @staticmethod
    def copy_files(file_list, source_dir, destination_dir):
        for file in file_list:
            dest = file.replace(source_dir, destination_dir)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(file, dest)
