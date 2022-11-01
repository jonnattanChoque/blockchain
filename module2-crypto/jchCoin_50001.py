#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 21:09:04 2022

@author: jonnattanchoque
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 18:43:20 2022

@author: jonnattanchoque
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class BlockChain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        
        block = {'index' : len(self.chain)+1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        
        return block
    
    def get_previous_block(self):
        
        return self.chain[-1]
        
    def proof_of_work(self, previous_proof):
        
        new_proof = 1
        check_proof = False
        while check_proof is False:
            has_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if has_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
            
    def hash(self, block):
        
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            has_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if has_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
            
            
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver, 
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                     max_length = length
                     longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
            
app = Flask(__name__)
# si genera error 500 descomentar la siguiente línea
# app.config['JSONIFY_PRETTYPRINT_REGULTAR'] = False

node_address = str(uuid4()).replace('-', '')

blockChain = BlockChain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockChain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockChain.proof_of_work(previous_proof)
    previous_hash = blockChain.hash(previous_block)
    block = blockChain.create_block(proof, previous_hash)
    blockChain.add_transactions(sender = node_address, receiver = 'Maria Vargas', amount = 10)
    response = {'message' : 'Congratulations, you have created a new block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']}
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain' : blockChain.chain,
                'length' : len(blockChain.chain)
        }
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockChain.is_chain_valid(blockChain.chain)
    if is_valid: 
        response = {'message' : 'Ok, blockchain valid'}
    else:
        response = {'message' : 'Error, blockchain is not valid'}
    return jsonify(response), 200
    

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_key = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_key):
        return 'No parsed json, bad request', 400
    index = blockChain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'OK, transaction created and append to block {index}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'Nodes not exist'
    for node in nodes:
        blockChain.add_node(node)
    response = {'message' : 'OK, Node added', 'total_nodes' : list(blockChain.nodes)}
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_replaced = blockChain.replace_chain()
    if is_replaced:
        response = {'message' : 'Chain replaced', 'new_chain' : blockChain.chain}
    else:
        response = {'message' : 'This is the chain more longest', 'actual_chain' : blockChain.chain}
    return jsonify(response), 200


app.run(host = '0.0.0.0', port = 5001)