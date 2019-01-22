#!/usr/bin/env python

import base64, hashlib, os, binascii

from Crypto import Random
from Crypto.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-s[-1]]


class SymmetricCipher:
  # presenting 'None' yields random key
  def __init__( self, key = None):
    if key is None:
      key = os.urandom(32)
    else:
      key = binascii.unhexlify(key)
    
    self.key = key

  def get_key(self):
    return binascii.hexlify(self.key)

  def encrypt( self, raw ):
    raw = pad(raw)
    iv = Random.new().read( AES.block_size )
    cipher = AES.new( self.key, AES.MODE_CBC, iv )
    return base64.b64encode( iv + cipher.encrypt( raw ) )

  def decrypt( self, enc ):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(self.key, AES.MODE_CBC, iv )
    return unpad(cipher.decrypt( enc[16:] ))


if __name__ == '__main__':
  cipher = SymmetricCipher()
  
  print (cipher.get_key())
  
  encrypted = cipher.encrypt('Secret Message A')
  print(encrypted)
  
  encrypted = cipher.encrypt('Secret Message A')
  print(encrypted)
  
  decrypted = cipher.decrypt(encrypted)
  print(decrypted)