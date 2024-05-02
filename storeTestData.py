import sqlite3
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Database connection function
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("product.db")
    except sqlite3.Error as e:
        print(e)
    return conn

def history_add(date, userID, productnames, prices,quantity):
    conhistory = sqlite3.connect('history.db')
    cursothistory = conhistory.cursor()

    # Convert lists to strings
    productnames_str = ', '.join(productnames)
    prices_str = ', '.join(map(str, prices))
    quantity_str = ','.join(map(str, quantity))

    cursothistory.execute("INSERT INTO history (date, userID, productnames, prices, quantity) VALUES (?, ?, ?, ? ,?)",
                          (date, userID, productnames_str, prices_str,quantity_str))
    conhistory.commit()
    conhistory.close()
    print("Data added to history.db")


user_list = [
    {"id": 0, "username": "user1", "psw": "1234", "wallet": 1500},
    {"id": 1, "username": "user2", "psw": "1234", "wallet": 1000},
    {"id": 2, "username": "user3", "psw": "1234", "wallet": 2400}
]


@app.route('/history', methods=['GET', 'PUT'])
def index2():
    if request.method == "GET":
        conhistory = sqlite3.connect('history.db')
        cursothistory = conhistory.cursor()
        try:
            # Load JSON data from request
            new_userid = request.form['userid']  # Assuming userid is in the query parameters

            # Execute SQL query to fetch history
            cursothistory.execute("SELECT * FROM history WHERE userID = ?", (new_userid,))
            history_list = cursothistory.fetchall()  # Fetch all rows

            # Check if history exists
            if history_list:
                # Convert rows to list of dictionaries
                history_dicts = []
                for row in history_list:
                    history_dict = {
                        'date': row[1],
                        'productnames': row[3].split(', '),
                        'prices': [int(price) for price in row[4].split(', ')],  # Convert prices to integers
                        'quantity': row[5].split(',')
                    }
                    history_dicts.append(history_dict)

                # Return success response with history list
                return jsonify(history_dicts), 200
            else:
                return jsonify({'error': 'History not found for the given user'}), 404

        except Exception as e:
            # Handle errors and return appropriate error message
            return jsonify({'error': str(e)}), 400
        finally:
            # Close cursor and connection
            cursothistory.close()
            conhistory.close()

    if request.method == 'PUT':
        try:
            # Parse JSON data
            print("test")
            data = request.json
            productnames = data.get('productnames')
            date = data.get('date')
            userid = data.get('userid')  # Corrected from 'userID'
            prices = data.get('prices')
            quantity = data.get('quantity')

            print("test")
            history_add(date, userid, productnames, prices,quantity)

            return jsonify('update successfully ')

        except Exception as e:
            return jsonify(f'error: {e}'), 400
    return jsonify('error: Method not allowed'), 405


@app.route('/')
def index():
    return 'Hello, world!'

# url for users
@app.route('/users', methods=['GET', 'POST'])
def get_user_list():
    if request.method == 'GET':
        return jsonify(user_list)

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_psw = request.form.get('psw')
        new_wallet = 0

        if any(user['username'] == new_username for user in user_list):
            return jsonify({'error': 'Username already exists'}), 409

        new_id = user_list[-1]['id'] + 1 if user_list else 0

        new_user = {
                'id': new_id,
                'username': new_username,
                'psw': new_psw,
                'wallet': new_wallet
            }
        user_list.append(new_user)

        return jsonify({'user add Post successfully get new id:': user_list[-1]['id']}), 201

# url for wallet change
@app.route('/userwallet', methods=['PUT'])
def update_user_wallet():
    if request.method == 'PUT':
        try:
            username = request.form.get('username')
            new_wallet = request.form.get('wallet')
            operation = request.form.get('operation')
        except (TypeError, ValueError):
            return jsonify({'error': 'wallet and operation'}), 400
        # Try to convert the wallet value to float
        try:
            wallet_value = float(new_wallet)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid wallet value provided'}), 400

        # Find the user with the provided username
        for user in user_list:
            if user['username'] == username:
                # Check the operation and update the user's wallet accordingly
                if operation == 'up':
                    user['wallet'] += wallet_value
                elif operation == 'down':
                    if user['wallet'] - wallet_value < 0:
                        return jsonify({'error': 'Insufficient balance'}), 400
                    user['wallet'] -= wallet_value
                else:
                    return jsonify({'error': 'Invalid operation'}), 400

                # Return the updated user data
                return jsonify(user), 200

        # If the user is not found, return a 404 error
        return jsonify({'error': 'User not found'}), 404


