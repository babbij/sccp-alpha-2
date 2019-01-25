#!/bin/bash

read -r -d '' DATA <<'EOF'

DELETE DATA { 
  <https://twitter.com/abcd>  foaf:name 'Alice Bobbit' .
  <https://twitter.com/abcd>  foaf:age 32
}

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-update" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8080/sparql"
  