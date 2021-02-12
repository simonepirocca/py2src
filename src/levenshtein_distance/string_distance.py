"""
This module contains functions for calculating string distance
"""
import copy
import numpy as np
from fuzzywuzzy import fuzz
import Levenshtein as lev


class StringDistance:

    """Docstring for PackageDistance. """

    def __init__(self, words: list = None):
        """TODO: to be defined1. """
        self.reserved_words = {"python": "*", "-": ""}
        self.words = words

    def levenshtein_distance(self, target: str, distance: int = 1):
        """TODO: Docstring for  levenshtein.
        Calculating levenshtein distance or ratio
        : packages_list: a list of strings of packages
        : distance: if you want to calculate distance (default)
        : ratio: if you want to calcuate ratio
        :returns: a list of distances

        """
        if self.words is not None:
            for word in self.words:
                # Removing noise edits by lowercasing strings
                word_original = word
                word = word.lower()
                target = target.lower()
                # Reducing noise by replacing predefined reserved words
                for key, value in self.reserved_words.items():
                    if (key in word) and (key in target):
                        word = word.replace(key, value)
                        target = target.replace(key, value)

                if 0 < lev.distance(target, word) <= distance:
                    yield (word_original)

    def levenshtein_distance_only(self, target: str, words: list = None):
        """TODO: Docstring for  levenshtein.
        Calculating levenshtein distance or ratio
        : packages_list: a list of strings of packages
        : distance: if you want to calculate distance (default)
        : ratio: if you want to calcuate ratio
        :returns: a list of distances

        """
        if words is not None:
            self.words = words

        if self.words is not None:
            for word in self.words:
                # Removing noise edits by lowercasing strings
                word_original = word
                word = word.lower()
                target = target.lower()
                # Reducing noise by replacing predefined reserved words
                for key, value in self.reserved_words.items():
                    if (key in word) and (key in target):
                        print(key, value)
                        word = word.replace(key, value)
                        target = target.replace(key, value)

                distance = lev.distance(target, word)
                yield distance

    def lev_distances_raw_strs(self, str1: str, str2: str):
        """TODO: Docstring for lev_distances_strs.
        Calculating distance between two raw strings

        """
        # Removing noise edits by lowercasing strings
        str1 = str1.lower()
        str2 = str2.lower()
        # Reducing noise by replacing predefined reserved words
        distance = lev.distance(str1, str2)
        return distance

    def lev_distances_strs(self, str1: str, str2: str):
        """TODO: Docstring for lev_distances_strs.
        Calculating distance between two strings

        """
        # Removing noise edits by lowercasing strings
        str1 = str1.lower()
        str2 = str2.lower()
        # Reducing noise by replacing predefined reserved words
        for key, value in self.reserved_words.items():
            if (key in str1) and (key in str2):
                str1 = str1.replace(key, value)
                str2 = str2.replace(key, value)

        distance = lev.distance(str1, str2)
        return distance

    def lev_distances_strs_editops(self, str1: str, str2: str):
        """TODO: Docstring for lev_distances_strs.
        Calculating distance between two strings

        """
        # Removing noise edits by lowercasing strings
        str1 = str1.lower()
        str2 = str2.lower()
        # Reducing noise by replacing predefined reserved words
        for key, value in self.reserved_words.items():
            if (key in str1) and (key in str2):
                str1 = str1.replace(key, value)
                str2 = str2.replace(key, value)

        editops = lev.editops(str1, str2)
        yield (str1, str2, editops)

    def fuzzy(
        self,
        log_time: dict = {},
        partial: bool = False,
        token_set: bool = False,
        token_sort: bool = False,
    ):
        """TODO: Docstring for  fuzzy.

        :arg1: TODO
        :returns: TODO

        """
        if self.packages_list is not None:
            rows = cols = copy.deepcopy(self.packages_list)
            # fuzz_matrix = np.zeros((len(rows), len(cols)), dtype=int)
            fuzz_matrix = csr_matrix((len(rows), len(cols)), dtype=np.int8).toarray()

            for i, _ in enumerate(rows):
                for j, _ in enumerate(cols):
                    # Hence distance of a string to itself is 1
                    if i == j:
                        fuzz_matrix[i][j] = 1
                    else:
                        # Removing noise edits by lowercasing strings
                        rows[i] = rows[i].lower()
                        cols[j] = cols[j].lower()

                        # Reducing noise by replacing predefined reserved words
                        if self.reserved_words:
                            for key, value in self.reserved_words.items():
                                rows[i] = rows[i].replace(key, value)
                                cols[j] = cols[j].replace(key, value)

                        if partial:
                            partial_ratio = fuzz.partial_ratio(rows[i], cols[j])
                            fuzz_matrix[i][j] = partial_ratio
                        elif token_set:
                            token_set_ratio = fuzz.partial_ratio(rows[i], cols[j])
                            fuzz_matrix[i][j] = token_set_ratio
                        elif token_sort:
                            token_sort_ratio = fuzz.partial_ratio(rows[i], cols[j])
                            fuzz_matrix[i][j] = token_sort_ratio
                        else:
                            ratio = fuzz.ratio(rows[i], cols[j])
                            fuzz_matrix[i][j] = ratio
        return fuzz_matrix
