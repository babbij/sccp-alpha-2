#!/bin/bash

curl -v \
  -H "Accept: application/json" \
  -X GET "http://localhost:8081/share?sub=https://twitter.com/ijmad8x&pre=http://xmlns.com/foaf/0.1/name&start=1514764800&end=1546300800"
