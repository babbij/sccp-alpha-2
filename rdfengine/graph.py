import os, logging
import rdflib

from store.fast import FastStore

LOCAL_ONLY = int(os.environ.get('LOCAL_ONLY', '0'))

print('LOCAL_ONLY', LOCAL_ONLY)

localgraph = rdflib.Graph(FastStore())
localstore = localgraph.store

print(localstore)

if LOCAL_ONLY == 1:
  logging.critical('DHT store disabled')
  
  dhtstore = None
  dhtgraph = None
else:
  from store.listening import ListeningStore
  
  dhtstore = ListeningStore()
  dhtgraph = rdflib.Graph(dhtstore)
