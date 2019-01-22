import xml.dom.minidom
import json

from collections import OrderedDict



def pretty_xml(input):
  return xml.dom.minidom.parseString(input).toprettyxml()

def pretty_json(input):
  return input



RESULT_FORMATS = OrderedDict()

RESULT_FORMATS['application/sparql-results+xml']  = ('xml',  lambda o : pretty_xml(o)  )
RESULT_FORMATS['application/sparql-results+json'] = ('json', lambda o : pretty_json(o) )
RESULT_FORMATS['application/rdf+xml']             = ('xml',  lambda o : pretty_xml(o)  )
RESULT_FORMATS['application/xml']                 = ('xml',  lambda o : pretty_xml(o)  )
RESULT_FORMATS['application/json']                = ('json', lambda o : pretty_json(o) )
RESULT_FORMATS['text/csv']                        = ('csv',  lambda o : o)
RESULT_FORMATS['text/plain']                      = ('txt',  lambda o : o)




UPLOAD_TYPES = OrderedDict()

UPLOAD_TYPES['application/rdf+xml']               = 'xml'
UPLOAD_TYPES['application/xml']                   = 'xml'
UPLOAD_TYPES['application/rdf+json']              = 'json-ld'
UPLOAD_TYPES['application/json']                  = 'json-ld'
UPLOAD_TYPES['text/turtle']                       = 'turtle'
UPLOAD_TYPES['text/n3']                           = 'n3'
UPLOAD_TYPES['text/plain']                        = 'nt'




def get_upload_type(content_type, data):
  if content_type:
    parts = list(map(lambda s : s.strip().lower(), content_type.split(';')))

    if parts[0] in UPLOAD_TYPES:
      charset = 'UTF-8' # if we can't find the encoding, this is our guess
      for part in parts[1:]:
        if part.startswith('charset'):
          charset = part.split('=')[1].strip()

      return UPLOAD_TYPES[parts[0]], data.decode(charset)
  
  raise ValueError('Did not understand content-type')


def get_result_format(accept):
  if accept:
    for mimetype, zz in RESULT_FORMATS.items():
      if mimetype in accept:
        (format, fn) = zz
        return (mimetype, format, fn)
  
  raise ValueError('Specify a valid Accept header')
  
  
if __name__ == '__main__':
  result = get_upload_type('application/rdf+xml; charset=utf-8', 'foo'.encode('UTF-8'))
  print(result)
