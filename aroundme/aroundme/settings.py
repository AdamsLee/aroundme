# Scrapy settings for aroundme project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'aroundme'

SPIDER_MODULES = ['aroundme.spiders']
NEWSPIDER_MODULE = 'aroundme.spiders'

ITEM_PIPELINES = {
    #'aroundme.jsonWriterPipeline.JsonWriterPipeline': 800,
    'scrapy_mongodb.MongoDBPipeline',
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'aroundme (+http://www.yourdomain.com)'

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

MONGODB_REPLICA_SET = 'myDevReplSet'
MONGODB_REPLICA_HOSTS = '127.0.0.1'
MONGODB_DATABASE = 'aroundme'
MONGODB_COLLECTION = 'eka'
MONGODB_UNIQUE_KEY = 'externalId'