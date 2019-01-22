import os
import requests
import json

from shared.repr import triple_to_repr, link_repr


DHT_ENDPOINT = os.environ['DHT_ENDPOINT']


class Claim:
  def __init__(self, triples_added, triples_removed, links):
    self.triples_added = triples_added
    self.triples_removed = triples_removed
    self.links = links
  
  def to_json(self):
    return json.dumps({
      'added' : list(map(triple_to_repr, self.triples_added)),
      'removed': list(map(triple_to_repr, self.triples_removed)),
      'links': [link_repr(ref, rel) for ref, rel in self.links.items()]
    })
    
  def submit(self):
    # submit claim upstream to DHT
    response = requests.post(
      url = os.environ['DHT_ENDPOINT'] + '/claims',
      headers = {'Content-Type': 'application/json'},
      data = self.to_json(),
    )

    if (response.status_code != 200):
      raise RuntimeError(f'DHT returned {response.status_code}')

    return ClaimSubmission(
      self,
      json.loads(response.text)['id']
    )


class ClaimSubmission:
  def __init__(self, claim, claim_id):
    self.claim_id = claim_id
    self.claim = claim

  def record(self, store):
    for triple in self.claim.triples_added:
      store.add(triple, self.claim_id)
    
    for triple in self.claim.triples_removed:
      store.remove(triple, self.claim_id)


