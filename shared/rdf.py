import uuid
import rdflib

def to_skolem_uri(bnode, mapping):
  generated_value = str(bnode)
  if generated_value in mapping:
    return mapping[generated_value]
  else:
    skolem_uri = rdflib.term.URIRef('urn:uuid:' + uuid.uuid4().hex)
    mapping[generated_value] = skolem_uri
    return skolem_uri 


def skolemize(triples, mapping = {}):
  results = []
  
  for triple in triples:
    (sub, pre, obj) = triple
    
    if type(sub) is rdflib.term.BNode:
      sub = to_skolem_uri(sub, mapping)

    if type(pre) is rdflib.term.BNode:
      pre = to_skolem_uri(pre, mapping)
      
    if type(obj) is rdflib.term.BNode:
      obj = to_skolem_uri(obj, mapping)
    
    results.append((sub, pre, obj))

  return results