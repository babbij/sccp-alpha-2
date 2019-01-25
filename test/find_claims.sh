#!/bin/bash

curl -v \
  -H "Accept: application/xml" \
  -X GET \
  "http://localhost:8081/matches?sub=<https://twitter.com/jsmith76>&pre=<http://xmlns.com/foaf/0.1/name>"
  