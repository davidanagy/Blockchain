import hashlib
import random
import requests
import sys
import json
from timeit import default_timer


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True)
    # Use random proofs until we find a valid one
    proof = random.random()
    while not valid_proof(block_string, proof):
        proof = random.random()
    return proof


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


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # Set coins at 0 to start
    coins = 0
    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Check to see if response is in json format
        try:
            data = r.json()

            # TODO: Get the block from `data` and use it to look for a new proof
            last_block = data['block']
            print('Looking for new proof')
            start = default_timer()
            new_proof = proof_of_work(last_block)
            end = default_timer()
            print('Found new proof')
            # Subtract start from end to get seconds elapsed.
            # Divide by 60 to get minutes, then round to the nearest hundredth.
            print(f'Time elapsed: {(end-start)/60:.2f} minutes')

            # When found, POST it to the server {"proof": new_proof, "id": id}
            post_data = {"proof": new_proof, "id": id}

            r = requests.post(url=node + "/mine", json=post_data)
            # Check to see if response is in json format
            try:
                data = r.json()
                print('Server message:', data['message'])
                # TODO: If the server responds with a 'message' 'New Block Forged'
                # add 1 to the number of coins mined and print it.  Otherwise,
                # print the message from the server.
                if data['message'] == 'New Block Forged':
                    coins += 1
                    print('Number of coins:', coins)
                # Already printed the server message above, so just print a blank line
                # to separate each mining round.
                print('')
            except ValueError:
                # If response is not in json format
                print('Error:  Non-json response')
                print('Response returned:')
                print(r)
                print('')

        except ValueError:
            # If response is not in json format
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            print('')
