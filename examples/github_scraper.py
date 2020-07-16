import sys
import os
import time
import random

from html.parser import HTMLParser
from urllib.request import urlopen
import urllib.request
from urllib import parse
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


cwd = os.path.dirname(__file__)
VERBOSE = False
BASE_GITHUB_URL = 'https://github.com'
PAGES = (1, 10)
SLEEP_TIME = (3, 5)
PROJECT_LIST_FILENAME = os.path.join(cwd, '..', 'data', 'mvnrepository_popular_ga.txt')
# URL_TO_CRAWL = "https://github.com/search?p={}&o=desc&s=stars&q=language%3AJava&type=Repositories"
URL_TO_CRAWL = "https://mvnrepository.com/popular?p={}"


class GithubProjectScraper(HTMLParser):
    def __init__(self, url, stop_count=None):
        HTMLParser.__init__(self)
        self.url = url
        self.links = set()
        self.in_h3 = False
        self.stop_count = stop_count
        self.stop = False

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.in_h3 = True
        elif len(self.links) < self.stop_count and self.in_h3 and tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.url, value)
                    self.links.add(newUrl)
                    if len(self.links) == self.stop_count:
                        self.stop = True

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_h3 = False

    # This function gets the links of a given page (used for recurring through pages)
    # as well as the poms that were found in the target page
    def parse(self):
        sleep = random.randint(*SLEEP_TIME)
        print('Sleeping for {} seconds ...'.format(sleep))
        time.sleep(sleep)
        retry = False
        try:
            response = urllib.request.urlopen(self.url)
        except Exception as e:
            print('Exception occured while processing page ' + str(self.url))
            print(e)
            retry = True

        if retry:
            sleep = 60
            print('Sleeping for {} seconds ...'.format(sleep))
            time.sleep(sleep)
            response = urllib.request.urlopen(self.url)

        if response.getheader('Content-Type') == 'text/html; charset=utf-8':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            for link in htmlString.splitlines():
                if self.stop:
                    break
                self.feed(link)
            return self.links
        else:
            return set()


