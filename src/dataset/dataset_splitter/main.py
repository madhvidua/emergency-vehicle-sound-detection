from .splitter import DataSplitter


def main():
    # Directories
    source_dir = 'data/labeled'
    train_dir = 'data/train-2'
    test_dir = 'data/test-2'

    # Split the data
    splitter = DataSplitter(source_dir, train_dir, test_dir)
    splitter.split_data()


# python -m src.data.dataset_splitter.main
if __name__ == "__main__":
    main()
