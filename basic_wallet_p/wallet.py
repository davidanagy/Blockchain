from flask import Flask, render_template, request
import os
import requests
import sys


app = Flask(__name__)

# Read user_id from id.txt if it exists; if it doesn't, set it to None.
# You can delete this file yourself to see what happens when you boot up the app
# with no ID saved.
id_filename = './id.txt'
if os.path.exists(id_filename):
    with open(id_filename, 'r') as f:
        user_id = f.read()
else:
    user_id = None

# The blockchain server needs to be hosted locally at a 5000 address.
# I recommend running this locally through the following process in your command line:
# 1) Type ` set FLASK_APP=wallet.py ` while in the directory containing this file.
# 2) Type ` flask run --port 5001`
node = "http://localhost:5000"


@app.route('/')
def root():
    # Count coins, so we start at 0.
    coins = 0
    r = requests.get(url=node+"/chain")
    data = r.json()
    chain = data['chain']
    relevant_transactions = []
    for block in chain:
        # Pull out the transactions
        transactions = block['transactions']
        for transaction in transactions:
            # If sender is the user_id, subtract the amount from their coins,
            # and display the transaction.
            if transaction['sender'] == user_id:
                coins -= transaction['amount']
                relevant_transactions.append(transaction)
            # If recipient is the user_id, add the amount to their coins,
            # and display the transaction.
            elif transaction['recipient'] == user_id:
                coins += transaction['amount']
                relevant_transactions.append(transaction)

    return render_template('base.html', title='Home', user_id=user_id,
                            balance=coins, transactions=relevant_transactions)


@app.route('/user', methods=['POST', 'GET'])
def user():
    # If the method is post, that means they're submitting a new ID
    if request.method == 'POST':
        # Set user_id as global so we can modify the global variable
        global user_id
        if not user_id:
            # If user_id is None, that means the user has set the ID for the first time.
            user_id = request.values['user_id']
            message = f"You've set your ID. Welcome, {user_id}!"
        else:
            # Otherwise, that means the user has changed their ID.
            user_id = request.values['user_id']
            message = f"You've changed your ID! Your new ID is {user_id}."
    else:
        # If the method is get, that means they're just checking their ID.
        message = f'Your ID is {user_id}.'
    return render_template('user.html', title='ID', user_id=user_id, message=message)


@app.route('/user/save', methods=['GET'])
def save_id():
    # Write their ID into a text file
    with open(id_filename, 'w') as f:
        f.write(user_id)
    return render_template('save_id.html', title='ID')


if __name__ == '__main__':
    app.run()
