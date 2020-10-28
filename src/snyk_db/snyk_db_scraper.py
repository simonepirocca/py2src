import os, time
from html.parser import HTMLParser
from urllib.request import urlopen
import urllib.request, urllib.error
import random

cwd = os.path.dirname(__file__)
DATA_FOLDER = os.path.join(cwd, '..', '..', 'data')
SNYK_DB_FILE = os.path.join(DATA_FOLDER, 'snyk_{}_db.csv')
BASE_URL = 'https://snyk.io/vuln/page/{}?type={}'
SLEEP_TIME = (3, 5)
SNYK_VULN_PAGE_BASE_URL = 'https://snyk.io'


class SnykDbScraper(HTMLParser):
    def __init__(self, url, type='maven'):
        HTMLParser.__init__(self)
        self.url = url
        self.vuln_db = [] # each element is a triple <ga;version_range;vuln_link>
        self.in_row = False
        self.gav_found = False
        self.ver_range_found = False
        self.type = type

    def handle_starttag(self, tag, attrs):
        if not self.in_row and tag == 'a':
            for (key, value) in attrs:
                if key == 'href' and value.startswith('/vuln/SNYK'):
                    self.in_row = True
                    self.vuln_db.append(';{}'.format(value))

        elif self.in_row and not self.gav_found and tag == 'a':
            for (key, value) in attrs:
                if key == 'href' and value.startswith('/vuln/{}:'.format(self.type)):
                    self.gav_found = True

        elif self.in_row and tag == 'span':
            for (key, value) in attrs:
                if key == 'class' and value == 'semver':
                    self.ver_range_found = True

    def handle_data(self, data):
        if self.gav_found:
            self.vuln_db[-1] = '{}{}'.format(data, self.vuln_db[-1])
            self.gav_found = False

        if self.ver_range_found:
            ga, link = self.vuln_db[-1].split(';')
            self.vuln_db[-1] = '{};{};{}'.format(ga, data, link)

            self.in_row = False
            self.gav_found = False
            self.ver_range_found = False

    # This function gets the links of a given page (used for recurring through pages)
    # as well as the poms that were found in the target page
    def parse(self):
        sleep = random.randint(*SLEEP_TIME)
        print('Scraping page ' + self.url)
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
            try:
                response = urllib.request.urlopen(self.url)
            except Exception as e:
                print('Exception occured while processing page ' + str(self.url))
                print(e)
                return []

        try:
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            print('Information successfully retrieved')
            return self.vuln_db
        except Exception as e:
            print('There was an error, while trying to decode ' + self.url)
            print(str(e))
            return []


class SnykVulnPageScraper(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = '{}{}'.format(SNYK_VULN_PAGE_BASE_URL, url)
        self.cve = ''
        self.cwe = ''
        self.commit = ''
        self.in_dd = False

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href' and 'github' in value and 'commit' in value:
                    self.commit = value.strip()
        elif tag == 'dd':
            self.in_dd = True

    def handle_endtag(self, tag):
        if tag == 'dd':
            self.in_dd = False

    def handle_data(self, data):
        if self.in_dd and 'CVE-' in data:
            self.cve = data.strip()
        elif self.in_dd and 'CWE-' in data:
            self.cwe = data.strip()

    def parse(self):
        sleep = random.randint(*SLEEP_TIME)
        print('Scraping page ' + self.url)
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
            try:
                response = urllib.request.urlopen(self.url)
            except Exception as e:
                print('Exception occured while processing page ' + str(self.url))
                print(e)
                return []

        try:
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            print('Information successfully retrieved')
            return self.cve, self.cwe, self.commit
        except Exception as e:
            print('There was an error, while trying to decode ' + self.url)
            print(str(e))
            return '', '', ''

def isJavaCommit(url):
    sleep = random.randint(*SLEEP_TIME)
    print('Sleeping for {} seconds ...'.format(sleep))
    time.sleep(sleep)
    retry = False
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print('Web page {} not found'.format(url))
            return False
        else:
            print('Exception occured while processing page ' + str(url))
            print(e)
            retry = True
    except Exception as e:
        print('Error occured while opening page ' + str(url))
        print(e)
        return False

    if retry:
        sleep = 60
        print('Sleeping for {} seconds ...'.format(sleep))
        time.sleep(sleep)
        try:
            response = urllib.request.urlopen(url)
        except Exception as e:
            print('Exception occured while processing page ' + str(url))
            print(e)
            return False

    if response.getheader('Content-Type') == 'text/html; charset=utf-8':
        htmlBytes = response.read()
        htmlString = htmlBytes.decode("utf-8").splitlines()

        for line in htmlString:
            if '.java' in line.lower():
                print(line)
                return True
    return False

class SnykDbAugmentor:
    def __init__(self, snyk_db_file=SNYK_DB_FILE, type='maven'):
        self.snyk_db_file = snyk_db_file.format(type)
        self.snyk_db = []

    def augmentDB(self):
        try:
            with open(self.snyk_db_file, 'r') as f_in:
                count = 0
                for line in f_in:
                    print('-'*80)
                    print('Processing line {}'.format(count))
                    print('-' * 80)
                    count += 1

                    if line.startswith('ga;version_range'):
                        line_to_write = 'ga;version_range;vuln_link;cveid;cwe;commit;java_file_changed\n'
                    else:
                        vuln_link = line.split(';')[2]
                        vuln_page_scraper = SnykVulnPageScraper(vuln_link)
                        cve, cwe, commit = vuln_page_scraper.parse()
                        line_to_write = '{};{};{};{};{}\n'.format(line.strip(), cve, cwe, commit, isJavaCommit(commit))

                    try:
                        with open(self.snyk_db_file[: -4] + '_augmented.csv', 'a') as f_out:
                            f_out.write(line_to_write)
                    except OSError as e:
                        print('There was an error, while opening file {} for writing'.format(self.snyk_db_file[: -4] + '_augmented.csv'))
                        print(str(e))
        except OSError as e:
            print('There was an error, while opening file {}'.format(self.snyk_db_file))
            print(str(e))


if __name__ == '__main__':
    # type = 'maven' #types could be 'maven', 'pip', etc.
    type = 'maven'
    with open(SNYK_DB_FILE.format(type), 'w') as f_out:
        f_out.write('ga;version_range;vuln_link\n')
    for i in range(1, 75):
        scraper = SnykDbScraper(url=BASE_URL.format(i, type), type=type)
        ga_list = scraper.parse()

        with open(SNYK_DB_FILE.format(type), 'a') as f_out:
            for line in ga_list:
                f_out.write('{}\n'.format(line))

    snykDBaugmentor = SnykDbAugmentor(type=type)
    snykDBaugmentor.augmentDB()
