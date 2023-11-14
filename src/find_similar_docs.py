import re
import hashlib
# import math
from random import randint, seed
from itertools import combinations

seed(1631996)


class hashFamily:
    """A class that represents a family of hash functions.

    Attributes:
        resultSize (int): how many bytes we want back
        maxLen (int): how long can our i be (in decimal)
        salt (str): a random string that will be used for hashing
    """

    def __init__(self, i):
        # how many bytes we want back
        self.resultSize = 8
        # how long can our i be (in decimal)
        self.maxLen = 20
        self.salt = str(i).zfill(self.maxLen)[-self.maxLen:]

    def get_hash_value(self, el_to_hash):
        """Get the hash value of the given element.

        Arguments:
            el_to_hash {str} -- element to hash

        Returns:
            int -- hash value
        """
        return int(
            hashlib.sha1(
                str(el_to_hash).encode("utf-8") +
                self.salt.encode("utf-8")).hexdigest()[-self.resultSize:],
            16,
        )


class shingler:
    """A class that represents a shingler.

    Attributes:
        k {int}: size of the shingles
    """

    def __init__(self, k):
        self.k = int(k) if k > 0 else 10

    # inner class utility
    def process_doc(self, document):
        """Process the document, removing multiple spaces and newlines.

        Arguments:
            document {str} -- document to process

            Returns:
                str -- processed document
        """
        return re.sub("( )+|(\n)+", " ", document).lower()

    def get_shingles(self, document):
        """Get the shingles of the given document.

        Arguments:
            document {str} -- document to process

        Returns:
            set -- set of shingles
        """
        document = self.process_doc(document)
        return {
            document[i:i + self.k]
            for i in range(len(document) - self.k + 1)
        }

    def get_k(self):
        """Get the size of the shingles.

        Returns:
            int -- size of the shingles
        """
        return self.k

    # return sorted hash
    def get_hashed_shingles(self, shingles_set):
        """Get the hashed shingles of the given document.

        Arguments:
            shingles_set {set} -- set of shingles

        Returns:
            list -- list of hashed shingles
        """
        hash_function = hashFamily(0)
        return sorted({hash_function.get_hash_value(s) for s in shingles_set})


class minhashSigner:
    """A class that represents a minhash signer.

    Attributes:
        sig_size {int}: size of the signature
        hash_functions {list}: list of hash functions
    """

    def __init__(self, sig_size):
        self.sig_size = sig_size
        self.hash_functions = [
            hashFamily(randint(0, 10000000000)) for _ in range(sig_size)
        ]

    def compute_set_signature(self, set_):
        """Compute the signature of the given set.

        Arguments:
            set_ {set} -- set to compute the signature of

        Returns:
            list -- list of signature values
        """
        return [
            min(h_funct.get_hash_value(el) for el in set_)
            for h_funct in self.hash_functions
        ]

    def compute_signature_matrix(self, set_list):
        """Compute the signature matrix of the given set list.

        Arguments:
            set_list {list} -- list of sets to compute the signature matrix of

        Returns:
            list -- list of signatures
        """
        return [self.compute_set_signature(s) for s in set_list]


class lsh:
    """A class that represents a lsh.

    Attributes:
        threshold {float}: threshold for the jaccard similarity
    """
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def get_signature_matrix_bands(self, sig_matrix, bands_nr, sign_len):
        """Get the signature matrix bands.

        Arguments:
            sig_matrix {list} -- signature matrix
            bands_nr {int} -- number of bands
            sign_len {int} -- length of the signature

        Returns:
            dict -- dictionary of bands
        """
        r = sign_len // bands_nr
        return {
            i: [
                " ".join(map(str, signature[i * r:(i + 1) * r]))
                for signature in sig_matrix
            ]
            for i in range(bands_nr)
        }

    def get_band_buckets(self, band, hash_funct):
        """Get the band buckets.

        Arguments:
            band {list} -- band to get the buckets of
            hash_funct {hashFamily} -- hash function to use

        Returns:
            dict -- dictionary of buckets
        """
        buckets = {}
        for doc_id in range(len(band)):
            value = hash_funct.get_hash_value(band[doc_id])
            if value not in buckets:
                buckets[value] = [doc_id]
            else:
                buckets[value].append(doc_id)

        return buckets

    def get_candidates_list(self, buckets):
        """Get the candidates list.

        Arguments:
            buckets {dict} -- dictionary of buckets

        Returns:
            set -- set of candidates
        """
        return {
            tuple(sorted(pair))
            for bucket, candidate_list in buckets.items()
            if len(candidate_list) > 1
            for pair in combinations(candidate_list, 2)
        }

    def check_candidates(self, candidates_list, threshold, sigs):
        """Check the candidates list.

        Arguments:
            candidates_list {set} -- set of candidates
            threshold {float} -- threshold for the jaccard similarity
            sigs {list} -- list of signatures

        Returns:
            set -- set of similar documents
        """
        similar_docs = set()  # set of tuples
        for similar_pair in candidates_list:
            doc_id_1 = similar_pair[0]
            doc_id_2 = similar_pair[1]
            signature_1 = set(sigs[doc_id_1])
            signature_2 = set(sigs[doc_id_2])
            js = len(signature_1.intersection(signature_2)) / len(
                signature_1.union(signature_2))

            if js >= threshold:
                similar_docs.add(tuple(sorted((doc_id_1, doc_id_2))))

        return similar_docs

    def get_similar_items(self, sig_matrix, bands_nr, sign_len):
        """Get the similar items.

        Arguments:
            sig_matrix {list} -- signature matrix
            bands_nr {int} -- number of bands
            sign_len {int} -- length of the signature

        Returns:
            set -- set of similar documents
        """
        similar_docs = set()
        # divide signature matrix into bands
        bands = self.get_signature_matrix_bands(sig_matrix, bands_nr, sign_len)

        # for all the bands
        for band_id, elements in bands.items():
            buckets = self.get_band_buckets(elements,
                                            hash_funct=hashFamily(
                                                randint(0, 10000000000)))
            # Get all the candidate pairs
            candidates = self.get_candidates_list(buckets)
            # Check all candidate pairs' signatures
            for sim_tuple in self.check_candidates(candidates, self.threshold,
                                                   sig_matrix):
                similar_docs.add(sim_tuple)

        return (similar_docs)
