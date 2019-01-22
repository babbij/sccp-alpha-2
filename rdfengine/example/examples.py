import rdflib
# from store.fetched import FetchedStore


g = rdflib.Graph()

g.parse("./rdfengine/example/foaf.rdf")

g.update('''

DELETE { ?person foaf:name ?name }
WHERE { ?person foaf:name 'Tim Berners-Lee' . ?person ?v ?name }
''')

g.update('''
INSERT DATA { <http://www.w3.org/People/Berners-Lee/card#i>  foaf:name  "Bim Lerners-Tee" }
''')

qres = g.query(
    """SELECT DISTINCT ?name
       WHERE {
          ?a foaf:knows ?b .
          ?a foaf:name 'Bim Lerners-Tee' .
          ?b foaf:name ?name .
       }""")


print(qres.serialize(format='xml'))

