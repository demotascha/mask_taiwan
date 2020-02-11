import os
import re
import requests
from algoliasearch.search_client import SearchClient

ALGOLIA_APP_ID = os.environ.get('ALGOLIA_APP_ID')
ALGOLIA_APP_KEY = os.environ.get('ALGOLIA_APP_KEY')
ALGOLIA_APP_INDEX = os.environ.get('ALGOLIA_APP_INDEX')

DATA_RESOURCE_URL = os.environ.get('DATA_RESOURCE_URL')

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_APP_KEY)
index = client.init_index(ALGOLIA_APP_INDEX)

def main(request):
  # 取得特約店家資料
  results = requests.get(DATA_RESOURCE_URL).json()

  infos=[]

  for point in results['features']:
    info={}
    info['objectID'] = point['properties']['id']
    info['name'] = point['properties']['name']
    info['phone'] = transform_tel_style(point['properties']['phone']) 
    info['address'] = transform_tel_style(point['properties']['address'])
    info['_geoloc'] = {
      'lat': float(point['geometry']['coordinates'][1]),
      'lng': float(point['geometry']['coordinates'][0])
    }
    # info['available'] = point['properties']['available']
    # info['note'] = point['properties']['note']

    infos.append(info)
  # print(infos)
  index.save_objects(infos)
  exit(0)

    # 重置電話格式
def transform_tel_style(line):
  rule = re.compile(u"02 -")
  line = rule.sub('+8862',line)
  rule = re.compile(u"03 -")
  line = rule.sub('+8863',line)
  rule = re.compile(u"037-")
  line = rule.sub('+88637-',line)
  rule = re.compile(u"038-")
  line = rule.sub('+88638-',line)
  rule = re.compile(u"04 -")
  line = rule.sub('+8864',line)
  rule = re.compile(u"049-")
  line = rule.sub('+88649',line)
  rule = re.compile(u"05 -")
  line = rule.sub('+8865',line)
  rule = re.compile(u"06 -")
  line = rule.sub('+8866',line)
  rule = re.compile(u"07 -")
  line = rule.sub('+8867',line)
  rule = re.compile(u"08 -")
  line = rule.sub('+8868',line)
  rule = re.compile(u"082-")
  line = rule.sub('+88682',line)
  rule = re.compile(u"82 -")
  line = rule.sub('+88682',line)
  rule = re.compile(u"083-")
  line = rule.sub('+88683',line)
  rule = re.compile(u"089-")
  line = rule.sub('+88689',line)
  rule = re.compile(u"-")
  line = rule.sub('',line)
  return line
