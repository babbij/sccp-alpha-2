import pyopenabe

openabe = pyopenabe.PyOpenABE()

context = openabe.CreateABEContext("KP-ABE")
context.generateParams()

# print('----------------------------------------')

# print('PUBLIC:')
public_key = context.exportPublicParams()
print(public_key.decode('US-ASCII'))

# print('----------------------------------------')

# print('SECRET:')
secret_key = context.exportSecretParams()
print(secret_key.decode('US-ASCII'))

# print('----------------------------------------')