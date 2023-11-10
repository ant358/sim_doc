import pandas as pd


def load_dataset(file, type):
    print(f"Loading dataset...{file}")
    if type == "tsv":
        dataset = pd.read_csv(file, sep="\t")
    elif type == "csv":
        dataset = pd.read_csv(file, sep=",")
    elif type == "excel":
        dataset = pd.read_excel(file)
    elif type == "json":
        dataset = pd.read_json(file)
    else:
        print("Error: file type not supported")
        return None
    # check the format of the dataset
    if "id" in dataset.columns:
        dataset = dataset.rename(columns={"id": "doc_id"})
    else:
        dataset["doc_id"] = dataset.index
    # concatenate all string type columns
    dataset["text"] = (
        dataset.drop("doc_id", axis=1)
        .astype(str)
        .apply(lambda x: " ".join(x), axis=1)
    )
    return dataset[["doc_id", "text"]]


def get_dataset_len(dataset):
    return len(dataset)
