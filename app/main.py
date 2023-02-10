from scraper.scrap import GetGithubInfos

# Path: app/main.py
if __name__ == '__main__':
    repos = GetGithubInfos('')
    repos.run()