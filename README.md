# Transactions-assignment

This is a Flask server using PostgreSQL as backend and SQLAlchemy as ORM for deploying on local.
This application can add and retrieve transactions details 

Python Version: 3.7.9

Steps to initiate:
1. Install PostgreSQL
2. Install Insomnia/Postman for interaction with the API's
3. pip install -r .\requirements.txt
4. Commands to init db tables:
   1. python manage.py db init
   2. python manage.py db migrate
   3. python manage.py db upgrade
   4. python manage.py db runserver (To run server)

## Create User
 http://localhost:5000/add-user (POST)

JSON:
{
	"username": "ripu",
	"password": "password"
}

## Login 
 http://localhost:5000/login  (POST)
JSON:
{
	"username": "ripu",
	"password": "password"
}

RESPONSE: 
{
	"statusCode": 200,
	"message": "Logged in",
	"token": token
}

## Get data
 http://localhost:5000/get-transactions (GET)

page = 1
limit = 10

city = Delhi
time_range = start_timestamp|end_timestamp
quantity range = start_limit|end_limit
price range = start_range|end_range

## Update Transaction
 http://localhost:5000/update-transaction/57fb7a38c1134066897a1e14718f6609 (PUT)

for Transaction id=57fb7a38c1134066897a1e14718f6609

Headers:
	Authorization token: Bearer <  > 

JSON:
{
	"quantity": 50,
	"unit_price": 10,
	"product_name": "Item 9999"
	"transaction_name" : "XYZ1"
	"delivered_to_city" : "Guwahati"
}
   
## Delete Transaction
http://localhost:5000/update-transaction/57fb7a38c1134066897a1e14718f6609 (DELETE)

for Transaction id=57fb7a38c1134066897a1e14718f6609
Headers:
	Authorization token: Bearer <  > 