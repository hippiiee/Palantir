from scraper.scrap import GetGithubInfos

# Path: app/main.py
if __name__ == '__main__':
    repos = GetGithubInfos('https://github.com/hippiiee/osgint')
    repos.run()