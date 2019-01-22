import logging
import os, sys

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')
  logging.getLogger('boto').setLevel(logging.CRITICAL)
  logging.getLogger('botocore').setLevel(logging.CRITICAL)
  
  port = int(os.environ.get('DHT_PORT', 8081))

  from app import app
  app.run(host='0.0.0.0', port=port, debug=True)