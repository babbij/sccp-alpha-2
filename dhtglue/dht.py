import os
import logging
import hashlib
import boto3
import pymongo


TABLE_CLAIMS = 'prototype_claims'
TABLE_POINTERS = 'prototype_pointers'


class DynamoBackend:
  def __init__(self):
    self.session = boto3.Session(
      aws_access_key_id = os.environ['DYNAMO_AWS_KEY_ID'],
      aws_secret_access_key = os.environ['DYNAMO_AWS_KEY'],
      region_name = os.environ['DYNAMO_REGION']
    )
    
    self.dynamodb = self.session.resource('dynamodb')

  def put_pointer(self, hash, data):
    logging.debug (f'Put Pointer {hash[0:10]}...{hash[-10:]} -> {data[0:10]}...{data[-10:]}')
  
    # create a primary key
    pkey = hashlib.sha256((hash + data).encode()).hexdigest()
  
    self.dynamodb.Table(TABLE_POINTERS).put_item(
      Item ={ 
        'pkey' : pkey,
        'hash' : hash,
        'data' : data 
      }
    )

  def get_pointers(self, hash):
    logging.debug (f'Get Pointer {hash[0:10]}...{hash[-10:]}')

    results = self.dynamodb.Table(TABLE_POINTERS).query(
      IndexName='hash-index', #hash ?
      KeyConditions={
        'hash': {
          'AttributeValueList': [ hash ],
          'ComparisonOperator': 'EQ'
        }
      }
    )
  
    if results and 'Items' in results:
      return list(map(lambda x: x['data'], results['Items']))
    else:
      return []


  def put_claim(self, id, data):
    logging.debug (f'Put Claim {id[0:10]}...{id[-10:]} -> {data[0:10]}...{data[-10:]}')

    self.dynamodb.Table(TABLE_CLAIMS).put_item(
      Item ={ 
        'id' : id,
        'data' : data 
      }
    )


  def get_claim(self, id):
    logging.debug (f'Get Claim {id[0:10]}...{id[-10:]}')

    result = self.dynamodb.Table(TABLE_CLAIMS).get_item(
      Key={
        'id': id
      }
    )

    if result and ('Item' in result) and ('data' in result['Item']):
      return  result['Item']['data']
    else:
      return None


class MongoBackend: 
  def __init__(self):
    self.client = pymongo.MongoClient(os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT']))
    self.db = self.client.claimdb

  def put_pointer(self, hash, data):
    self.db[TABLE_POINTERS].insert_one({
      'hash': hash,
      'data': data
    })

  def get_pointers(self, hash):
    docs = self.db[TABLE_POINTERS].find({
      'hash': hash
    })
    
    if docs:
      return list(map(lambda doc : doc['data'], docs))
    else:
      return []

  def put_claim(self, id, data):
    self.db[TABLE_CLAIMS].insert_one({
      'id': id, 
      'data': data
    })

  def get_claim(self, id):
    doc = self.db[TABLE_CLAIMS].find_one({ 'id' : id })

    if doc:
      return doc['data']
    else:
      return None


class TestingBackend: 
  def __init__(self):
    self.pointers = {}
    self.claims = {}

  def put_pointer(self, hash, data):
    if hash in self.pointers:
      if data not in self.pointers[hash]:
        self.pointers[hash].append(data)
    else:
      self.pointers[hash] = [data]

  def get_pointers(self, hash):
    if hash in self.pointers:
      return self.pointers[hash]
    else:
      return []

  def put_claim(self, id, data):
    self.claims[id] = data

  def get_claim(self, id):
    try:
      return self.claims[id]
    except KeyError:
      return None



INSTANCE = MongoBackend()


def put_pointer(hash, data):
  logging.debug (f'Put Pointer {hash[0:10]}...{hash[-10:]} -> {data[0:10]}...{data[-10:]}')
  return INSTANCE.put_pointer(hash, data)

def get_pointers(hash):
  logging.debug (f'Get Pointer {hash[0:10]}...{hash[-10:]}')
  results = INSTANCE.get_pointers(hash)
  logging.debug(f'Got {len(results)} pointers')
  return results

def put_claim(id, data):
  logging.debug (f'Put Claim {id[0:10]}...{id[-10:]} -> {data[0:10]}...{data[-10:]}')
  return INSTANCE.put_claim(id, data)


def get_claim(id):
  logging.debug (f'Get Claim {id[0:10]}...{id[-10:]}')
  result = INSTANCE.get_claim(id)
  if result:
    logging.debug('Found claim')
  else:
    logging.error('Did not find claim')
  return result



if __name__ == '__main__':
  put_pointer('abc', 'def')
  put_pointer('abc', 'ghi')

  print (get_pointers('abc'))
  
  put_claim('123', '456')
  
  print (get_claim('123'))
  
