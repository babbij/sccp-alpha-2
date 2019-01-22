#!/usr/bin/env python

import logging
import signal
import json
import os, sys
import datetime

from flask import Flask, Response, request, abort, make_response, jsonify, render_template
from flask_cors import CORS

import rdflib

import dht, search, patterns, keys, share

from abe import abeclient
from claim import create_claim, Pointer, Claim
from shared.repr import from_n3, repr_to_triple


app = Flask(__name__)
CORS(app)


def request_wants_json():
  best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
  return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


@app.route("/matches", methods=['GET'])
def dht_get():
  logging.debug('----------------------------------------')

  claims = search.matches(
    repr_to_triple(json.loads(request.values.get('pattern', None)))
  )

  return Response(
    '[' + ','.join( map(lambda c: c.to_json(False), claims) ) + ']',
    mimetype='application/json'
  )


@app.route("/claims", methods=['POST'])
def claim_post():
  logging.debug('----------------------------------------')
  
  # create claim based on input data
  claim = create_claim(
    request.json['added'],
    request.json['removed'],
    request.json['links']
  )

  # place claim in DHT
  dht.put_claim( claim.get_id(), claim.to_hex(encrypted = True) )

  # place pointers in DHT
  for hash, ptr in claim.get_pointer_map().items():
    dht.put_pointer( hash, ptr.to_encrypted() )

  # create share keys for ourself to ensure we can continue to get our own claims
  # they can be explicit for each statement.
  for pattern in claim.get_patterns(combinations = True, add_time = False, add_mpk = False):
    keys.record_key(pattern, abeclient.DEFAULT_ABE.share(pattern))

  return Response(
    json.dumps({
      'id': claim.get_id()
    }),
    mimetype='application/json'
  )


@app.route("/claims/<id>", methods=['GET'])
def claim_get(id):
  logging.debug('----------------------------------------')

  key = request.values.get('key', None)
  data = dht.get_claim(id)
  if data:
    if key:
      claim = Claim.from_hex(data, key) # FIXME key needs decoding.
      return Response(claim.to_json(False), mimetype='application/json')
    else:
      return Response(json.dumps({ 'data' : data }), mimetype='application/json')
  else:
    return abort(404)


# create a share key for a particular pattern
@app.route('/share', methods=['GET'])
def share_get():
  sub = request.values.get('sub', None)
  pre = request.values.get('pre', None)
  obj = request.values.get('obj', None)
  
  # time limits
  start_time = request.values.get('start', None)
  if start_time:
    start_time = share.convert_datetime_local(start_time)
  
  end_time = request.values.get('end', None)
  if end_time:
    end_time = share.convert_datetime_local(end_time)
  
  # make key
  key = share.make_share_key(sub, pre, obj, start_time = start_time, end_time = end_time)
  
  if request_wants_json():
    return Response(json.dumps({ 'key': key }, indent=2) + '\n', mimetype='application/json')
  else:
    try:
      if sub or pre or obj:
        return render_template('key.html', key = key)
    except ValueError as e:
      pass

    return render_template('share.html')


@app.route('/share', methods=['POST'])
def share_post():
  if request.form and 'key' in request.form:
    keydata = request.form['key']
  else:
    rawdata = request.get_data()
    if rawdata:
      keydata = rawdata.decode('US-ASCII')
    
  if keydata:
    keydata = keydata.strip()
    
    (triple, pattern, key) = share.decode_key(keydata)
    (sub, pre, obj) = triple
    
    logging.debug(f'Accepting key for {triple} -- {pattern}')
    keys.record_key(pattern, key)
  
    if request_wants_json():
      return Response(
        json.dumps({
          'pattern': { 'sub': sub, 'pre': pre, 'obj': obj, }
        }, indent=2) + '\n',
        status=202,
        mimetype='application/json'
      )
    else:
      return render_template('done.html', triple = triple, pattern = pattern, key = key), 202

  return render_template('error.html'), 500

