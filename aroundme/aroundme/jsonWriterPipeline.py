import json

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('D:\\workspace\\eka.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item