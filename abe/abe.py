import sys, os
import logging
import threading
import random
import string
import base64
import binascii

import pyopenabe


# run as mini-threads because this avoids crashing OpenABE...
def _as_thread(fn):
  result = None
  error = None
  
  def fn_wrapper():
    nonlocal result, error
    
    try:
      result = fn()
    except Exception as e:
      error = e

  t = threading.Thread(target = fn_wrapper)
  t.start()
  t.join()
  
  if error:
    raise error

  return result



def _do_encrypt(abe, cleartext, attributes, encoding = 'US-ASCII'):
  # logging.debug(f'Encrypting with {attributes}')

  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  context.importPublicParams(abe.public_key)
  context.importSecretParams(abe.secret_key)

  ciphertext = context.encrypt(attributes, cleartext.encode(encoding)).decode('US-ASCII')
  # logging.debug(f'Ciphertext {ciphertext[0:20]}...{ciphertext[-20:]}')
  return ciphertext


def _do_share(abe, attributes):
  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  context.importPublicParams(abe.public_key)
  context.importSecretParams(abe.secret_key)

  key_name = ''.join(random.choices(string.ascii_uppercase, k=10))
  context.keygen(attributes, key_name)

  return context.exportUserKey(key_name).decode('US-ASCII')


def _do_decrypt(abe, ciphertext, public_key, secret_key, encoding = 'US-ASCII'):
  openabe = pyopenabe.PyOpenABE()
  context = openabe.CreateABEContext('KP-ABE')

  context.importPublicParams(public_key)

  key_name = ''.join(random.choices(string.ascii_uppercase, k=10))
  context.importUserKey(key_name, secret_key)

  return context.decrypt(key_name, ciphertext).decode(encoding)




class ABE:
  def __init__(self, public_key = os.environ['KPABE_PUBLIC_KEY'], secret_key = os.environ['KPABE_SECRET_KEY']):
    self.public_key = public_key
    self.secret_key = secret_key
    
  def get_mpk_encoded(self):
    return 'A' + binascii.hexlify(base64.b64decode(self.public_key)).decode('US-ASCII')

  def encrypt(self, cleartext, attributes, encoding = 'US-ASCII'):
    def _task():
      return _do_encrypt(self, cleartext, attributes)
    return _as_thread(_task)

  def share(self, attributes):
    def _task():
      return _do_share(self, attributes)
    return (self.public_key, _as_thread(_task))

  def decrypt(self, ciphertext, sharekey, encoding = 'US-ASCII'):
    (public_key, secret_key) = sharekey
    def _task():
      return _do_decrypt(self, ciphertext, public_key, secret_key)
    return _as_thread(_task)


DEFAULT_ABE = ABE() # uses environment variables




if __name__ == '__main__':
  cmd = sys.argv[1]
  
  if cmd == 'encrypt':
    print(_do_encrypt(DEFAULT_ABE, sys.argv[2], sys.argv[3]))
    
  elif cmd == 'share':
    print(_do_share(DEFAULT_ABE, sys.argv[2]))

  elif cmd == 'decrypt':
    print(_do_decrypt(DEFAULT_ABE, sys.argv[2], sys.argv[3], sys.argv[4]))

  else:
    sys.exit(1)