#  url for product
@app.route('/products', methods=['GET', 'POST'])
def products_list():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        cursor.close()
        return jsonify(
            [{'id': row[0], 'barcode': row[1], 'name': row[2], 'number': row[3], 'price': row[4]} for row in products])

    if request.method == 'POST':

        try:
            # Load JSON data from request
            new_barcode = request.form['barcode']
            new_name = request.form['name']
            new_number = request.form['number']
            new_price = request.form['price']
            print("post barcode:",new_barcode)

            # Insert data into the database
            cursor.execute("INSERT INTO product (barcode, name, number, price) VALUES (?, ?, ?, ?)",
                           (new_barcode, new_name, new_number, new_price))

            conn.commit()
            conn.close()
            # Return success response
            return jsonify({'Post successfully get new id:': cursor.lastrowid}), 201
        except Exception as e:
            # Handle errors and return appropriate error message
            return jsonify({'error': str(e)}), 400

# url for product to change
@app.route('/products/<barcode>', methods=['GET', 'PUT', 'DELETE'])
def single_product(barcode):
    conn = db_connection()
    cursor = conn.cursor()


    # Get product by barcode
    cursor.execute("SELECT * FROM product WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()

    if request.method == 'GET':
        if product:
            return jsonify({'id': product[0], 'barcode': product[1], 'name': product[2], 'number': product[3],
                            'price': product[4]})
        else:
            abort(404, description="Product not found")

    # Update product by barcode
    if request.method == 'PUT':
        try:
            new_barcode = request.form['barcode']
            new_name = request.form['name']
            new_number = request.form['number']
            new_price = request.form['price']
            print("put barcode:", new_barcode)
            cursor.execute("UPDATE product SET barcode = ?, name = ?, number = ?, price = ? WHERE barcode = ?",
                           (new_barcode, new_name, new_number,
                            new_price, barcode))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Product updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Delete product by barcode
    if request.method == 'DELETE':
        if product:
            cursor.execute("DELETE FROM product WHERE barcode = ?", (barcode,))
            conn.commit()
            conn.close()
            return jsonify({'message': f'Product with barcode {barcode} deleted'}), 200
        else:
            abort(404, description="Product not found")

@app.route('/order', methods=['PUT'])
def order_put():
    if request.method == 'PUT':
        # Get barcode and new number from the request
        try:
            barcode = request.form.get('barcode')
            new_number = request.form.get('number')
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid barcode and number'}), 400

        # Validate new number
        try:
            new_number = int(new_number)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid number value'}), 400

        # Database connection
        conn = db_connection()
        cursor = conn.cursor()

        try:
            # Get product by barcode
            cursor.execute("SELECT * FROM product WHERE barcode = ?", (barcode,))
            product = cursor.fetchone()

            # Check if the product exists
            if not product:
                return jsonify({'error': 'Product not found'}), 404

            # Calculate updated stock quantity
            current_number = product[3]
            updated_number = int(current_number) - new_number

            # Check if the requested quantity is valid
            if updated_number < 0:
                return jsonify({'error': 'Insufficient stock quantity'}), 400

            # Update product quantity in the database
            cursor.execute("UPDATE product SET number = ? WHERE barcode = ?", (updated_number, barcode))
            conn.commit()
            conn.close()

            # Return success message
            return jsonify({'message': 'Product updated successfully'}), 200

        except Exception as e:
            # Return error message in case of any exception
            return jsonify({'error': str(e)}), 400

        finally:
            # Close cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()

if __name__ == '__main__':
    app.run(debug=True)
