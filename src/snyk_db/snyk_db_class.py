import os, csv, re
from pkg_resources import parse_version
from src.Dependency import Dependency, DependencyExtended

cwd = os.path.dirname(__file__)
DATA_FOLDER = os.path.join(cwd, '..', '..', 'data')
INPUT_FILE = os.path.join(DATA_FOLDER, 'snyk_{}_db_augmented.csv')

class SnykDB:
    def __init__(self, input_file=INPUT_FILE, type='maven'):
        self.input_file = input_file.format(type)
        self.vuln_db = dict()
        self.loadDB()
        self.type = type.lower()

    def loadDB(self):
        try:
            with open(self.input_file, 'r', newline='') as f_in:
                reader = csv.reader(f_in, delimiter=';')
                for line in reader:
                    if line[0] == 'ga':
                        continue

                    if not line[0] in self.vuln_db:
                        self.vuln_db[line[0]] = []
                    self.vuln_db[line[0]].append('{}::{}'.format(line[1], line[3]))
            print('Snyk DB was successfully loaded and has entries for {} gavs'.format(len(self.vuln_db)))
        except OSError as e:
            print('There was an error, while trying to open file {}'.format(self.input_file))
            print(str(e))
        except Exception as e:
            print('There was an exception, while processing information from file {}'.format(self.input_file))
            print(str(e))

    def clean_version(self, version):
        version = re.sub(r'[A-Z]|[a-z]', '', version)
        version = re.sub(r'\.\.', '', version)
        if version.startswith('.'): version = version[1:]
        if version.endswith('.'): version = version[:-1]
        return version

    def isVersionBigger(self, version, int_border):
        ver_equal = '[' in version or ']' in version or re.sub('[()\[\]]', '', version) == version

        int_border_equal = '[' in int_border or ']' in int_border

        if int_border == '[' or int_border == '(':
            return True
        if version == '[' or version == '(':
            return False
        if version == ']' or version == ')':
            return True
        if int_border == ']' or int_border == ')':
            return False

        version = re.sub(r'[()\[\]]', '', version)
        int_border = re.sub(r'[()\[\]]', '', int_border)

        version = self.clean_version(version)
        int_border = self.clean_version(int_border)

        if ver_equal and int_border_equal:
            return parse_version(version) >= parse_version(int_border)
        else:
            return parse_version(version) > parse_version(int_border)

    def isVersionSmaller(self, version, int_border):
        ver_equal = '[' in version or ']' in version or re.sub('[()\[\]]', '', version) == version

        int_border_equal = '[' in int_border or ']' in int_border

        if version == '[' or version == '(':
            return True
        if int_border == '[' or int_border == '(':
            return False
        if int_border == ']' or int_border == ')':
            return True
        if version == ']' or version == ')':
            return False

        version = re.sub(r'[()\[\]]', '', version)
        int_border = re.sub(r'[()\[\]]', '', int_border)

        version = self.clean_version(version)
        int_border = self.clean_version(int_border)

        if ver_equal and int_border_equal:
            return parse_version(version) <= parse_version(int_border)
        else:
            return parse_version(version) < parse_version(int_border)

    def isInterval(self, version):
        return '[' in version or '(' in version or ']' in version or ')' in version

    def inInterval(self, version, intervals):
        intervals = re.sub(' ', '', intervals)
        intervals = re.sub('\),', ');', intervals)
        intervals = re.sub('],', '];', intervals)
        intervals = re.sub(';,', ';', intervals)

        for interval in intervals.split(';'):
            if not ',' in interval:
                continue
            try:
                left, right = interval.split(',')

                is_bigger = self.isVersionBigger(version, left)
                is_smaller = self.isVersionSmaller(version, right)
                if is_bigger and is_smaller:
                    return True
            except Exception as e:
                print('There was an error, while trying to identify whether {} belongs to {}'.format(version, intervals))
                print(str(e))
                continue
        return False

    def isIntersection(self, interval1, interval2):
        intervals = re.sub(' ', '', interval2)
        intervals = re.sub('\),', ');', intervals)
        intervals = re.sub('\],', '];', intervals)

        intervals = re.sub('\]', ')', intervals)# change border brackets, because we'll check for absence of intersection later on
        intervals = re.sub('\)', ']', intervals)
        intervals = re.sub('\[', '(', intervals)
        intervals = re.sub('\(', '[', intervals)

        # interval1 = re.sub(':', ',', interval1)
        for interval in intervals.split(';'):
            try:
                left_a, right_a = interval1.split(',')

                left_b, right_b = interval.split(',')

                if not (self.isVersionSmaller(right_a, left_b) or self.isVersionBigger(left_a, right_b)):
                    return True
            except Exception as e:
                print(
                    'There was an error, while trying to identify whether {} belongs to {}'.format(interval1, interval))
                print(str(e))
                continue
        return False

    def checkGAV(self, gav):
        # returns None if gav has wrong format (right format is "group:artifact:version")
        # returns 0 if gav is not found in the database
        # returns #vulns if gav is found

        # try:
        #     group, artifact, version = Dependency(gav).getGAV().split(':')
        # except Exception as e:
        #     print('"{}" does not have a correct gav format'.format(gav))
        #     print(str(e))
        #     return

        dep = Dependency(gav)
        ga = dep.getGA()
        if not ga in self.vuln_db:
            return 0
        else:
            num_vulns = 0
            for info in self.vuln_db[ga]:
                if self.inInterval(dep.getVersion(), info.split('::')[0]):
                    num_vulns += 1
            return num_vulns

    # def checkPkg(self, pkg):
    #     # returns None if gav has wrong format (right format is "group:artifact:version")
    #     # returns 0 if gav is not found in the database
    #     # returns #vulns if gav is found
    #     try:
    #         name, version = pkg.split(':')
    #     except:
    #         return None
    #
    #     dep = PyPackage(name, version)
    #     if not dep.getName() in self.vuln_db:
    #         return 0
    #     else:
    #         num_vulns = 0
    #         for info in self.vuln_db[dep.getName()]:
    #             if self.isInterval(dep.getVersion()):
    #                 if self.isIntersection(dep.getVersion(), info.split('::')[0]):
    #                     num_vulns += 1
    #             else:
    #                 if self.inInterval(dep.getVersion(), info.split('::')[0]):
    #                     num_vulns += 1
    #         return num_vulns

    def checkLib(self, lib):
        if self.type == 'maven':
            return self.checkGAV(lib)
        # elif self.type == 'pip':
        #     return self.checkPkg(lib)

    def getCVEfromGAV(self, gav):
        dep = Dependency(gav)
        ga = dep.getGA()
        if not ga in self.vuln_db:
            return []
        else:
            cves = []
            for info in self.vuln_db[ga]:
                if self.inInterval(dep.getVersion(), info.split('::')[0]):
                    cve = info.split('::')[-1]
                    if cve != '':
                        cves.append(cve)
            return cves

    # def getCVEfromPkg(self, pkg):
    #     try:
    #         name, version = pkg.split(':')
    #     except:
    #         return []
    #     dep = PyPackage(name, version)
    #     if not dep.getName() in self.vuln_db:
    #         return []
    #     else:
    #         cves = []
    #         for info in self.vuln_db[dep.getName()]:
    #             if self.isInterval(dep.getVersion()):
    #                 if self.isIntersection(dep.getVersion(), info.split('::')[0]):
    #                     cve = info.split('::')[-1]
    #                     if cve != '':
    #                         cves.append(cve)
    #             else:
    #                 if self.inInterval(dep.getVersion(), info.split('::')[0]):
    #                     cve = info.split('::')[-1]
    #                     if cve != '':
    #                         cves.append(cve)
    #         return cves

    def getCVE(self, lib):
        if self.type == 'maven':
            return self.getCVEfromGAV(lib)
        # elif self.type == 'pip':
        #     return self.getCVEfromPkg(lib)

    def getVulnFromList(self, dependencies):
        vuln_dep = []
        if dependencies is None:
            return vuln_dep
        for dep in dependencies:
            dep_to_check = Dependency(dep).getGAV()
            if self.checkGAV(dep_to_check):
                vuln_dep.append(dep)
        return vuln_dep

    def getCVEfromList(self, dependencies):
        cve_set = set()
        for dep in dependencies:
            dep_to_check = Dependency(dep).getGAV()
            cves = self.getCVE(dep_to_check)
            if len(cves) > 0:
                for cve in cves:
                    cve_set.add(cve)
        return cve_set

    def get_safe_from_list(self, dependencies):
        safe_dep = []
        for dep in dependencies:
            dep_to_check = Dependency(dep).getGAV()
            if self.checkGAV(dep_to_check) == 0:
                safe_dep.append(dep)
        return safe_dep

    def get_all_safe_gavs(self, gav):
        dep = DependencyExtended(gav)
        all_versions = dep.getAllVersions()
        all_gavs = ['{}:{}'.format(dep.getGA(), version) for version in all_versions]
        return self.get_safe_from_list(all_gavs)

    def get_all_vuln_gavs(self, gav):
        dep = DependencyExtended(gav)
        all_versions = dep.getAllVersions()
        all_gavs = ['{}:{}'.format(dep.getGA(), version) for version in all_versions]
        return self.getVulnFromList(all_gavs)

    def get_safe_gavs_later(self, gav):
        dep = DependencyExtended(gav)
        later_versions = dep.get_later_versions()
        later_gavs = ['{}:{}'.format(dep.getGA(), version) for version in later_versions]
        return self.get_safe_from_list(later_gavs)

    def get_safe_gavs_earlier(self, gav):
        dep = DependencyExtended(gav)
        earlier_versions = dep.get_earlier_versions()
        earlier_gavs = ['{}:{}'.format(dep.getGA(), version) for version in earlier_versions]
        return self.get_safe_from_list(earlier_gavs)

    def get_changes_in_between(self, gav_earlier, gav_later):
        cve_earlier = set(self.getCVE(gav_earlier))
        cve_later = set(self.getCVE(gav_later))
        fixed = cve_earlier.difference(cve_later)
        still_present = cve_earlier.intersection(cve_later)
        introduced = cve_later.difference(cve_earlier)
        return (fixed, still_present, introduced)


if __name__ == '__main__':
    # gav_list = ['org.jenkins-ci.main:jenkins-core:1.1', 'org.jenkins-ci.main:jenkins-core:1.625.3', 'org.jenkins-ci.main:jenkins-core:1.630', 'org.jenkins-ci.main:jenkins-core:1.631', 'org.jenkins-ci.main:jenkins-core:1.641']
    gav_list = ['requests:[1.1,2.20]']
    snyk_db = SnykDB(type='maven')
    print(snyk_db.checkGAV('com.fasterxml.jackson.core:jackson-databind:2.9.5'))
    # print(snyk_db.inInterval('2.7.1', '[,2.7.1]'))
    print(snyk_db.inInterval('1.2.3', '[1.2.1,3.1.4.RELEASE];,[3.2.0.RELEASE,3.2.18.RELEASE);[4.2.0.RELEASE,4.2.9.RELEASE);[4.3.0.RELEASE,4.3.5.RELEASE)'))

    # for gav in gav_list:
    #     print(snyk_db.checkLib(gav))
    #     print(snyk_db.getCVE(gav))







