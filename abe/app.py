import os, random, string, re
import pyopenabe

from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"



from flask import Flask, request, abort, jsonify

app = Flask(__name__)


@app.route("/encrypt", methods=['POST'])
def encrypt():  
  try:
    json = request.get_json()
    attributes = check_attributes(json['attributes'])
    text = json['text']
  except (KeyError, AttributeError, ValueError) as ex:
    return abort(400, str(ex))
  
  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  context.importPublicParams(get_public_key())
  context.importSecretParams(get_secret_key())
  
  return jsonify({
    'attributes': attributes,
    'ciphertext': context.encrypt('|'.join(attributes), text.encode("UTF-8"))
  })


@app.route("/decrypt", methods=['POST'])
def decrypt():
  try:
    json = request.get_json()
    ciphertext = json['ciphertext']
  except (KeyError, AttributeError, ValueError) as ex:
    return abort(400, str(ex))
  
  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  key_name = ''.join(random.choices(string.ascii_uppercase, k=10))

  context.importPublicParams(get_public_key())
  context.importUserKey(key_name, get_share_key())

  return jsonify({
    'cleartext': context.decrypt(key_name, ciphertext)
  })


@app.route("/share", methods=['POST'])
def share():
  public_key = get_public_key()
  secret_key = get_secret_key()
  
  try:
    json = request.get_json()
    attributes = check_attributes(json['attributes'])
  except (KeyError, AttributeError, ValueError) as ex:
    return abort(400, str(ex))

  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  context.importPublicParams(public_key)
  context.importSecretParams(secret_key)

  key_name = ''.join(random.choices(string.ascii_uppercase, k=10))
  context.keygen(' AND '.join(attributes), key_name)

  return jsonify({
    'sharekey': {
      'public': public_key,
      'share': context.exportUserKey(key_name).decode('US-ASCII')
    },
  })


class KeyException(Exception):
  def __init__(self, message):
    super().__init__(message)


def get_public_key():
  public_key = request.headers.get('x-abe-public-key', os.environ.get('KPABE_PUBLIC_KEY', None))
  if public_key and len(public_key) > 0:
    return public_key
  else:
    raise KeyException('No public key specified')
  
def get_secret_key():
  secret_key = request.headers.get('x-abe-secret-key', os.environ.get('KPABE_SECRET_KEY', None))
  if secret_key and len(secret_key) > 0:
    return secret_key
  else:
    raise KeyException('No secret key specified')

def get_share_key():
  share_key = request.headers.get('x-abe-share-key', None)
  if share_key and len(share_key) > 0:
    return share_key
  else:
    raise KeyException('No share key specified')



ATTRIBUTE_REGEX = re.compile('[a-zA-Z].*')
def check_attributes(attributes):
  if not isinstance(attributes, list) or len(attributes) == 0:
    raise ValueError('Attributes must be list with len > 0')
    
  if next((x for x in attributes if not ATTRIBUTE_REGEX.match(x)), None) is not None:
    raise ValueError(f'Attributes must match {ATTRIBUTE_REGEX.pattern}')
    
  return attributes
  
  

@app.errorhandler(pyopenabe.PyOpenABEError)
def crypto_exception(e):
  return jsonify({
    'error': str(e)
  }), 400
  
@app.errorhandler(KeyException)
def crypto_exception(e):
  return jsonify({
    'error': str(e)
  }), 400


if __name__ == '__main__':
  ABE_PORT = int(os.environ.get('ABE_PORT', 8088))
  
  app.run(host='0.0.0.0', port=ABE_PORT, debug=True)
