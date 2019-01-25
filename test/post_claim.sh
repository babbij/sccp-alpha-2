#!/bin/bash

read -r -d '' DATA <<'EOF'

<rdf:RDF
  xmlns:ns1="http://xmlns.com/foaf/0.1/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="https://twitter.com/jsmith76">
    <ns1:age rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">42</ns1:age>
    <ns1:name>John Smith</ns1:name>
  </rdf:Description>
</rdf:RDF>

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/rdf+xml" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8081/claims"
  