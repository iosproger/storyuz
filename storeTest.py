# pip freeze > requirements.txt

from flask import Flask ,request ,jsonify

# withot database

app = Flask(__name__)

book_list = [
    {
        "id":0,
        "barcode":"1021304123",
        "name":"Cola",
        "number":"15",
        "price":"12000"
    },
{
        "id":1,
        "barcode":"1230483745",
        "name":"Fanta",
        "number":"10",
        "price":"8000"
    },
{
        "id":2,
        "barcode":"02183743",
        "name":"Polvon",
        "number":"7",
        "price":"2000"
    }
]

@app.route('/')
def index():
    return 'Hello world'

# @app.route('/<name>')
# def print_name(name):
#     return 'hi , {}'.format(name)

@app.route('/stores',methods=['GET','POST'])
def books():
    if request.method == 'GET':
        if len(book_list) > 0:
            return jsonify(book_list)
        else:
            return 'Nothing Found',404

    if request.method == 'POST':
        new_barcode = request.form['barcode']
        new_name = request.form['name']
        new_number = request.form['number']
        new_price = request.form['price']
        iD = book_list[-1]['id']+1

        new_obj = {
            'id' : iD,
            'barcode': new_barcode,
            'name': new_name,
            'number': new_number,
            'price': new_price
        }
        book_list.append(new_obj)
        return jsonify(book_list) , 201

@app.route('/store/<int:id>',methods=['GET','PUT','DELETE'])
def single_book(id):
    if request.method == 'GET':
        for book in book_list:
            if book['id'] == id:
                return jsonify(book)
            pass
    if request.method == 'PUT':
        for book in book_list:
            if book['id'] == id:
                book['barcode'] = request.form['barcode']
                book['name'] = request.form['name']
                book['number'] = request.form['number']
                book['price'] = request.form['price']
                updated_book = {
                    'id': id,
                    'barcode': book['barcode'],
                    'name': book['name'],
                    'number': book['number'],
                    'price': book['price']
                }
                return jsonify(updated_book)
    if request.method == 'DELETE':
        for index,book in enumerate(book_list):
            if book['id'] == id:
                book_list.pop(index)
                return jsonify(book_list)

if __name__ == '__main__':
    app.run(debug=True)