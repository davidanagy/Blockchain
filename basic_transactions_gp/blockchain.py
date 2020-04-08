# Paste your version of blockchain.py from the client_mining_p
# folder here
import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)
            guess = f'{block_string}{proof}'.encode()
            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            current_hash = ''

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
            'hash': current_hash
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    def new_transaction(self, sender, recipient, amount):
        obj = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.current_transactions.append(obj)
        return len(self.chain) + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 6
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == '000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    # Get proof from the request
    data = request.get_json()
    if 'proof' not in data or 'id' not in data:
        response = {
            'type': 'error',
            'message': 'Request must be a JSON object with "proof" and "id" fields'
        }

        # 400 error
        return jsonify(response), 400

    else:
        proof = data['proof']
        block_string = json.dumps(blockchain.last_block, sort_keys=True)
        if blockchain.valid_proof(block_string, proof):
            # Reward the miner with one coin
            miner_id = data['id']
            blockchain.new_transaction(0, miner_id, 1)
            # If proof is valid, forge the new Block by adding it to the chain with the proof
            previous_hash = blockchain.hash(blockchain.last_block)
            block = blockchain.new_block(proof, previous_hash)
            response = {
                'type': 'success',
                'message': 'New Block Forged',
                'index': block['index'],
                'transactions': block['transactions'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']
            }
        else:
            # If proof is not valid, return a failure response
            response = {
                'type': 'failure',
                'message': 'Proof not valid'
            }

        return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def get_last_block():
    response = {'block': blockchain.last_block}
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_user_transaction():
    data = request.get_json()
    if 'sender' not in data or 'recipient' not in data or 'amount' not in data:
        response = {
            'type': 'error',
            'message': '''Request must be a JSON object with "sender", "recipient",
            and "amount" fields'''
        }
        return jsonify(response), 400
    
    else:
        index = blockchain.new_transaction(data['sender'], data['recipient'], data['amount'])
        response = {
            'type': 'success',
            'message': f'Transaction completed successfully and is contained in block {index}'
        }
        return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