class GithubPomScraper(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.in_a = False
        self.pom_found = False

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            pom_title = False
            pom_href = False
            for (key, value) in attrs:
                if key == 'href' and value.endswith('pom.xml'):
                    pom_href = True
                elif key == 'title' and value == 'pom.xml':
                    pom_title = True
            if pom_href and pom_title:
                self.in_a = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_a = False

    def handle_data(self, data):
        if self.in_a and data == 'pom.xml':
            self.pom_found = True

    # This function gets the links of a given page (used for recurring through pages)
    # as well as the poms that were found in the target page
    def parse(self):
        sleep = random.randint(*SLEEP_TIME)
        print('Sleeping for {} seconds ...'.format(sleep))
        time.sleep(sleep)
        retry = False
        try:
            response = urllib.request.urlopen(self.url)
        except Exception as e:
            print('Exception occured while processing page ' + str(self.url))
            print(e)
            retry = True

        if retry:
            sleep = 60
            print('Sleeping for {} seconds ...'.format(sleep))
            time.sleep(sleep)
            response = urllib.request.urlopen(self.url)

        if response.getheader('Content-Type') == 'text/html; charset=utf-8':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            for link in htmlString.splitlines():
                if self.pom_found:
                    break
                self.feed(link)
            return self.pom_found
        else:
            return False

class MVNRepositoryProjectScraper(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.ga_set = set()
        self.in_div_im = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for (key, value) in attrs:
                if key == 'class' and value == 'im':
                    self.in_div_im = True
        elif self.in_div_im and tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newGA = value[len('/artifact/'):].replace('/', ':')
                    self.ga_set.add(newGA)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_div_im = False

    # This function gets the links of a given page (used for recurring through pages)
    # as well as the poms that were found in the target page
    def parse(self):
        response = urllib.request.urlopen(self.url)
        if response.getheader('Content-Type').lower() == 'text/html; charset=utf-8':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return self.ga_set
        else:
            return set()


class GithubReleaseScraper(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.releases = []
        self.found_parent_tag = False
        self.found_release_id = False

    def handle_starttag(self, tag, attrs):
        # if tag == 'h1' and 'release-title' in attrs['class']:
        if tag == 'ul':
            for name, value in attrs:
                if name == 'class' and 'tag-references' in value:
                    # print('Found ul.tag-references')
                    self.found_parent_tag = True
                    return
                else:
                    # print('self.found_parent_tag = False')
                    self.found_parent_tag = False
        elif tag == 'span' and self.found_parent_tag:
            # print('Found span in ul.tag-references')
            # print('self.found_parent_tag =' + str(self.found_parent_tag))
            self.found_release_id = True
            # self.found_parent_tag = False
            return
        elif tag == 'span' and ('class', 'tag-name') in attrs:
            # for certain pages it is enough to just get this type of span
            # print('Found span.tag-name')
            self.found_release_id = True
            # self.found_parent_tag = False

    def handle_data(self, data):
        if self.found_release_id:
            # print('Processing data: ' + data)
            if len(data.strip()) > 0:
                self.releases.append(data)
                self.found_parent_tag = False
                self.found_release_id = False
            # else:
            #     print('No data, skippping')

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.found_parent_tag = False

    # This function gets the links of a given page (used for recurring through pages)
    # as well as the poms that were found in the target page
    def parse(self):
        sleep = random.randint(*SLEEP_TIME)
        print('Sleeping for {} seconds ...'.format(sleep))
        time.sleep(sleep)
        retry = False
        try:
            print('Scraping latest release for ' + self.url)
            response = urllib.request.urlopen(self.url)
        except Exception as e:
            print('Exception occured while processing page ' + str(self.url))
            print(e)
            retry = True

        if retry:
            sleep = 60
            print('Sleeping for {} seconds ...'.format(sleep))
            time.sleep(sleep)
            response = urllib.request.urlopen(self.url)

        if response.getheader('Content-Type').lower() == 'text/html; charset=utf-8':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return self.releases
        else:
            return []


class Crawler(HTMLParser):

    def __init__(self, url, pages=PAGES, output_dir=None):
        super().__init__()
        self.pages_to_crawls = pages
        self.pagesVisited = set()
        self.numberVisited = 0
        self.collectedItems = set()
        if not url is None:
            self.startUrl = url

        self.timing = {}
        self.output_dir = output_dir

    def collect(self, data):
        self.collectedItems |= set(data)

    def getCollectedItems(self, filter=True):
        return self.collectedItems


class GithubCrawler(Crawler):
    def crawl(self):
        # scans target website and collects links using self.collect()
        start_time = time.time()

        search_term = ''
        retry = False

        if isinstance(self.pages_to_crawls, tuple):
            range_interval = (self.pages_to_crawls[0], self.pages_to_crawls[1] + 1)
        else:
            range_interval = self.pages_to_crawls + 1

        for i in range(*range_interval):

            sleep = 5
            if i % 2 == 0:
                sleep = random.randint(*SLEEP_TIME)
            print('Sleeping for {} seconds ...'.format(sleep))
            time.sleep(sleep)

            print('Retrieving page {} / {}'.format(i, self.pages_to_crawls[1]))
            try:
                scrape_url = self.startUrl.format(i)
                print('Scanning {}'.format(scrape_url))

                if 'github' in self.startUrl:
                    scraper = GithubProjectScraper(scrape_url)
                else:
                    print('The scraper for {} is not supported yet'.format(self.startUrl))
                    raise Exception('The scraper for {} is not supported yet'.format(self.startUrl))

                results = scraper.parse()
                self.collect(results)
            except Exception as e:
                print('Exception occured while processing page ' + str(i))
                print(e)
                retry = True

            if retry:
                sleep = 60
                print('Sleeping for {} seconds ...'.format(sleep))
                time.sleep(sleep)
                print('(RETRY) Retrieving page {} / {}'.format(i, self.pages_to_crawls[1]))
                try:
                    scrape_url = self.startUrl.format(i)
                    print('Scanning {}'.format(scrape_url))

                    if 'github' in self.startUrl.lower():
                        scraper = GithubProjectScraper(scrape_url)
                    else:
                        print('The scraper for {} is not supported yet'.format(self.startUrl))
                        raise Exception('The scraper for {} is not supported yet'.format(self.startUrl))

                    results = scraper.parse()
                    self.collect(results)
                    retry = False
                except Exception as e:
                    print('Exception occured while processing page ' + str(i))
                    print(e)
                    print('Crawling stops here')
                    break

            print(str(self.getCollectedItems()))

        end_time = time.time()
        self.timing['crawl'] = end_time - start_time


class MVNRepositoryCrawler(Crawler):
    def crawl(self):
        # scans target website and collects links using self.collect()
        start_time = time.time()

        search_term = ''
        retry = False

        if isinstance(self.pages_to_crawls, tuple):
            range_interval = (self.pages_to_crawls[0], self.pages_to_crawls[1] + 1)
        else:
            range_interval = self.pages_to_crawls + 1

        for i in range(*range_interval):

            sleep = 5
            if i % 2 == 0:
                sleep = random.randint(*SLEEP_TIME)
            print('Sleeping for {} seconds ...'.format(sleep))
            time.sleep(sleep)

            print('Retrieving page {} / {}'.format(i, self.pages_to_crawls[1]))
            try:
                scrape_url = self.startUrl.format(i)
                print('Scanning {}'.format(scrape_url))

                if 'mvnrepository' in self.startUrl.lower():
                    scraper = MVNRepositoryProjectScraper(scrape_url)
                else:
                    print('The scraper for {} is not supported yet'.format(self.startUrl))
                    raise Exception('The scraper for {} is not supported yet'.format(self.startUrl))

                results = scraper.parse()
                self.collect(results)
            except Exception as e:
                print('Exception occured while processing page ' + str(i))
                print(e)
                retry = True

            if retry:
                sleep = 60
                print('Sleeping for {} seconds ...'.format(sleep))
                time.sleep(sleep)
                print('(RETRY) Retrieving page {} / {}'.format(i, self.pages_to_crawls[1]))
                try:
                    scrape_url = self.startUrl.format(i)
                    print('Scanning {}'.format(scrape_url))

                    if 'mvnrepository' in self.startUrl.lower():
                        scraper = MVNRepositoryProjectScraper(scrape_url)
                    else:
                        print('The scraper for {} is not supported yet'.format(self.startUrl))
                        raise Exception('The scraper for {} is not supported yet'.format(self.startUrl))

                    results = scraper.parse()
                    self.collect(results)
                    retry = False
                except Exception as e:
                    print('Exception occured while processing page ' + str(i))
                    print(e)
                    print('Crawling stops here')
                    break

            print(str(self.getCollectedItems()))

        end_time = time.time()
        self.timing['crawl'] = end_time - start_time

# class GithubCrawler(HTMLParser):
#
#     def __init__(self, url=None, pages=(1, 10), output_dir=None):
#
#         self.pages_to_crawls = pages
#         self.pagesVisited = set()
#         self.numberVisited = 0
#         self.collectedItems = set()
#         if not url is None:
#             self.startUrl = url
#         else:
#             self.startUrl = "https://github.com/search?p={}&o=desc&s=stars&q=language%3AJava&type=Repositories"
#
#         self.timing = {}
#         self.output_dir = output_dir
#
#     def collect(self, data):
#         self.collectedItems |= set(data)
#
#     def crawl(self):
#         # scans target website and collects links using self.collect()
#         start_time = time.time()
#
#         search_term = ''
#         retry = False
#
#         for i in range(*PAGES):
#
#             sleep = 5
#             if i % 2 == 0:
#                 sleep = random.randint(*SLEEP_TIME)
#             print('Sleeping for {} seconds ...'.format(sleep))
#             time.sleep(sleep)
#
#             print('Retrieving page {} / {}'.format(i, PAGES[1]))
#             try:
#                 github_url = self.startUrl.format(i)
#                 print('Scanning {}'.format(github_url))
#                 scraper = GithubProjectScraper(github_url)
#                 results = scraper.parse()
#                 self.collect(results)
#             except Exception as e:
#                 print('Exception occured while processing page ' + str(i))
#                 print(e)
#                 retry = True
#
#             if retry:
#                 sleep = 60
#                 print('Sleeping for {} seconds ...'.format(sleep))
#                 time.sleep(sleep)
#                 print('(RETRY) Retrieving page {} / {}'.format(i, PAGES[1]))
#                 try:
#                     github_url = self.startUrl.format(i)
#                     print('Scanning {}'.format(github_url))
#                     scraper = GithubProjectScraper(github_url)
#                     results = scraper.parse()
#                     self.collect(results)
#                     retry = False
#                 except Exception as e:
#                     print('Exception occured while processing page ' + str(i))
#                     print(e)
#                     print('Crawling stops here')
#                     break
#
#             print(str(self.getCollectedItems()))
#
#         end_time = time.time()
#         self.timing['crawl'] = end_time - start_time
#
#     def getCollectedItems(self, filter=True):
#         return self.collectedItems


if __name__ == '__main__':
    start_time = time.time()

    url = URL_TO_CRAWL

    project_crawler = MVNRepositoryCrawler(url=url)
    project_crawler.crawl()
    print('Done crawling projects in {} seconds'.format(int(project_crawler.timing['crawl'])))
    collected_ga = project_crawler.getCollectedItems()

    with open(PROJECT_LIST_FILENAME, 'a', newline='', encoding='utf8') as f:
        f.write('# ------------------------------\n')
        for p in collected_ga:
            f.write(p + '\n')

    # sys.exit()
    # for u in collected_project_urls:
    #     # print(u)
    #     sleep = random.randint(*SLEEP_TIME)
    #     # if i % 3 == 0:
    #     #     sleep = 30
    #     print('Sleeping for {} seconds ...'.format(sleep))
    #     time.sleep(sleep)  # Sleep for 15 seconds every fifth page
    #     release_crawler = GithubReleaseScraper(u + '/releases')
    #     releases = release_crawler.parse()
    #     if len(releases) == 0:
    #         continue
    #     print("{}:{}".format(u, releases[0]))
    # # with open(output_file, 'a', newline='', encoding='utf8') as f_out:
    # #     writer = csv.writer(f_out, delimiter=';')
    # #     for j in range(0, len(url_list)):
    # #         writer.writerow([url_list[j], tag_list[j]])
    #
    # elapsed_time = time.time() - start_time
    # elapsed_time_minutes = int(elapsed_time / 60)
    # elapsed_time_seconds = int(elapsed_time % 60)
    # print("Crawling and scan completed in {}m{}s".format(elapsed_time_minutes, elapsed_time_seconds))

    # -------------------previous main function------------------------------------------------------
    # start_time = time.time()
    #
    # url = "https://github.com/search?p={}&o=desc&s=stars&q=language%3AJava&type=Repositories"
    #
    # project_crawler = GithubCrawler(pages=PAGES)
    # project_crawler.crawl()
    # print('Done crawling projects in {} seconds'.format(int(project_crawler.timing['crawl'])))
    # collected_project_urls = project_crawler.getCollectedItems()
    #
    # with open(PROJECT_LIST_FILENAME, 'a', newline='', encoding='utf8') as f:
    #     f.write('# ------------------------------\n')
    #     for p in collected_project_urls:
    #         f.write(p + '\n')
    #
    # sys.exit()
    # for u in collected_project_urls:
    #     # print(u)
    #     sleep = random.randint(*SLEEP_TIME)
    #     # if i % 3 == 0:
    #     #     sleep = 30
    #     print('Sleeping for {} seconds ...'.format(sleep))
    #     time.sleep(sleep)  # Sleep for 15 seconds every fifth page
    #     release_crawler = GithubReleaseScraper(u + '/releases')
    #     releases = release_crawler.parse()
    #     if len(releases) == 0:
    #         continue
    #     print ("{}:{}".format(u, releases[0]))
    # # with open(output_file, 'a', newline='', encoding='utf8') as f_out:
    # #     writer = csv.writer(f_out, delimiter=';')
    # #     for j in range(0, len(url_list)):
    # #         writer.writerow([url_list[j], tag_list[j]])
    #
    # elapsed_time = time.time() - start_time
    # elapsed_time_minutes = int(elapsed_time / 60)
    # elapsed_time_seconds = int(elapsed_time % 60)
    # print("Crawling and scan completed in {}m{}s".format(elapsed_time_minutes, elapsed_time_seconds))
