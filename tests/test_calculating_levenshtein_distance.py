import sys
import os
import csv
import logging
import pytest
from pathlib import Path

src_module_path = Path().resolve().parent / "src" / "levenshtein_distance"
sys.path.append(str(src_module_path))
from string_distance import StringDistance

lev_distance = StringDistance()
distance_of_three = lev_distance.lev_distances_raw_strs("kitten", "sitting")
assert distance_of_three == 3

