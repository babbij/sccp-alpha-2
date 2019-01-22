import ecdsa
import binascii


def string_to_algorithm(alg):
  if alg == 'prime256v1':
    return ecdsa.NIST256p

  raise ValueError(f'Unsupported algorithm: {alg}')



def create_signing_pair():
  alg = ecdsa.NIST256p
  
  sk = ecdsa.SigningKey.generate(curve = alg) 
  vk = sk.get_verifying_key()
  
  return (alg.openssl_name, sk, vk)


def signing_pair_from_string(key, alg_name):
  alg = string_to_algorithm(alg_name)
  sk = ecdsa.SigningKey.from_string(binascii.unhexlify(key), curve = alg)
  vk = sk.get_verifying_key()
  
  return (alg.openssl_name, sk, vk)



if __name__ == '__main__':
  (alg, sk, vk) = create_signing_pair()
  
  sk_str = binascii.hexlify(sk.to_string()).decode('ASCII')
  print(sk_str)
  
  vk_str = binascii.hexlify(sk.get_verifying_key().to_string()).decode('ASCII')
  print(vk_str)
  
  msg = str.encode("my test message", "UTF-8")
  
  sig = sk.sign(msg)
  print(binascii.hexlify(sig).decode('ASCII'))

  print(vk.verify(sig, msg))
  
  sig = sk.sign(msg)
  print(binascii.hexlify(sig).decode('ASCII'))
  
  print(vk.verify(sig, msg))
  
