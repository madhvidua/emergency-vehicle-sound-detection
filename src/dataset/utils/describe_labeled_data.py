import argparse
import os
from collections import defaultdict


# sjakcbkjasdhcljdhj
class FileStructure:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.file_structure = {}
        self.duplicates = defaultdict(list)
        self._build_file_structure()

    def _build_file_structure(self):
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.startswith('.'):  # Skip hidden files
                    continue
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.base_dir)
                dir_structure = self.file_structure

                for part in relative_path.split(os.sep)[:-1]:
                    dir_structure = dir_structure.setdefault(part, {})
                dir_structure[relative_path.split(os.sep)[-1]] = file_path

                self.duplicates[file].append(file_path)

    def count_files(self, structure):
        if isinstance(structure, str):
            return 1
        return sum(self.count_files(substructure) for substructure in structure.values())

    def find_duplicates(self):
        return {file: paths for file, paths in self.duplicates.items() if len(paths) > 1}


class FileStructurePrinter:
    @staticmethod
    def print_structure(structure, indent="", is_last=True):
        for i, (name, substructure) in enumerate(structure.items()):
            if isinstance(substructure, str):
                continue
            else:
                num_files = FileStructurePrinter._count_files(substructure)
                if i == len(structure) - 1:
                    print(f"{indent}└── {name}/ ({num_files} files)")
                    FileStructurePrinter.print_structure(substructure, indent + "    ", True)
                else:
                    print(f"{indent}├── {name}/ ({num_files} files)")
                    FileStructurePrinter.print_structure(substructure, indent + "│   ", False)

    @staticmethod
    def _count_files(structure):
        if isinstance(structure, str):
            return 1
        return sum(FileStructurePrinter._count_files(substructure) for substructure in structure.values())

    @staticmethod
    def print_state(base_dir, file_structure):
        print("**State of data**")
        num_files = FileStructurePrinter._count_files(file_structure.file_structure)
        print(f"{os.path.basename(base_dir)}/ ({num_files} files)")
        FileStructurePrinter.print_structure(file_structure.file_structure, "    ")

    @staticmethod
    def print_duplicates(duplicates):
        if duplicates:
            print("\n**Duplicates**")
            for file, paths in duplicates.items():
                print(file)
                for path in paths:
                    print(f"...{path}")
        else:
            print("\n**Duplicates**")
            print("No duplicate files found.")


def main():
    parser = argparse.ArgumentParser(description="Analyze the file structure of a directory.")
    parser.add_argument('--base_dir', type=str, default='data/labeled', help='The base directory to analyze')
    args = parser.parse_args()

    base_dir = args.base_dir

    if not os.path.exists(base_dir):
        print(f"The directory '{base_dir}' does not exist.")
        return

    file_structure = FileStructure(base_dir)

    FileStructurePrinter.print_state(base_dir, file_structure)

    duplicate_files = file_structure.find_duplicates()
    FileStructurePrinter.print_duplicates(duplicate_files)


# python describe_labeled_data.py --base_dir data/test
if __name__ == "__main__":
    main()
