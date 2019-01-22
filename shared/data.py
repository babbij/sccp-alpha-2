def get_file_format(path):
  if path.endswith('.rdf'):
    return 'xml'
    
  if path.endswith('.xml'):
    return 'xml'
    
  if path.endswith('.ttl'):
    return 'turtle'
    
  if path.endswith('.json'):
    return 'json-ld'
    
  return None