#!/bin/bash

read -r -d '' DATA <<'EOF'

PREFIX foaf: <http://xmlns.com/foaf/0.1/>

INSERT DATA { 
  <https://twitter.com/ijmad8x>  foaf:name 'Ian Maddison'.
  <https://twitter.com/ijmad8x>  foaf:age 35
}

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-update" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8083/sparql"
  