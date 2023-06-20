import crochet
crochet.setup()     # initialize crochet

import json
from datetime import datetime
from flask import Flask
from scrapy.crawler import CrawlerRunner
from adidasspider import AdidasSpider
import boto3



app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner() 

@app.route('/scrape')
def crawl_for_quotes():
    
    scrape_with_crochet()
    return 'SCRAPING'

@crochet.run_in_reactor
def scrape_with_crochet():
    start_time= datetime.now()
    print(f"Script started at {start_time}")
    eventual = crawl_runner.crawl(AdidasSpider)
    eventual.addCallback(finished_scrape)

def finished_scrape(null):
    end_time= datetime.now()
    AdidasSpider().send_email()
    print(f"Script finished at {end_time}")

if __name__=='__main__':
    app.run('0.0.0.0', 8080, debug=True, error= True)
