#!/bin/bash

read -r -d '' DATA <<'EOF'

PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
PREFIX owl: <http://www.w3.org/2002/07/owl#>  
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT  #DISTINCT 
	?property   
	(COALESCE(?prefLabel, ?pLabel,"" ) as ?propertyLabel )         
	(COALESCE(?sdomain, ?pdomain,rdfs:Resource) as ?domain)    
	(COALESCE(?definition, ?comment,"") as ?description )  
	?propertyType  
	?superProperty
	?superDomain 
	?v
WHERE {  
	{	# detect those properties without defined domains but superproperties may or may not exist. If none then rdfs:resource assumed
		{	VALUES(?propertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)} 
      		?property a ?propertyType .  
      		#FILTER NOT EXISTS{?property rdfs:domain ?pdomain .}
            OPTIONAL{?property rdfs:domain ?pdomain . } FILTER( !Bound (?pdomain )) 
			{ 
				VALUES(?spropertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)}  
        		?spropertyType a ?spropertyType .  
				{?property rdfs:subPropertyOf ?sproperty}
				UNION {?property rdfs:subPropertyOf [rdfs:subPropertyOf ?sproperty ] }
				UNION {?property rdfs:subPropertyOf [rdfs:subPropertyOf  [rdfs:subPropertyOf ?sproperty ] ] }			
				?sproperty rdfs:domain ?sdomain .  
			}
		}	BIND("15" as ?v)
	} UNION
  	{	# detect those properties with superclasses with different domain (treat as complex), hence property takes subclassDomain ?pdomain
		{	  
              VALUES(?propertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)} 
               ?property a ?propertyType  . 
				?property rdfs:subPropertyOf+ ?sproperty .
      			OPTIONAL{ ?sproperty rdfs:domain ?pdomain }.  
				?property rdfs:domain ?sdomain . 
				FILTER(?pdomain != ?sdomain || !BOUND(?pdomain))
		}	BIND("30" as ?v)
	}  UNION
	{	# detect those properties with superclasses with same domain, hence property takes superProperty Domain ?sdomain
		{	  
              VALUES(?propertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)} 
               ?property a ?propertyType  . 
				?property rdfs:subPropertyOf+ ?sproperty .
				?sproperty rdfs:domain ?sdomain .  
      			OPTIONAL{ ?property rdfs:domain ?pdomain } . 
      			FILTER(?pdomain = ?sdomain || !BOUND(?pdomain))
		}	BIND("35" as ?v)
	} UNION
	{	# detect those properties without superclasses or subproperties of something
		VALUES(?propertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)} 
		?property a ?propertyType .  ?property rdfs:domain ?pdomain .  
		FILTER NOT EXISTS{
      		VALUES(?propertyType){(owl:DatatypeProperty)(owl:AnnotationProperty)(rdf:Property)} 
		    ?property a ?propertyType .  
            ?property rdfs:domain ?pdomain .  
			{ BIND(?property as ?sproperty ) }
      UNION {?property rdfs:subPropertyOf+ ?sproperty}
			?sproperty rdfs:domain ?sdomain .  
      { ?pdomain rdfs:subClassOf+ ?sdomain }
		}	BIND("40" as ?v)
	} 
 	OPTIONAL { ?property rdfs:label ?pLabel }   
	OPTIONAL { ?property skos:prefLabel ?prefLabel }   
	OPTIONAL{ ?property rdfs:comment ?comment. } 
	OPTIONAL{ ?property skos:definition ?definition . } 
	OPTIONAL{ ?property rdfs:subPropertyOf ?superProperty . 
    	OPTIONAL{?superProperty rdfs:domain ?superDomain }
  	}
} 
ORDER BY ?propertyLabel

EOF

echo $VAR

curl -v \
  -H "Accept: application/xml" \
  -H "Content-Type: application/sparql-query" \
  -X POST \
  -d "$DATA" \
  "http://localhost:8080/sparql"
  