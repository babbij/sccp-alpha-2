#/usr/bin/env python3

import logging, time
import json, cbor2, binascii, hashlib, os

from pyblake2 import blake2b

from signing import create_signing_pair, signing_pair_from_string
from symmetric import SymmetricCipher
from identity import sign_with_identity
from patterns import make_patterns, make_pattern
from shared.repr import triple_to_repr, repr_to_triple

from abe.abe import DEFAULT_ABE



class Pointer:
  @classmethod
  def from_hex(cls, string):
    obj = cbor2.loads(binascii.unhexlify(string))
    return Pointer(obj[0], SymmetricCipher(obj[1]), obj[2])
  
  def __init__(self, id, key, nonce = binascii.hexlify(os.urandom(16))):
    self.id = id
    self.key = key
    self.nonce = nonce

  def to_hex(self, nonce = None):
    return binascii.hexlify(
      cbor2.dumps(
        [ self.id, self.key ] + ([nonce] if nonce else [])
      )
    ).decode('ASCII')


class EncryptedPointer(Pointer):
  def __init__(self, patterns, id, key, abe_instance):
    super(EncryptedPointer, self).__init__(id, key)
    self.patterns = patterns
    self.attributes = '|'.join(patterns)
    self.abe_instance = abe_instance

  def to_encrypted(self, nonce = None):
    if not nonce:
      nonce = binascii.hexlify(os.urandom(16))
    return self.abe_instance.encrypt(self.to_hex(nonce = nonce), self.attributes)


class InnerEnvelope:
  def __init__(self, triples_added, triples_removed, antecedents, linkv_alg, linkv_sk, linkv_vk):
    self.triples_added = triples_added
    self.triples_removed = triples_removed
    self.antecedents = antecedents
    
    self.linkv_alg = linkv_alg
    self.linkv_sk = linkv_sk
    self.linkv_vk = linkv_vk
    
    self.time = int(time.time())
    
    self._hash = blake2b(cbor2.dumps(self.get_contents())).hexdigest()

  def get_id(self):
    return self._hash

  def get_contents(self, contents_key = None):
    obj = {
      'type':         'claim',
      'added':        list(map(triple_to_repr, self.triples_added)),
      'removed':      list(map(triple_to_repr, self.triples_removed)),
      'antecedents':  self.antecedents,
      'link_secret':  { 
        'key':        binascii.hexlify(self.linkv_sk.to_string()).decode('ASCII'),
        'alg':        self.linkv_alg
      }
    }
    
    if contents_key:
      hex = binascii.hexlify(cbor2.dumps(obj)).decode('ASCII')
      return contents_key.encrypt(hex).decode('ASCII')
    else:
      return obj

  def to_json(self, contents_key = None):
    lv = {
     'key': binascii.hexlify(self.linkv_vk.to_string()).decode('ASCII'),
     'alg': self.linkv_alg
    }
    
    # When stored in the Weft, this is a base64 encoded encrypted blob, with a multikey wrapper
    return {
      'contents': self.get_contents(contents_key),
      'hashkey': self._hash,
      'link_verifier': lv,
      'signature': sign_with_identity(
        cbor2.dumps([
          self.get_contents(), self._hash, lv
        ])
      )
    }

  def get_patterns(self, combinations = True, add_mpk = True, add_time = True):
    patterns = set()
    
    for triple in self.triples_added:
      (sub, pre, obj) = triple
      if combinations:
        patterns |= make_patterns(sub, pre, obj)
      else:
        patterns.add(make_pattern(sub, pre, obj))
  
    for triple in self.triples_removed:
      (sub, pre, obj) = triple
      if combinations:
        patterns |= make_patterns(sub, pre, obj)
      else:
        patterns.add(make_pattern(sub, pre, obj))

    # if add_mpk:
    #   patterns.add(abe.get_mpk_encoded())

    if add_time:
      patterns.add(f'time = {self.time}') # also add the claim's timestamp
    
    return patterns


