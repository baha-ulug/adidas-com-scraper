from scrapy.crawler import CrawlerProcess
from adidasspider import AdidasSpider

def main():    
    #settings = get_project_settings(settings={'LOG_LEVEL': 'ERROR'})
    process = CrawlerProcess(settings={'LOG_LEVEL': 'INFO'})
    process.crawl(AdidasSpider)
    process.start()

    return "Success!"

if __name__=='__main__':
    main()