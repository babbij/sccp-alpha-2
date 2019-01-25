#!/bin/bash

read -r -d '' DATA <<'EOF'

PREFIX com: <https://schemas.goodforgoodbusiness.com/common-operating-model/lite/>
SELECT ?buyerRef ?quantity ?unitPrice ?shipmentRef ?ain ?vaccine WHERE {
  ?order com:buyer <urn:uuid:448c5299-b858-4eb1-bc55-0a7a6c04efee>;
    com:buyerRef ?buyerRef;
    com:quantity ?quantity;
    com:unitPrice ?unitPrice;
    com:fulfilledBy ?shipment.
  ?shipment com:consignee <urn:uuid:448c5299-b858-4eb1-bc55-0a7a6c04efee>;
    com:shipmentRef ?shipmentRef.
  OPTIONAL {
    ?shipment com:usesItem ?cow.
    OPTIONAL {
      ?cow com:ain ?ain.
      OPTIONAL {
        ?cow com:vaccination ?vaccination.
        ?vaccination com:vaccine ?vaccine.
      }
    }
  }
}

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-query" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8081/sparql"
  