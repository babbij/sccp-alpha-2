# this is a script to run to upload ttl/rdf+xml files to the rdf engine

import logging
import os, sys, json
import ctypes
import chardet

import requests


def get_content_type(path):
  if path.endswith('.rdf'):
    return 'application/rdf+xml'
    
  if path.endswith('.xml'):
    return 'application/rdf+xml'
    
  if path.endswith('.ttl'):
    return 'text/turtle'
    
  if path.endswith('.json'):
    return 'application/rdf+json'
    
  return None


def upload_file(endpoint, path):
  logging.debug(f'Loading file {path}')
  content_type = get_content_type(path)
  if content_type:  
    with open(path, 'r') as fp:
      data = fp.read()
      r = requests.post(endpoint, headers={'content-type': f'{content_type}; charset=utf-8'}, data = data)
      if r.status_code == 200:
        logging.debug(f'Success!')
        logging.debug(json.dumps(r.json(), indent = 2))
      else:
        logging.error(f'ERROR: endpoint returned {r.status_code}')
  else:
    logging.error(f'ERROR: Could not identify file type')
  
  logging.debug('----------------------------------------')


def is_hidden(path):
  try:
    attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(path))
    return bool(attrs & 2)
  except (AttributeError, AssertionError):
    return False


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(message)s')
  
  endpoint = sys.argv[1]

  logging.debug('----------------------------------------')
  logging.debug(f'Uploading to {endpoint} ...')
  logging.debug('----------------------------------------')
  
  for path in sys.argv[2:]:
    if os.path.isfile(path):
      upload_file(endpoint, path)
    elif os.path.isdir(path):
      logging.debug(f'Loading files from {path}')
      for name in os.listdir(path):
        filepath = os.path.join(path, name)
        if os.path.isfile(filepath) and not (name.startswith('.') or is_hidden(filepath)):
          upload_file(endpoint, filepath)
