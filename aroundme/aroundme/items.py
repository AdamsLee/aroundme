# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class AroundmeItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class EkaStoreListItem(Item):
    externalId = Field()
    name = Field()
    main_business = Field() 
    address = Field()
    contact_phone = Field()
    opening_hours = Field()
    consumer_rules = Field()
    special_cooperation = Field()
    join_date = Field() 
    popularity = Field()
    fromUrl = Field()
