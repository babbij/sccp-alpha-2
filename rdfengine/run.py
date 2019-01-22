#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

import os, sys
from graph import localgraph, localstore


if __name__ == '__main__':  
  port = int(os.environ.get('RDF_PORT', 8080))
  preload_path = os.environ.get('PRELOAD_PATH', None)

  if preload_path:
    logging.debug(f'Preload path = {preload_path}')
    from preload import run_preload
    run_preload([preload_path], localgraph)

  from app import app  
  app.run(host='0.0.0.0', port=port, debug=True)
