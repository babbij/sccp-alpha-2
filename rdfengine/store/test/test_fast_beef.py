import logging
import cProfile
import rdflib


from store.fast import FastStore



def run_query(graph):
  stmt = '''PREFIX com: <https://schemas.goodforgoodbusiness.com/common-operating-model/lite/>
    SELECT ?buyerRef ?quantity ?unitPrice ?shipmentRef ?ain ?vaccine WHERE {
      ?order com:buyer <urn:uuid:448c5299-b858-4eb1-bc55-0a7a6c04efee>;
        com:buyerRef ?buyerRef;
        com:quantity ?quantity;
        com:unitPrice ?unitPrice;
        com:fulfilledBy ?shipment.
      ?shipment com:consignee <urn:uuid:448c5299-b858-4eb1-bc55-0a7a6c04efee>;
        com:shipmentRef ?shipmentRef.
      OPTIONAL {
        ?shipment com:usesItem ?cow.
        OPTIONAL {
          ?cow com:ain ?ain.
          OPTIONAL {
            ?cow com:vaccination ?vaccination.
            ?vaccination com:vaccine ?vaccine.
          }
        }
      }
    }'''

  result = graph.query(stmt)
  
  found = 0
  for row in result:
    found += 1

  print('Found=', found)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')
  
  graph = rdflib.Graph(FastStore())

  preload_path = '/Users/ijmad/Desktop/sccp/tb_example/generated_claims'
  logging.debug(f'Preload path = {preload_path}')
  from preload import run_preload
  run_preload([preload_path], graph)

  cProfile.run('run_query(graph)', 'beef.stats')