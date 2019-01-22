import binascii
import ecdsa
import signing


# these will be provided by sovrin
DID = 'did:sov:ab1321c'
SK_STR = '75be8a74c7d45e226ed852122148b463011eee616e458ccfc3bc25f6795a483c'
ALG = 'prime256v1'

# unencode/instantiate from string
SK = ecdsa.SigningKey.from_string(binascii.unhexlify(SK_STR), curve = signing.string_to_algorithm(ALG))
VK = SK.get_verifying_key()


def sign_with_identity(msg):
  sig = SK.sign(msg)

  return {
    'did': DID,
    'alg': ALG,
    'sig': binascii.hexlify(sig).decode('UTF-8'),
  }



if __name__ == '__main__':
  msg = str.encode('my test message', 'UTF-8')
  
  sig = SK.sign(msg)
  print(VK.verify(sig, msg))