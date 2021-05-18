import pytest
from ..src.url_finder import URLFinder
from ..src.string_distance import StringDistance

class GetFinalURL:
    def __init__(self, package_name: str):
        self._package_name = package_name

    # Get the metrics and return the array
    def get_final_url(self):
        # Instanziate package
        finder = URLFinder(self._package_name)

        # Get URLs from sources
        ossgadget_url = finder.find_ossgadget_url("pypi")
        #ossgadget_github_url = finder.find_ossgadget_url("github")
        badge_url = finder.find_github_url_from_pypi_badge()
        homepage_url = finder.mode_2()
        metadata_url = finder.mode_1()
        #page_conservative_url = finder.mode_3()
        #page_majority_url = finder.find_github_url_from_pypi_page()
        readthedocs_url = finder.find_github_url_from_readthedocs()
        statistics_url = finder.find_github_url_from_pypi_statistics()

        proposed_urls = [badge_url, homepage_url, metadata_url, readthedocs_url, statistics_url]

        # Calculate different URLs
        mode_urls = {}
        for tmp_url in proposed_urls:
            if tmp_url != "":
                if tmp_url in mode_urls: mode_urls[tmp_url] += 1
                else: mode_urls[tmp_url] = 1

        # Evaluate Mode URL
        occ_mode_url = 0
        mode_url = ""
        for url in mode_urls:
            count = mode_urls[url]
            if count > occ_mode_url:
                occ_mode_url = count
                mode_url = url

        # Evaluate Final URL
        if mode_url != "": final_url = mode_url
        else: final_url = ossgadget_url

        final_url_score = ""
        if final_url != "":
            finder.set_github_url(final_url)

            if final_url[-1] != "/": url_package_name = final_url.split("/")[-1]
            else: url_package_name = final_url.split("/")[-2]

            # Calculate Levenshtein distance and similarity between package names
            lev_distance = StringDistance().lev_distances_raw_strs(url_package_name, self._package_name)
            len1 = len(url_package_name)
            len2 = len(self._package_name)
            if len1 > len2: max_lev_dist = len1
            else: max_lev_dist = len2
            lev_dist_text = str(lev_distance) + "/" + str(max_lev_dist)

            similarity = "Different"
            if url_package_name == self._package_name: similarity = "Equal"
            elif url_package_name in self._package_name or self._package_name in url_package_name: similarity = "Substring"

            # Check Levenshtein distance between PyPI and GitHub descriptions
            pypi_descr = finder.get_pypi_descr().replace("\n","")
            github_descr = finder.get_github_descr().replace("\n","")
            descr_distance = StringDistance().lev_distances_raw_strs(pypi_descr, github_descr)
            len1 = len(pypi_descr)
            len2 = len(github_descr)
            if len1 > len2: max_descr_dist = len1
            else: max_descr_dist = len2
            descr_dist_text = str(descr_distance) + "/" + str(max_descr_dist)

            # Get PyPI badge, Python and other languages on GitHub page
            github_badge = str(finder.check_pypi_badge())
            python_lang = finder.check_python_lang()
            other_languages = finder.get_other_lang()

            # Calculate Name similarity score
            if lev_dist_text != "":
                lev_distance = lev_dist_text.split("/")[0]
                if lev_distance == "0" or lev_distance == "1" or similarity == "Substring": score_1 = 1
                else: score_1 = -1
            else: score_1 = 0

            # Calculate Description similarity score
            if descr_dist_text != "":
                descr_distance = float(descr_dist_text.split("/")[0])
                descr_len = float(descr_dist_text.split("/")[1])
                dist_len_rel = 0
                if descr_len != 0: dist_len_rel = round(float(descr_distance / descr_len), 3)
                if dist_len_rel < 0.5: score_2 = 1
                else: score_2 = -1
            else: score_2 = 0

            # Calculate PyPI badge score
            if github_badge == "True": score_3 = 1
            elif github_badge == "False" or github_badge == "": score_3 = 0
            else: score_3 = -1

            # Calculate Python language score
            perc = 0
            if python_lang == "": score_4 = 0
            elif python_lang != "0%": score_4 = 1
            else:
                if other_languages == "": score_4 = 0
                else: score_4 = -1

            final_url_score = score_1 + score_2 + score_3 + score_4

        url_data = [final_url, final_url_score]
        return url_data