import rdflib, json, logging

def from_n3(term):
  if term is None:
    return None
  else:
    term = term.strip()
    if len(term) == 0:
      return None

    if term[0] == '"' and term[-1] == '"':
      return rdflib.term.Literal( term[1:-1] )
    elif term[0] == '"' and '"^^' in term:
      (val, typ) = term.split('^^')
      if val[0] == '"' and val[-1] == '"' and typ[0] == '<' and typ[-1] == '>':
        return rdflib.term.Literal(val[1:-1], datatype = typ[1:-1])
    elif term[0] == '<' and term[-1] == '>':
       return rdflib.term.URIRef( term[1:-1] )
    # elif term[0:2] == '_:':
    #   # it probably doesn't make sense to deserialize BNodes like this here
    #   # the references are only internal links and are not consisent.
    #   return rdflib.term.BNode(term[2:])

  raise ValueError(f'{term}')


def repr_to_value(rterm):
  if rterm:    
    if 'literal' in rterm:
      return rterm['literal']['value']

    if 'uri' in rterm:
      return rterm['uri']
    
  raise ValueError(rterm)


def term_to_repr(term):
  if term:
    if type(term) is rdflib.term.URIRef:
      return {
        'uri': term
      }

    if type(term) is rdflib.term.Literal:
      result = {
        'literal': {
          'value': term,
        }
      }
    
      if term.datatype:
        result['literal']['type'] = term_to_repr(term.datatype)

      if term.language:
        result['literal']['lang'] = term.language
    
      return result

  raise ValueError(f'{term} is {type(term)}')


def triple_to_repr(triple):
  (sub, pre, obj) = triple
  result = {}
  
  if sub:
    result['s'] = term_to_repr(sub)
    
  if pre:
    result['p'] = term_to_repr(pre)
  
  if obj:
    result['o'] = term_to_repr(obj)

  return result


def repr_to_term(term):
  if term:
    if 'literal' in term:
      return rdflib.term.Literal(
        term['literal']['value'],
        datatype = (repr_to_term(term['literal']['type']) if 'type' in term['literal'] else None),
        lang = (term['literal']['lang'] if 'lang' in term['literal'] else None)
      )
  
    if 'uri' in term:
      return rdflib.term.URIRef(term['uri'])
    
  raise ValueError(term)


def repr_to_triple(json):
  sub = repr_to_term(json['s']) if ('s' in json) else None
  pre = repr_to_term(json['p']) if ('p' in json) else None
  obj = repr_to_term(json['o']) if ('o' in json) else None
  
  return (sub, pre, obj)
  
  
def link_repr(ref_id, rel):
  return {
    'ref': ref_id,
    'rel': rel
  }


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

  triple = (
    from_n3('"foo"'),
    from_n3('<http://schema.org/people#age>'),
    from_n3('"35"^^<http://www.w3.org/2001/XMLSchema#integer>')
  )
  
  print (triple)
  
  result = json.dumps(
      triple_to_repr(triple), indent = 2
    )
    
  print (result)
  
  print( repr_to_triple(json.loads(result)) )
  


