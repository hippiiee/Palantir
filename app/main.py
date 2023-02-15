from scraper.scrap import GetGithubInfos
from core.clustering import global_clustering
import argparse
import logging
import sys
import os

"""
This script is the main script of the project. It is used to run the scraper and the clustering.
"""
# Path: app/main.py
if __name__ == '__main__':
    """
    Main function
    """

    version_number = '1.0.0'

    banner = f"""\x1b[0;33m
     _____            _                   _     _        
    |  __ \          | |                 | |   (_)       
    | |__) |   __ _  | |   __ _   _ __   | |_   _   _ __ 
    |  ___/   / _` | | |  / _` | | '_ \  | __| | | | '__|
    | |      | (_| | | | | (_| | | | | | | |_  | | | |   
    |_|       \__,_| |_|  \__,_| |_| |_|  \__| |_| |_|   
                                                                                                                  
    \x1b[0;1;3mBy Y0yor\x1b[0;33m | \x1b[0;1mhttps://github.com/Y0yor/Palantir\x1b[0m
    """
    print(banner)
    # Set the logging level
    logging.basicConfig(level=logging.INFO)
    # Parse the arguments
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--repo', type=str, help='Github repo')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version_number)
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--cluster', action='store_true', help='Run the clustering')
    args = parser.parse_args()
    # Run the scraper
    if args.repo:
        logging.info("GetGithubInfos : %s" % args.repo)
        repos = GetGithubInfos(args.repo)
        repos.run()
    else:
        logging.error("No repo provided")    
        logging.warning("Usage: python3 main.py --repo")
    # Run the clustering
    if args.cluster:
        if os.listdir('../download/') != []:
            logging.info("Clustering : %s" % os.listdir('../download/'))
            global_clustering()
        else:
            logging.error("No repo downloaded")
    else:
        logging.warning("Usage: python3 main.py --cluster")
        sys.exit(1)
