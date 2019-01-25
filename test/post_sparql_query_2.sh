#!/bin/bash

read -r -d '' DATA <<'EOF'

SELECT ?name
  WHERE {
    <https://twitter.com/ijmad8x> <http://xmlns.com/foaf/0.1/name> ?name
  }


EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-query" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8081/sparql"
  