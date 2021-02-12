# Component to manage data push to Elasticsearch
from datetime import datetime

from elasticsearch import Elasticsearch


class ES_Manager():
    def __init__(self):
        self.es = Elasticsearch([localhost:9200],timeout=30)

    def insert_into_es(self, data, index):
        res = self.es.index(index=index, body=data)
        return res

    def insert_into_es_id(self, data, index,id=id):
        res = self.es.index(index=index, body=data,id=id)
        return res



    def search_es(self, index,query={"query": {"match_all": {}}}):
        res = self.es.search(index=index, body=query,size=100)
        #print (res)
        #for hit in res['hits']['hits']:
        #    print(hit["_source"]
        return res

    def search_es_id(self, index, id):
        res = self.es.get(index=index,id=id)
        #print (res)
        #for hit in res['hits']['hits']:
        #    print(hit["_source"]
        return res["_source"]

    def scroll_search_es(self,index,query,scroll="2m"):
        res = self.es.search(index=index, body=query,scroll=scroll,size=1000)
        # for hit in res['hits']['hits']:
        #    print(hit["_source"]
        return res

    def contine_scroll_es(self,scrollid,scroll="1m"):
        res = self.es.scroll(scroll_id=scrollid,scroll=scroll)
        return res

if __name__ == '__main__':
    es_obj = ES_Manager()
    json_data = {}
    json_data["requestId"]  = 101
    time_val = datetime.now().strftime("%Y-%M-%dT%H:%M:%SZ")
    print (time_val)
    json_data["timestamp"] = time_val
    print (json_data)
    es_obj.insert_into_es(1,json_data,"test3")
