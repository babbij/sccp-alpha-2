import requests, os


ABE_ENDPOINT = os.environ.get('ABE_ENDPOINT', None)


class ABE:
  def __init__(self, public_key = None, secret_key = None):
    self.session = requests.Session()
    self.public_key = public_key if public_key else os.environ.get('KPABE_PUBLIC_KEY', None)
    self.secret_key = secret_key if secret_key else os.environ.get('KPABE_SECRET_KEY', None)
    
  def _get_default_headers(self):
    return {
      'x-abe-public-key': self.public_key,
      'x-abe-secret-key': self.secret_key,
    }
    
  def get_mpk_encoded(self):
    return 'A' + binascii.hexlify(base64.b64decode(self.public_key)).decode('US-ASCII')

  def encrypt(self, cleartext, attributes, encoding = 'US-ASCII'):
    r = self.session.post(f'{ABE_ENDPOINT}/encrypt', 
      headers=self._get_default_headers(),
      json={
        'text': cleartext,
        'attributes': attributes.split('|')
      }
    )
    
    if r.status_code == 200:
      robj = r.json()
      return robj['ciphertext']
    else:
      raise RuntimeError(f'Bad response ({r.status_code}, {r.text}) from crypto service')

  def share(self, attributes):
    r = self.session.post(f'{ABE_ENDPOINT}/share',
      headers=self._get_default_headers(),
      json={
        'attributes': attributes.split(' and ')
      }
    )
    
    if r.status_code == 200:
      robj = r.json()
      return (robj['sharekey']['public'], robj['sharekey']['share'])
    else:
      raise RuntimeError(f'Bad response ({r.status_code}, {r.text}) from crypto service')
      

  def decrypt(self, ciphertext, sharekey, encoding = 'US-ASCII'):
    (public_part, share_part) = sharekey
    
    r = self.session.post(f'{ABE_ENDPOINT}/decrypt',
      headers={
        'x-abe-public-key': public_part,
        'x-abe-share-key': share_part,
      },
      json={
        'ciphertext': ciphertext,
      }
    )

    if r.status_code == 200:
      robj = r.json()
      return robj['cleartext']
    else:
      raise RuntimeError(f'Bad response ({r.status_code}, {r.text}) from crypto service')


DEFAULT_ABE = ABE() # uses environment variables


if __name__ == '__main__':
  public_key_1 = 'AAAAFqpvyukKW5LMcF8yf2rq9fQhNPBtcGsAAAGooQFZsgEEtLIBAAJmsPzcTZ+wIeX0X5D6pvvLsvhdaQdsr1EMb711IZmXIlFmqZBMZtgINsvLoGSfIMR45l2DEXPetIAu45x0ZX4H+ABVR3k3lENQo8Eb58dtbujVf7D+8bPs49+fz9n8jRtn87ubxhjN3Rx2YxOEpejh+3hTj3g/n52Vb+8HmPMgEef775dV5EZk6R2m2GVd5xIYXDXFSp6va3z7DdI5hTMe2lbERwn6h3DCFbIlbMyoLZblP3kAHqkIHePsrMeBnB9MMZOjda9hTWjUlqBQVtelBquYL16LxEdSesUyy/FSF+NpC+22nxtWh1MpL0DKA4/etGKle7d4YqhukkkWFQGhAmcxoSSyoSEDCgSgHhtHFDqH5zHTOPztn1ur6ojOkn2lvFpRkn59FjihAmcyoUSzoUEDGn2bbBAZ6lnzjwPWSqaT0DxPe1yMMBRXesv4XJa3YuAeG/4C9Lxif0nxOAjpzDPLhXXHcj4ST1rT0izlS6tTRKEBa6ElHQAAACAIuBbI8oTi3GlpCVsMEoNgR0GTJZ4pnKaWvXvbuhGHSw=='
  secret_key_1 = 'AAAAFqpvyqvfb+Cj4iNPo3ivyoyje31tc2sAAAAooQF5oSOxACAfBMtHxhf3zOV5h9cj4qfGay86GyxlCYoUq32+8tEqsA=='

  abe_1 = ABE(public_key_1, secret_key_1)

  ciphertext_1 = abe_1.encrypt('foobar aruba', 'abc|def')
  print (ciphertext_1)
  print('----------')

  sharekey_1 = abe_1.share('abc')
  print(sharekey_1)
  print('----------')

  cleartext_1 = abe_1.decrypt( ciphertext_1, sharekey_1 )
  print (cleartext_1)
  print('----------')

  public_key_2 = 'AAAAFqpvyjjs8JbgJKPf4x+Bi1MrO9ltcGsAAAGooQFZsgEEtLIBABy79gLrTKZEZeCM3LfQZBbUwTzlHgG3U/nMRbtA28LfEh3EzPDpBpcSTRB8vNE9QdUfHg5QsHpEBxjOuHVSDRESvxv1xH6mqZZp38rLY4msl0OyJtiY0apE0gfMy4kf0Am8ypGiSK2tPWlAnT8tf/GMmATGgcCW7zxhoSYjC4KbIn3Mto9GJfu8dVCUgUejwzlV1FKaQ++LTzXOu8OiXucJ2v86i0vLNKOf7qIKqpw7NPdBU+FwQlOc9yeEvyftCRdyEv38UXcmgsJPK6z3cpVDvAd0fxF/QqMp6Wv73U81CuJk3XCVicp9w7V6WJFFMwqeud/NNUJDKpAMi0Ptd/ihAmcxoSSyoSECBgxLztR3p4Ld5gntMzhlUOAgooGDgpJ53eAKwFImHwqhAmcyoUSzoUECBWB9mBT4tivvhqLQmm+SO02ypRYtN8cf/6drOFYPF+wR4F+ovew3cDE2q5m1uzgboqXcXbH7UKUS/pYsgqYsKKEBa6ElHQAAACAGBA0u8C13O+z+iMryGdEUuk7EOI22LtkWXCJKtmTMwQ=='
  secret_key_2 = 'AAAAFqpvyjoaFq9upCJbLrO0zoi1P3htc2sAAAAnoQF5oSKxAB9HIfSaaTvFQoeSX+oAtankfBRPCxc6p+edI4BXWhzV'
  abe_2 = ABE(public_key_2, secret_key_2)

  ciphertext_2 = abe_2.encrypt('foobar aruba', 'abc|def')
  print (ciphertext_2)
  print('----------')

  sharekey_2 = abe_2.share('abc')
  print(sharekey_2)
  print('----------')

  # use a bad key
  cleartext_1 = ABE().decrypt( ciphertext_2, (public_key_2, 'alkajshgdfkjahsdflkjhaslkdfjhalkjsdhflkajshdfklajshdf') )
  print (cleartext_1)
