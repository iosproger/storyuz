import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# with database

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("store.sqlite")
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/')
def index():
    return 'Hello world'

@app.route('/stores', methods=['GET', 'POST'])
def products():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        print("get")
        cursor.execute("""
            SELECT * FROM "product"
        """)
        products = [
            dict(id=row[0], barcode=row[1], name=row[2], number=row[3], price=row[4])
            for row in cursor.fetchall()
        ]
        if products:
            return jsonify(products)
        else:
            return jsonify([])  # Return an empty list if no products found
    if request.method == 'POST':
        print("post")
        new_barcode = request.form['barcode']
        new_name = request.form['name']
        new_number = request.form['number']
        new_price = request.form['price']
        sql = """INSERT INTO product(barcode, name, number, price) VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (new_barcode, new_name, new_number, new_price))
        conn.commit()
        return f'Product with the id: {cursor.lastrowid} created successfully', 201

@app.route('/store/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_product(id):
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        print(f"get {id}")
        cursor.execute("""SELECT * FROM "product" WHERE barcode=?""", (id,))
        product = cursor.fetchone()
        if product:
            return jsonify(dict(id=product[0], barcode=product[1], name=product[2], number=product[3], price=product[4]))
        else:
            return jsonify({'message': 'Product not found'}), 404

    if request.method == 'PUT':
        sql = """UPDATE "product"
                 SET barcode = ?, name = ?, number = ?, price = ?
                 WHERE id = ?"""
        barcodee = request.form['barcode']
        namee = request.form['name']
        numberr = request.form['number']
        pricee = request.form['price']
        up_pr = {
            "id":id,
            "barcode" : barcodee ,
            "name" : namee,
            "number" : numberr,
            "price" : pricee
        }
        conn.execute(sql, (barcodee,namee,numberr,pricee,id))
        conn.commit()
        return jsonify(up_pr)

        ### GPT
        # print(f"put to {id}")
        # updated_data = request.get_json()
        # # Ensure that the required fields are present in the JSON data
        # if 'barcode' in updated_data and 'name' in updated_data and 'number' in updated_data and 'price' in updated_data:
        #     updated_data['id'] = id
        #     sql = """UPDATE product
        #              SET barcode = ?, name = ?, number = ?, price = ?
        #              WHERE id = ?"""
        #     cursor.execute(sql, (
        #     updated_data['barcode'], updated_data['name'], updated_data['number'], updated_data['price'], id))
        #     conn.commit()
        #     return jsonify(updated_data), 200
        # else:
        #     return jsonify({'error': 'Incomplete data provided'}), 400

    if request.method == 'DELETE':
        print(f"del id {id}")
        cursor.execute("""DELETE FROM "product" WHERE barcode=?""", (id,))
        conn.commit()
        return jsonify({'message': f'Product deleted {id}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
