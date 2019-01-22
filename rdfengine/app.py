#!/usr/bin/env python

import os, logging, json

import requests
from flask import Flask, Response, request, abort, make_response
from flask_cors import CORS

from rdfutil import get_result_format, get_upload_type

from graph import dhtgraph, dhtstore
from graph import localgraph, localstore

app = Flask(__name__, static_url_path='/static')
CORS(app)


@app.after_request
def add_headers(response):
  # response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  # response.headers['Pragma'] = 'no-cache'
  # response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

  return response


def do_query(stmt):
  logging.debug('----------------------------------------')
  
  
  print('dhtgraph=', dhtgraph)
  if dhtgraph is not None:
    result = dhtgraph.query(stmt)
  else:
    result = localgraph.query(stmt)
  
  mimetype, format, pretty_fn = get_result_format(request.headers["Accept"])
  response = make_response(pretty_fn(result.serialize(format=format)))
  response.headers["Content-Type"] = mimetype

  return response


def do_update(stmt):
  logging.debug('----------------------------------------')

  if dhtgraph is not None:
    context = dhtstore.new_context()
    dhtgraph.update(stmt)
    
    # any novel claim made?
    claim = context.get_claim()
    if claim:
      submission = claim.submit()
    
      # save claim in to localstore
      submission.record(localstore)
    
      # return claim id
      result = { 'id': submission.claim_id }
    else:
      result = { 'id': None }

    return Response(
      json.dumps(result, indent=2) + '\n\n',
      mimetype='application/json'
    )
  else:
    localgraph.update(stmt)
    return Response(
      json.dumps({ 'id': None }, indent=2) + '\n\n',
      mimetype='application/json'
    )


@app.route("/sparql", methods=['GET', 'POST'])
def sparql_handler():  
  if request.content_type == 'application/sparql-query':
    return do_query( request.get_data().decode('utf-8') )

  elif request.content_type == 'application/sparql-update':
    return do_update( request.get_data().decode('utf-8') )

  elif 'query' in request.values:
    return do_query(request.values['query'])

  elif 'update' in request.values:
    return do_update(request.values['update'])

  else:
    return abort(400)


# quick method allows direct upload of turtle
@app.route('/upload', methods=['POST'])
def upload_handler():
  (format, data) = get_upload_type(request.content_type, request.get_data())
  claim = dhtstore.new_claim()

  if format and data:
    result = dhtstore.parse(data=data, format=format)
  else:
    return abort(400)
  
  # possibility open that multiple claims could be returned
  if claim.has_captured():
    submit_result = submit(claim)
    update_result = [ submit_result ]
  else:
    update_result = []

  return Response(
    json.dumps(update_result, indent=2) + '\n\n',
    mimetype='application/json'
  )

