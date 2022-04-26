import os
from flask import Flask, request, render_template, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json

from functools import wraps
from auth import create_access_token, decode_access_token
from upload_handler import process_uploaded_file

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Transaction

UPLOAD_FOLDER = 'static/files'


@app.route("/")
def hello():

    return("Hello TechVariable !")


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        print("HERE")
        if 'Authorization' not in request.headers:
            res = {
                'statusCode': 401,
                'message': f"Please provide authorization header"
            }
            return Response(json.dumps(res), mimetype='application/json', status=401)

        user = None
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        try:
            user = decode_access_token(token)
        except:
            res = {
                'statusCode': 401,
                'message': f"Not authorized/Invalid Access token"
            }
            return Response(json.dumps(res), mimetype='application/json', status=401)

        return f(*args, **kws)

    return decorated_function


@app.route("/add-user", methods=["POST"])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        user = User.query.filter((User.username == username)).first()

        if user is not None:
            res = {
                'statusCode': 409,
                'message': 'User already exists'
            }
            return Response(json.dumps(res), mimetype='application/json', status=409)

        user = User(
            username_=username,
            password_=password
        )
        db.session.add(user)
        db.session.commit()

        res = {
            'statusCode': 200,
            'message': f"User added : user id={user.id}"
        }
        return Response(json.dumps(res), mimetype='application/json', status=200)
    except Exception as e:
        return (str(e))


@app.route("/login", methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        user = User.query.filter((User.username == username)).first()

        if user is not None:
            if user.check_password(password):
                access_token = create_access_token(user)
                status_code = 200
                res = {
                    'statusCode': status_code,
                    'message': 'Logged in',
                    'token': access_token
                }
            else:
                status_code = 403
                res = {
                    'statusCode': status_code,
                    'message': 'Wrong password!'
                }
        else:
            status_code = 404
            res = {
                'statusCode': status_code,
                'message': "User not registered!"
            }

        return Response(json.dumps(res), mimetype='application/json', status=status_code)

    except Exception as e:
        return (str(e))


@app.route("/upload-csv")
def upload_csv_template():
    try:
        return render_template('upload.html')
    except Exception as e:
        return (str(e))


@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            # set the file path
            uploaded_file.save(file_path)
            items = process_uploaded_file(filepath=file_path)

            for i in items:
                transaction = Transaction(name_=i['Transaction Name'],
                                          product_name_=i['Product Name'],
                                          quantity_=int(i['Quantity']),
                                          unit_price_=float(i['Unit Price']),
                                          delivered_city_=i['Delivered to city'])
                db.session.add(transaction)
                db.session.commit()

        # save the file
        return redirect(url_for('upload_csv_template'))
    except Exception as e:
        print(e)
        return 'Invalid CSV File. Please use the correct format.'


@app.route("/get-transactions", methods=["GET"])
def get_transactions():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    time_range = request.args.get('time_range')
    total_price_range = request.args.get('price_range')
    quantity_range = request.args.get('quantity_range')

    city_name = request.args.get('city')
    try:
        filters = []

        # Quantity Filter
        if quantity_range is not None:
            quantity_range_arr = list(map(int, quantity_range.split('|')))
            print(quantity_range_arr)
            filters.append(
                (quantity_range_arr[0] <= Transaction.quantity) & (Transaction.quantity <= quantity_range_arr[1]))
        # Time range filter (input start_timestamp|end_timestamp : timestamp = int)
        if time_range is not None:
            time_range_arr = list(map(int, time_range.split('|')))
            filters.append((time_range_arr[0] <= Transaction.timestamp) & (Transaction.timestamp <= time_range_arr[1]))
        # Total Price Filter
        if total_price_range is not None:
            total_price_range_arr = list(map(float, total_price_range.split('|')))
            filters.append((total_price_range_arr[0] <= Transaction.total_price) & (
                        Transaction.total_price <= total_price_range_arr[1]))
        # City Filter
        if city_name is not None:
            filters.append(Transaction.delivered_to_city == city_name)

        if filters is None:
            record_query = Transaction.query.paginate(page, limit, False)
        else:
            record_query = Transaction.query.filter(*filters).paginate(page, limit, False)

        total = record_query.total
        record_items = record_query.items

        serialized_items = [i.serialize() for i in record_items]

        response = {
            'statusCode': 200,
            'results': serialized_items,
            'total_items': total,
            'page': page,
            'message': 'Success' if len(serialized_items) > 0 else 'No more items'
        }

        return Response(json.dumps(response), mimetype='application/json', status=200)

    except Exception as e:
        return (str(e))


@app.route("/update-transaction/<tid>", methods=["PUT", "DELETE"])
@authorize
def update_transactions(tid):
    transaction = Transaction.query.filter((Transaction.transaction_id == tid))

    if transaction.first() is None:
        response = {
            'statusCode': 404,
            'message': 'Item not found'
        }

        return Response(json.dumps(response), mimetype='application/json', status=404)

    if request.method == 'PUT':
        transaction_item = transaction.first()

        if request.json.get("quantity") is not None:
            transaction_item.quantity = request.json.get("quantity")
            transaction_item.total_price = int(transaction_item.quantity) * transaction_item.unit_price
        if request.json.get("unit_price") is not None:
            transaction_item.unit_price = request.json.get("unit_price")
            transaction_item.total_price = int(transaction_item.quantity) * transaction_item.unit_price
        if request.json.get("delivered_to_city") is not None:
            transaction_item.delivered_to_city = request.json.get("delivered_to_city")
        if request.json.get("product_name") is not None:
            transaction_item.product_name = request.json.get("product_name")
        if request.json.get("transaction_name") is not None:
            transaction_item.transaction_name = request.json.get("transaction_name")

        r1 = db.session.flush()
        r2 = db.session.commit()
        print(r1, r2)

        response = {
            'statusCode': 200,
            'message': 'Successfully Updated'
        }

        return Response(json.dumps(response), mimetype='application/json', status=200)

    if request.method == 'DELETE':
        r = transaction.delete()
        print(r)
        db.session.commit()

        response = {
            'statusCode': 200,
            'message': 'Successfully deleted'
        }

        return Response(json.dumps(response), mimetype='application/json', status=200)

    return Response(json.dumps({'s': 200}), mimetype='application/json', status=200)


if __name__ == '__main__':
    app.run()
