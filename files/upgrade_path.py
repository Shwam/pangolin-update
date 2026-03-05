import requests
from functools import total_ordering
import re
import sys
import json
import time

@total_ordering
class Version:
    def __init__(self, version):
        self.version = version

    def __lt__(self, rhs):
        my_vals = [re.sub(r'[^0-9]', '', v) for v in self.version.split(".")]
        rhs_vals = [re.sub(r'[^0-9]', '', v) for v in rhs.version.split(".")]
        for i in range(max(len(my_vals), len(rhs_vals))):
            try:
                my_val = int(my_vals[i])
            except Exception as err:
                my_val = 0
            try:
                rhs_val = int(rhs_vals[i])
            except Exception as err:
                rhs_val = 0
        
            if my_val < rhs_val:
                return True
            if my_val > rhs_val:
                return False

        return False

    def __eq__(self, rhs):
        my_vals = [re.sub(r'[^0-9]', '', v) for v in self.version.split(".")]
        rhs_vals = [re.sub(r'[^0-9]', '', v) for v in rhs.version.split(".")]
        for i in range(max(len(my_vals), len(rhs_vals))):
            my_val = ('0' if i >= len(my_vals) else my_vals[i])
            rhs_val = ('0' if i >= len(rhs_vals) else rhs_vals[i])
            if my_val != rhs_val:
                return False
        return True

    def __getitem__(self, key):
        my_vals = [re.sub(r'[^0-9]', '', v) for v in self.version.split(".")]
        if type(key) != int:
            raise Exception("Must provide integer value")
        try:
            val = int(my_vals[key])
        except Exception as err:
            val = 0
        return val

    def __repr__(self):
        return self.version

    def __str__(self):
        return self.version

def version_filter(versions, v_prefix=None):
    # Select whether to use 'v' prefix or not, e.g. v1.0.0
    if v_prefix == True:
        versions = [version for version in versions if version[0] == 'v']
    elif v_prefix == False:
        versions = [version for version in versions if version[0]  in "0123456789"]

    # Exclude strange versions with dashes
    #versions = [version for version in versions if len(version.split(".")) == 3 and len(version.split("-")) == 1]
    versions = [Version(version) for version in versions if "-" not in version]
    # Sort versions
    versions = sorted(versions)#, key=lambda v: v.split('.'))
    return versions

def gitlab_repo_versions(owner, repo, v_prefix=None):
    for i in range(3):
        try:
            response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
            result = response.json()
            versions = [obj['name'] for obj in result]
            versions = version_filter(versions, v_prefix)
            return versions
        except Exception as err:
            time.sleep(5)
            continue

def docker_hub_versions(repo, project, v_prefix=None):
    for i in range(3):
        try:
            response = requests.get(f"https://hub.docker.com/v2/repositories/{repo}/{project}/tags?page_size=1000").json()
            versions = [obj['name'] for obj in response['results']]
            versions = version_filter(versions, v_prefix)
            return versions
        except Exception as err:
            time.sleep(5)
            continue

def upgrade_path(starting_version, versions):
    path = []
    # Go to next major version
    for version in versions:
        if version > starting_version and (version[0] != starting_version[0] or version[1] != starting_version[1]) and not any(version[0] == p[0] and version[1] == p[1] for p in path):
            path.append(version)

    # Get the latest minor version
    if (not path or (versions[-1] != path[-1])) and versions[-1] > starting_version:
        path.append(versions[-1])

    return path

if __name__ == "__main__":
    service_names = ["pangolin", "traefik", "badger", "gerbil"]
    service_versions = dict()
    service_versions['pangolin'] = gitlab_repo_versions('fosrl', 'pangolin')
    service_versions['badger'] = gitlab_repo_versions('fosrl', 'badger')
    service_versions['gerbil'] = gitlab_repo_versions('fosrl', 'gerbil')
    service_versions['traefik'] = docker_hub_versions('library', 'traefik', v_prefix=False)
    
    initial_versions = dict()
    upgrade_paths = dict()
    for i in range(len(sys.argv)-1):
        service = service_names[i]
        initial_versions[service_names[i]] = Version(sys.argv[i+1])
        _upgrade_path = [v.version for v in upgrade_path(initial_versions[service], service_versions[service])]
        if _upgrade_path:
            upgrade_paths[service] = _upgrade_path
    
    print(json.dumps(upgrade_paths))
