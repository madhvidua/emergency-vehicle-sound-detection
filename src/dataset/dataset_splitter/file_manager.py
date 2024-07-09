import os
import shutil


class FileManager:
    @staticmethod
    def check_and_create_dirs(train_dir, test_dir):
        # Check if train and test directories exist and are not empty (excluding system files)
        for directory in [train_dir, test_dir]:
            if os.path.exists(directory):
                non_system_files = [f for f in os.listdir(directory) if not f.startswith('.')]
                if non_system_files:
                    raise ValueError(f"{directory} directory exists and is not empty. Please clear the directory or use a different path.")
            else:
                os.makedirs(directory)

    @staticmethod
    def get_all_files(source_dir):
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
