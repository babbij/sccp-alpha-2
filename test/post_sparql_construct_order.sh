#!/bin/bash

read -r -d '' DATA <<'EOF'

PREFIX com: <https://schemas.goodforgoodbusiness.com/common-operating-model/lite/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX j0: <http://example.com/variables#>
PREFIX j1: <urn:uuid:>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
CONSTRUCT {
	#targetEntityIdentifier
	?Order_s <http://targetEntity> true .
	#constructType
	?Order_s <http://assertedType> <https://schemas.goodforgoodbusiness.com/common-operating-model/lite/Order> .
	#constructPath
	?Order_s ?Order_p ?Order_o .
	#constructComplex
	#constructExpandSelect
}
WHERE {
	#selectExpand
	{	SELECT *
		#selectExpandWhere
		{
			#filter
			#search
			#clausesFilter
			#clausesExpandFilter
			#selectPath
			{
				#filter
				#search
				#clausesPath_URI1
				VALUES(?class){(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/Order>)}
				?Order_s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class .
				#clausesFilter
				#clausesExpandFilter
			}
		}
	}
	#clausesPathProperties
	{
		VALUES(?Order_p){(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/acceptedOn>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/buyerRef>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/confirmedOn>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/placedOn>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/quantity>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/shippedOn>)(<https://schemas.goodforgoodbusiness.com/common-operating-model/lite/unitPrice>)(<http://www.w3.org/2000/01/rdf-schema#label>)(<http://www.w3.org/1999/02/22-rdf-syntax-ns#subjectId>)}
		?Order_s ?Order_p ?Order_o .
	}
	#clausesComplex
	#clausesExpandSelect
} LIMIT 10000

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-query" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8081/sparql"
  