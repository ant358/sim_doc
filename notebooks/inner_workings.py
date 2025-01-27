# %%
import time
import os
import src.load_data as ld
import src.find_similar_docs as fsd
# %%

def get_shinglings(dataset):
    """get the shinglings for each document in the dataset

    Arguments:
        dataset {pandas.DataFrame} -- dataset containing the documents

    Returns:
        list -- list of shinglings for each document
    """
    shingling_list = [None] * dataset.shape[0]
    for index, row in dataset.iterrows():
        shinglings = shingler_inst.get_hashed_shingles(
            shingler_inst.get_shingles(row["text"]))
        shingling_list[index] = shinglings
    return shingling_list


def find_matching_doc(doc_id):
    """Find the similar documents, with the given id

    Arguments:
        doc_id {int} -- id of the document to search for

    Returns:
        list -- list of couples of similar documents
    """
    return [couple for couple in lsh_similar_itemset if doc_id in couple]


def get_matching_doc_set(doc_id):
    """Get the set of similar documents, with the given id

    Arguments:
        doc_id {int} -- id of the document to search for

    Returns:
        set -- set of similar documents
    """
    sim_docs = find_matching_doc(doc_id)
    sim_docs_set = set()
    for couple in sim_docs:
        sim_docs_set.add(couple[0])
        sim_docs_set.add(couple[1])

    return sim_docs_set
# %%
SHINGLING_SIZE = 10
SIGNATURE_SIZE = 50
BANDS_NR = 10
# THRESHOLD = 0.8
FILENAME = "data/rent_rome_text.json"
FILETYPE = "json"
OUTPUT = "output/output"
# %%
# check output dir exits if not create it
if not os.path.exists(OUTPUT.split("/")[0]):
    os.makedirs("output")
# %%
# overall_time_start = time.time()
# %%
# load the dataset
try:
    start_time = time.time()
    dataset = ld.load_dataset(file=FILENAME, type=FILETYPE)
    print(dataset.head())
    print(dataset.info())
    doc_nr = ld.get_dataset_len(dataset)
    end_time = time.time()
    print("Dataset loaded in:\t %.2f seconds." % (end_time - start_time))
except Exception as e:
    print("Error: ", e)
    exit(1)
# %%
# produce shinglings
print("Producing Shingles...")
start_time = time.time()
shingler_inst = fsd.shingler(SHINGLING_SIZE)
signer = fsd.minhashSigner(SIGNATURE_SIZE)

shingling_list = get_shinglings(dataset)
end_time = time.time()
print("Hashed Shingles produced in:\t %.2f seconds." % (end_time - start_time))
print(shingling_list[0][:10])
# %%
# produce a signature for each shingle set
print("Computing signature matrix...")
start_time = time.time()
# produce a signature for each shingle set
signature_matrix = signer.compute_signature_matrix(shingling_list)
end_time = time.time()
print("Signature Matrix computed in:\t %.2f seconds." %
        (end_time - start_time))
# %%
# use a range of threshold values to find the best one
for threshold in [0.6, 0.7, 0.8, 0.9]:
    # compute LSH similarity
    lsh_instance = fsd.lsh(threshold)
    start_time = time.time()
    print("Computing LSH similarity...")
    lsh_similar_itemset = lsh_instance.get_similar_items(
        signature_matrix, BANDS_NR, SIGNATURE_SIZE)
    end_time = time.time()
    print("LSH Similarity computed in:\t %.2f seconds.\nNo. Similar : %d" %
            ((end_time - start_time), len(lsh_similar_itemset)))

    # add a new column to the dataset 
    # containing the set of similar documents
    dataset[f"similar_docs_{threshold}"] = dataset["doc_id"].apply(
        get_matching_doc_set)
    dataset[f"num_similar_docs_{threshold}"] = dataset[
        f"similar_docs_{threshold}"].apply(len)

# dataset sort by number of similar documents
dataset = dataset.sort_values(by=["num_similar_docs_0.9"], ascending=False)

print(dataset[["doc_id", "similar_docs_0.9",
                "num_similar_docs_0.9"]].head())

# output the dataset to a file
dataset.to_csv(f"{OUTPUT}.csv", index=False)
# reduce the dataset to only one version of each similar document
dataset_reduced = dataset.drop_duplicates(subset=["similar_docs_0.9"],
                                            keep="first")
# output the reduced dataset to a file
dataset_reduced.to_csv(f"{OUTPUT}_reduced.csv", index=False)
print(dataset_reduced.info())
# show reduction ratio
print("Reduction ratio: %.2f%%" %
        (100 * (1 - dataset_reduced.shape[0] / dataset.shape[0])))

print(f"done: overall time taken {time.time() - overall_time_start}")
