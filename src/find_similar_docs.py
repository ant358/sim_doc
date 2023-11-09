import re
import hashlib
import math
from random import randint, seed

seed(1631996)


class hashFamily:
    def __init__(self, i):
        # how many bytes we want back
        self.resultSize = 8
        # how long can our i be (in decimal)
        self.maxLen = 20
        self.salt = str(i).zfill(self.maxLen)[-self.maxLen:]

    def get_hash_value(self, el_to_hash):
        return int(
            hashlib.sha1(
                str(el_to_hash).encode("utf-8") + self.salt.encode("utf-8")
            ).hexdigest()[-self.resultSize:],
            16,
        )


class shingler:
    def __init__(self, k):
        self.k = int(k) if k > 0 else 10

    # inner class utility
    def process_doc(self, document):
        return re.sub("( )+|(\n)+", " ", document).lower()

    def get_shingles(self, document):
        document = self.process_doc(document)
        return {
            document[i:i + self.k]
            for i in range(len(document) - self.k + 1)
        }

    def get_k(self):
        return self.k

    # return sorted hash
    def get_hashed_shingles(self, shingles_set):
        hash_function = hashFamily(0)
        return sorted({hash_function.get_hash_value(s) for s in shingles_set})


class minhashSigner:
    def __init__(self, sig_size):
        self.sig_size = sig_size
        self.hash_functions = [
            hashFamily(randint(0, 10000000000)) for _ in range(sig_size)
        ]

    def compute_set_signature(self, set_):
        set_sig = []
        for h_funct in self.hash_functions:
            min_hash = math.inf
            for el in set_:
                h = h_funct.get_hash_value(el)
                if h < min_hash:
                    min_hash = h

            set_sig.append(min_hash)

        return set_sig

    # return a list of lists that can be seen as the signature matrix
    def compute_signature_matrix(self, set_list):
        return [self.compute_set_signature(s) for s in set_list]


class lsh:
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def get_signature_matrix_bands(self, sig_matrix, bands_nr, sign_len):
        # bands_nr = b
        # sign_len = n
        r = int(sign_len / bands_nr)
        bands = {i: [] for i in range(bands_nr)}
        for signature in sig_matrix:
            for i in range(bands_nr):
                idx = i * r
                bands[i].append(" ".join(
                    str(x) for x in signature[idx:idx + r]))

        return bands

    def get_band_buckets(self, band, hash_funct):
        buckets = {}
        for doc_id in range(len(band)):
            value = hash_funct.get_hash_value(band[doc_id])
            if value not in buckets:
                buckets[value] = [doc_id]
            else:
                buckets[value].append(doc_id)

        return buckets

    def get_candidates_list(self, buckets):
        candidates = set()
        for bucket, candidate_list in buckets.items():
            if len(candidate_list) > 1:
                for i in range(len(candidate_list) - 1):
                    for j in range(i + 1, len(candidate_list)):
                        pair = tuple(
                            sorted((candidate_list[i], candidate_list[j])))
                        candidates.add(pair)

        return candidates

    def check_candidates(self, candidates_list, threshold, sigs):
        similar_docs = set()  # set of tuples
        for similar_pair in candidates_list:
            doc_id_1 = similar_pair[0]
            doc_id_2 = similar_pair[1]
            signature_1 = set(
                sigs[doc_id_1]
            )
            signature_2 = set(sigs[doc_id_2])
            js = len(signature_1.intersection(signature_2)) / len(
                signature_1.union(signature_2))

            if js >= threshold:
                similar_docs.add(tuple(sorted((doc_id_1, doc_id_2))))

        return similar_docs

    def get_similar_items(self, sig_matrix, bands_nr, sign_len):
        similar_docs = set()
        # divide signature matrix into bands
        bands = self.get_signature_matrix_bands(
            sig_matrix, bands_nr, sign_len)

        # for all the bands
        for band_id, elements in bands.items():
            buckets = self.get_band_buckets(
                elements, hash_funct=hashFamily(randint(0, 10000000000)))
            # Get all the candidate pairs
            candidates = self.get_candidates_list(buckets)
            # Check all candidate pairs' signatures
            for sim_tuple in self.check_candidates(
                    candidates, self.threshold, sig_matrix):
                similar_docs.add(sim_tuple)

        return (
            similar_docs
        )
