import os, subprocess
 
# this is a temporary hackaround to sidestep issues with concurrency
# in the binding of OpenABE.

# Run separately from the command line in its own process that will get terminated.
 
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
def _run(*args):
  proc = subprocess.run(
    ['bash', './cli.sh'] + list(args),
    cwd=DIR_PATH,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )

  if proc.returncode != 0:
    raise RuntimeError(proc.stderr.decode('utf-8'))

  return proc.stdout.decode('utf-8').strip()



def encrypt(cleartext, attributes):
  return _run('encrypt', cleartext, attributes)

def share(attributes):
  return _run('share', attributes)

def decrypt(ciphertext, sharekey):
  (public_key, secret_key) = sharekey
  return _run('decrypt', ciphertext, public_key, secret_key)



if __name__ == '__main__':
  print('----------------------------------------')
  ciphertext = encrypt('foo', 'abc|def')
  print (ciphertext)
  
  print('----------------------------------------')
  sharekey = share('abc')
  print( sharekey )

  try:
    print('----------------------------------------')
    cleartext = decrypt( ciphertext, ( os.environ['KPABE_PUBLIC_KEY'], 'funk' ))
    print ( cleartext )
  except Exception as e:
    print ('Error!')

  print ('fun fun.')
