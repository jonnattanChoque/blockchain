#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 22:37:49 2022

@author: jonnattanchoque
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify

class BlockChain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        
        block = {'index' : len(self.chain)+1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash}
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
            
            
            
app = Flask(__name__)

blockChain = BlockChain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockChain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockChain.proof_of_work(previous_proof)
    previous_hash = blockChain.hash(previous_block)
    block = blockChain.create_block(proof, previous_hash)
    response = {'message' : 'Congratulations, you have created a new block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']
        }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain' : blockChain.chain,
                'length' : len(blockChain.chain)
        }
    return jsonify(response), 200
    

app.run(host = '0.0.0.0', port = 5001)