class Claim:
  @classmethod
  def from_hex(cls, hex, key):
    obj = json.loads(cbor2.loads(binascii.unhexlify(hex)))
    contents = cbor2.loads(binascii.unhexlify(key.decrypt(obj['inner_envelope']['contents']).decode('ASCII')))
    
    logging.debug(f'Raw claim content= {contents}')
    
    (linkv_alg, linkv_sk, linkv_vk) = signing_pair_from_string(
      contents['link_secret']['key'], 
      contents['link_secret']['alg']
    )
      
    triples_added = list(map(repr_to_triple, contents['added']))
    triples_removed = list(map(repr_to_triple, contents['removed']))
    antecedents = contents['antecedents']
    links = obj['links']
    
    return Claim(
      InnerEnvelope(
        triples_added,
        triples_removed,
        antecedents,
        linkv_alg,
        linkv_sk,
        linkv_vk
      ),
      links,
      key
    )

  @classmethod
  def create(cls, triples_added = [], triples_removed = [], links = []):
    contents_key = SymmetricCipher()
    (linkv_alg, linkv_sk, linkv_vk) = create_signing_pair()
    
    # generate antecedents from links
    antecedents = list(map(lambda link: sign_link(linkv_sk, link), links))
    
    inner_envelope = InnerEnvelope(
      triples_added,
      triples_removed,
      antecedents,
      linkv_alg,
      linkv_sk,
      linkv_vk
    )
    
    # add proof to links 
    for link in links:
      link['proof'] = link_proof(linkv_sk, inner_envelope, link)
    
    return Claim(
      inner_envelope,
      links, 
      contents_key
    )
  
  def __init__(self, inner_envelope, links, contents_key):
    self.inner_envelope = inner_envelope
    self.links = links
    self.contents_key = contents_key

  def get_id(self):
    return self.inner_envelope.get_id()

  def get_predecessors(self):
    return list(map(lambda link: link['ref'], self.links))

  def to_json(self, encrypted = False):
    contents_key = self.contents_key if encrypted else None
    
    outer_envelope = {
      'inner_envelope': self.inner_envelope.to_json(contents_key = contents_key),
      'links': self.links,
      'signature': sign_with_identity(
        cbor2.dumps([self.inner_envelope.to_json(), self.links])
      )
    }

    return json.dumps(outer_envelope, indent=1)
  
  def to_hex(self, encrypted = False):
    return binascii.hexlify(cbor2.dumps(self.to_json(encrypted))).decode('ASCII')
  
  def get_patterns(self, combinations = True, add_mpk = True, add_time = True):
    return self.inner_envelope.get_patterns(combinations, add_mpk, add_time)
  
  def get_pointer_map(self, abe_instance = DEFAULT_ABE):
    patterns = self.inner_envelope.get_patterns()

    logging.debug(f'Pointer map for patterns= {patterns}')

    return dict(
      (pattern, EncryptedPointer(patterns, self.get_id(), self.contents_key.get_key(), abe_instance)) 
      for pattern in patterns
    )


def create_claim(triples_added, triples_removed, links):
  logging.debug(f'triples_added = {triples_added}')
  logging.debug(f'triples_removed = {triples_removed}')
  
  claim = Claim.create(
    list(map(repr_to_triple, triples_added)),
    list(map(repr_to_triple, triples_removed)),
    links
  )
  
  logging.debug(f'Claim Object Created = {claim.to_json(False)}')
  return claim


def sign_link(linkv_sk, link):
  logging.debug(f'sign_link: {link}')
  
  canon = cbor2.dumps(link)
  link_hash = hashlib.sha256(canon).hexdigest()
  
  return binascii.hexlify(
      linkv_sk.sign( 
        link_hash.encode('ASCII')
      )
    ).decode('ASCII')
    

def link_proof(linkv_sk, inner_envelope, link):
  logging.debug(f'link_proof: {link}')
  
  canon = cbor2.dumps([
    inner_envelope.get_id(), link['rel'], link['ref']
  ])
  
  link_proof_hash = hashlib.sha256(canon).hexdigest()
  
  return binascii.hexlify(
      linkv_sk.sign( 
        link_proof_hash.encode('ASCII')
      )
    ).decode('ASCII')
  


if __name__ == '__main__':
  (linkv_alg, linkv_sk, linkv_vk) = create_signing_pair()
  
  link = {
    'ref': '315d0c7f84f3f1f2b946b22b3eed2dacdff168e0cff0c207dfabb6119994a7628bc0d1a753b7d6f731cb19cfb777e2d609463e6404484d58fab52912ff1e545a',
    'rel': 'https://schemas.goodforgoodbusiness.org/weft/1.0#causedBy'
  }
  
  print(sign_link(linkv_sk, link))
  print(sign_link(linkv_sk, link))
