import datetime
import binascii, cbor2, logging

import patterns

from abe.abe import ABE, DEFAULT_ABE
from shared.repr import from_n3


def convert_datetime_local(input):
  logging.debug(f'Date in = {input}')
  
  # is it an int?
  try:
    epoch = int(input)
  except ValueError:  
    epoch = int(
      datetime.datetime(
        *[int(v) for v in input.replace('T', '-').replace(':', '-').split('-')]
      ).timestamp()
    )
  
  logging.debug(f'Epoch out = {epoch}')
  
  return epoch


def make_share_key(sub, pre, obj, add_mpk = False, start_time = None, end_time = None, abe_instance = DEFAULT_ABE):
  logging.debug(f'Making share key for {sub} {pre} {obj}')
  
  pointer_pattern = \
    patterns.hash_values(sub, pre, obj) # + f' AND {abe.get_mpk_encoded()}'

  if start_time:
    pointer_pattern += f' AND time >= {int(start_time)}'
    
  if end_time:
    pointer_pattern += f' AND time < {int(end_time)}'

  logging.debug(f'attribute pattern = ' + pointer_pattern)
  
  return encode_key((sub, pre, obj), abe_instance.share(pointer_pattern), start_time = start_time, end_time = end_time)


def encode_key(triple, share_key, start_time = None, end_time = None):
  (sub, pre, obj) = triple
  (public_key, secret_key) = share_key
  
  obj = {
    'pattern': {
      'sub': sub,
      'pre': pre,
      'obj': obj,
    },
    'range': {
      'start': start_time,
      'end': end_time,
    },
    'public': public_key,
    'secret': secret_key,
  }
  
  return \
    binascii.hexlify(
      cbor2.dumps(obj)
    ).decode('US-ASCII')
  

def decode_key(data):
  obj = cbor2.loads(
    binascii.unhexlify(
      data.encode('US-ASCII')
    )
  )
  
  triple = (
    obj['pattern']['sub'],
    obj['pattern']['pre'],
    obj['pattern']['obj']
  )
  
  pattern = patterns.hash_values(*triple)

  return (
    triple, pattern, (obj['public'], obj['secret']) # XXX return key start/end?
  )

