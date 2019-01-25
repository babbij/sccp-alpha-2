#!/bin/bash

read -r -d '' DATA <<'EOF'

PREFIX foaf:  <http://xmlns.com/foaf/0.1/>

DELETE {
  ?person foaf:name 'Ian Maddison'
}
INSERT { 
  ?person foaf:name 'Hana Ijecko' 
}
WHERE {
  ?person foaf:name 'Ian Maddison'
}

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-update" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8083/sparql"
  