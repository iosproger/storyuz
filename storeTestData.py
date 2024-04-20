import sqlite3
from flask import Flask, request, jsonify, abort

app = Flask(__name__)


# Database connection function
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("store.sqlite")
    except sqlite3.Error as e:
        print(e)
    return conn

user_list = [
    {"id": 0, "username": "user1", "psw": "1234", "wallet": 1500},
    {"id": 1, "username": "user2", "psw": "1234", "wallet": 1000},
    {"id": 2, "username": "user3", "psw": "1234", "wallet": 2400}
]

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
@app.route('/userwallet/<username>', methods=['PUT'])
def update_user_wallet(username):
    if request.method == 'PUT':
        new_wallet = request.form.get('wallet')
        operation = request.form.get('operation')

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
            return jsonify({'message': 'Product updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Delete product by barcode
    if request.method == 'DELETE':
        if product:
            cursor.execute("DELETE FROM product WHERE barcode = ?", (barcode,))
            conn.commit()
            return jsonify({'message': f'Product with barcode {barcode} deleted'}), 200
        else:
            abort(404, description="Product not found")

@app.route('/order', methods=['PUT'])
def order_put():
    if request.method == 'PUT':
        # Get barcode and new number from the request
        barcode = request.form.get('barcode')
        new_number = request.form.get('number')

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
