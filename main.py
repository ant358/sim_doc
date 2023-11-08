import pandas as pd
import time
import src.find_similar_docs as fsd


print("Loading dataset...")
dataset=pd.read_csv("data/dataset_rent_rome_kijiji.tsv", sep="\t")
dataset['doc_id']=dataset.index
doc_nr = dataset['doc_id'].max()
print("Dataset loaded correctly.")
print("Producing Shingles...")
start_time = time.time()
#an array where the index i represent the document_id and the element shingling_list[i] the hashed shingles for document document_id
shingling_list = [None] * (doc_nr +1) 
shingling_size = 10
signature_size = 50
bands_nr = 10

shingler_inst = fsd.shingler(shingling_size)
signer = fsd.minhashSigner(signature_size)


#produce hashed shinglings for all documents
for index, row in dataset.iterrows():
    doc = row['Title']+" "+row['Short Description']
    i = row['doc_id']
    
    shinglings = shingler_inst.get_hashed_shingles( shingler_inst.get_shingles(doc) )
    shingling_list[i] = shinglings

end_time = time.time()
print("Shingles produced in:\t %.2f seconds."%(end_time - start_time))


start_time = time.time()
print("Computing signature matrix...")
#produce a signature for each shingle set
signature_matrix = signer.compute_signature_matrix( shingling_list )
end_time = time.time()
print("Signature Matrix computed in:\t %.2f seconds." %(end_time - start_time))



