# similar to uploader, this brings in files from a specified directory

import logging
import os, sys, json

from shared.data import get_file_format
from shared.file import is_hidden


def preload_file(path, graph):
  logging.debug(f'Preloading file {path}')
  file_format = get_file_format(path)
  if file_format:
    with open(path, 'r') as fp:
      data = fp.read()
      len_store_before = len(graph)
      graph.parse(data=data, format=file_format)
      
      logging.debug(f'Loaded {len(graph) - len_store_before} statements')
  else:
    logging.error(f'ERROR: Could not identify file format')


def run_preload(paths, graph):
  for path in paths:
    if os.path.isfile(path):
      preload_file(path, graph)
    elif os.path.isdir(path):
      logging.debug(f'Preloading files from {path}')
      for name in os.listdir(path):
        filepath = os.path.join(path, name)
        if os.path.isfile(filepath) and not is_hidden(filepath):
          preload_file(filepath, graph)

