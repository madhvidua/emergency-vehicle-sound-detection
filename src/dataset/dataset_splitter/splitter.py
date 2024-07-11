from sklearn.model_selection import train_test_split

from utils.file_manager import FileManager


class DataSplitter:
    def __init__(self, source_dir, train_dir, test_dir, train_size=0.8):
        self.source_dir = source_dir
        self.train_dir = train_dir
        self.test_dir = test_dir
        self.train_size = train_size

    def split_data(self):
        # Check and create directories
        for directory in [self.train_dir, self.test_dir]:
            FileManager.create_directory(directory=directory, allow_existing=True, allow_non_empty=False)

        # Get all files
        all_files = FileManager.get_all_non_system_files(self.source_dir)
        print(f"Total files found: {len(all_files)}")

        if not all_files:
            raise ValueError("No files found in the source directory. Please check the path.")

        # Split the files
        train_files, test_files = train_test_split(all_files, train_size=self.train_size, random_state=42)
        print(f"Training files: {len(train_files)}")
        print(f"Testing files: {len(test_files)}")

        # Copy files to train and test directories
        FileManager.copy_files(train_files, self.source_dir, self.train_dir)
        FileManager.copy_files(test_files, self.source_dir, self.test_dir)
