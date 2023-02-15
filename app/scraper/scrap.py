import requests
import json
from models.items import GithubUser, Repository
from configparser import ConfigParser
import logging

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='\033[32m[%(levelname)s]: %(message)s\033[0m',
    handlers=[logging.StreamHandler()]
)
# Custom logging level
logging.addLevelName(logging.ERROR, "\033[31m%s\033[0m" % logging.getLevelName(logging.ERROR))

class GetGithubInfos:
    default_github_url = "https://github.com"
    headers = ""
    owner = None
    tusers = None
    repo_name = None
    repo_url = ""
    
    def __init__(self, repo_url):
        self.repo_url = repo_url
        # Read the API key from the config file
        config = ConfigParser()
        try:
            config.read('config/.keys.cfg')
            API_KEY = config.get('github', 'token')
            USER_AGENT = config.get('github', 'user-agent')
        except:
            logging.error("No API key found")
            exit(1)
        # Generate the headers for the requests
        self.headers = {"Authorization": "Token %s"% (API_KEY), "Accept": "application/vnd.github.v3+json", "User-Agent": "%s" % (USER_AGENT)}        
    
    def run(self):
        # Get the repo infos
        self.get_repo_infos()
    
    def get_repo_infos(self): 
        owner = GithubUser(url=self.repo_url.rsplit('/', 1)[0], name=self.repo_url.split('/')[-2])    
        repo = Repository(url = self.repo_url, author = self.repo_url.split('/')[-2], name= self.repo_url.split('/')[-1])
        page = 1
        stargazers = []
        while True:
            url = 'https://api.github.com/repos/%s/%s/stargazers?page=%s'% (owner.name, repo.name, page)
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200:
                # If the response is empty, we have reached the end of the pages
                if r.json() == []:
                    # Add the stargazers to the repo object
                    repo.stargazers = stargazers
                    # Serialize the object to a JSON string
                    data = repo.dict()
                    # Write the JSON string to a file
                    with open('../download/%s_%s.json'% (owner.name, repo.name), 'w') as f:
                        json.dump(data, f, indent=4)
                    return False
                for user in r.json():
                    stargazers.append(self.get_stargazer_info(user))
            else:
                logging.error("Error while getting stargazers")
            page += 1
        
        
    def get_stargazer_info(self, user):
        followers = self.get_followers(user)
        following = self.get_following(user)
        starred = self.get_starred(user)
        tmpUser = GithubUser(url = user["html_url"], name = user["login"], followers=followers, following=following, starred = starred)
        return tmpUser
    
    def get_followers(self, user):
        url = 'https://api.github.com/users/%s/followers' % user["login"]
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            followers = []
            for follower in r.json():
                followers.append(follower["login"])
            return followers
        else:
            logging.error("Error while getting followers")
            return None
    
    def get_following(self, user):
        url = 'https://api.github.com/users/%s/following' % user["login"]
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            followings = []
            for following in r.json():
                followings.append(following["login"])
            return followings
        else:
            logging.error("Error while getting following")
            return None
    
    def get_starred(self, user):
        url = 'https://api.github.com/users/%s/starred' % user["login"]
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            repos = []
            for repo in r.json():
                repos.append(repo["name"])
            return repos
        else:
            logging.error("Error while getting starred repos")
            return None


