import os, logging, threading, json

import rdflib
from rdflib.events import Dispatcher, Event
from rdflib.store import StoreCreatedEvent, TripleAddedEvent, TripleRemovedEvent

from shared.repr import repr_to_triple, triple_to_repr
from dht import fetch_matches
from claim import Claim

from .base import BaseStore

__all__ = ['ListeningStore']


class ListenContext:
  def __init__(self):
    self.triples_added = set()
    self.triples_removed = set()
    self.links = {}
    self.capture = True
  
  def add(self, triple):
    if self.capture:
      logging.debug(f'Captured addition of {triple}')
      self.triples_added.add(triple)
    
  def remove(self, triple):
    if self.capture:
      logging.debug(f'Captured removal of {triple}')
      self.triples_removed.add(triple)
  
  def linked(self, id, rel):
    self.links[id] = rel
      
  def get_claim(self):
    if len(self.triples_added) > 0 or len(self.triples_removed) > 0:
      return Claim(self.triples_added, self.triples_removed, self.links)
    else:
      return None
  


class ListeningStore(BaseStore):
  def __init__(self, configuration = None, identifier = None):
    super(ListeningStore, self).__init__()
    
    def store_created(event): pass
    self.dispatcher.subscribe(StoreCreatedEvent, store_created)

    def triple_added(event): self.context.add(event.triple)
    self.dispatcher.subscribe(TripleAddedEvent, triple_added)
    
    def triple_removed(event): self.context.remove(event.triple)
    self.dispatcher.subscribe(TripleRemovedEvent, triple_removed)
    
    self.new_context() # create a context 

  def new_context(self):
    # any chance this needs to be thread-local?
    self.context = ListenContext()
    return self.context

  def triples(self, triplein, context = None):
    logging.debug(f'triples triplein: {triplein}')

    self.context.capture = False # avoid capturing any fetched triples and thinking they're part of new claim
    for claim in fetch_matches(triplein, self, context):
      logging.debug(f'Fetched claim= {claim}')
      self.context.linked(claim.get_id(), 'https://schemas.goodforgoodbusiness.org/weft/1.0#causedBy')
   
      for triple in claim.get_removed():
        logging.debug(f'Removing {triple}')
        super(ListeningStore, self).remove(triple, context)
   
      for triple in claim.get_added():
        logging.debug(f'Adding {triple}')
        super(ListeningStore, self).add(triple, context)

    self.context.capture = True
    triples = super(ListeningStore, self).triples(triplein, context)
    return triples

  