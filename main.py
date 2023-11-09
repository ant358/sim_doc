import pandas as pd
import time
import src.find_similar_docs as fsd


print("Loading dataset...")
dataset = pd.read_csv("data/dataset_rent_rome_kijiji.tsv", sep="\t")
print(dataset.head())
print(dataset.info())
dataset['doc_id'] = dataset.index
doc_nr = dataset['doc_id'].max()
print("Dataset loaded correctly.")
print("Producing Shingles...")
start_time = time.time()
shingling_list = [None] * (doc_nr + 1)
shingling_size = 10
signature_size = 50
bands_nr = 10

shingler_inst = fsd.shingler(shingling_size)
signer = fsd.minhashSigner(signature_size)


# produce hashed shinglings for all documents
for index, row in dataset.iterrows():
    doc = row['Title'] + " " + row['Short Description']
    i = row['doc_id']

    shinglings = shingler_inst.get_hashed_shingles(
        shingler_inst.get_shingles(doc))
    shingling_list[i] = shinglings

end_time = time.time()
print("Shingles produced in:\t %.2f seconds."%(end_time - start_time))


start_time = time.time()
print("Computing signature matrix...")
# produce a signature for each shingle set
signature_matrix = signer.compute_signature_matrix(shingling_list)
end_time = time.time()
print("Signature Matrix computed in:\t %.2f seconds." %
      (end_time - start_time))


lsh_instance = fsd.lsh(threshold=0.8)
start_time = time.time()
print("Computing LSH similarity...")
lsh_similar_itemset = lsh_instance.get_similar_items(signature_matrix, bands_nr, signature_size)
end_time = time.time()
lsh_computation_time = end_time - start_time
print(
    "LSH Similarity computed in:\t %.2f seconds.\nSimilar Elements Found: %d" %
    (lsh_computation_time, len(lsh_similar_itemset)))


# find all the matching doc_id for a given doc_id
def find_matching_doc(doc_id):
    return [couple for couple in lsh_similar_itemset if doc_id in couple]


def get_matching_doc_set(doc_id):
    sim_docs = find_matching_doc(doc_id)
    sim_docs_set = set()
    for couple in sim_docs:
        sim_docs_set.add(couple[0])
        sim_docs_set.add(couple[1])

    return sim_docs_set


# add a new column to the dataset containing the set of similar documents
dataset['similar_docs'] = dataset['doc_id'].apply(get_matching_doc_set)
dataset['num_similar_docs'] = dataset['similar_docs'].apply(len)

# dataset sort by number of similar documents
dataset = dataset.sort_values(by=['num_similar_docs'], ascending=False)

print(dataset[['Title', 'similar_docs', 'num_similar_docs']].head())

# output the dataset to a file
dataset.to_csv("output/dataset_rent_rome_kijiji_similar.tsv", sep="\t")
# reduce the dataset to only one version of each similar document
dataset_reduced = dataset.drop_duplicates(subset=['similar_docs'],
                                          keep='first')
dataset_reduced.to_csv("output/dataset_rent_rome_kijiji_similar_reduced.tsv",
                       sep="\t")
print(dataset_reduced.info())
# show reduction ratio
print("Reduction ratio: %.2f%%" %
      (100 * (1 - dataset_reduced.shape[0] / dataset.shape[0])))

print("done")
