[![Build Status](https://travis-ci.org/andela-rwachira/cp2.svg?branch=develop)](https://travis-ci.org/andela-rwachira/cp2)
[![Coverage Status](https://coveralls.io/repos/github/andela-rwachira/cp2/badge.svg?branch=develop)&bust=1](https://coveralls.io/github/andela-rwachira/cp2?branch=develop)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/andela-rwachira/cp2/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/andela-rwachira/cp2/?branch=develop)
![Python Version](https://img.shields.io/badge/python-2.7-brightgreen.svg)


# Bucketlist API. 

This is a Flask-RESTful API for a bucketlist service. 
It was built using Flask and Flask_SQLAlchemy.

## Install

These are the basic steps to install and run the application locally on a linux system:

Create a project directory:
```
$ mkdir flask_app

$ cd flask_app
```

Set up and activate your virtual environment:

You can find instructions [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Once you have activated your virtualenv, clone the repo from GitHub:
```
$ cd flask_app

$ git clone https://github.com/andela-rwachira/cp2
```

Install the requirements:
```
$ pip install -r requirements.txt
```

## Launch

Run the following commands from the root folder containing manage.py:

Set up the database and run an inital migration:
```
$ python manage.py db init

$ python manage.py db migrate

$ python manage.py db upgrade
```

Start the local server:
```
$ python manage.py runserver
```

## Usage

Once your local server is up and running, you can use your favourite REST Client
to interact with the endpoints below. I recommend [Postman](https://www.getpostman.com/)
from Chrome which was used in the building of this app.


| Method | URL | Description | Token Required |
| -------- | ------------- | --------- |--------------- |
| POST | `/auth/register/` | User registration | FALSE |
| POST | `/auth/login/` | User login | FALSE |
| POST, GET | `/bucketlists/` | Create or retrieve a user's bucketlist(s) | TRUE |
| GET, PUT, DELETE | `/bucketlists/<id>` | Retrieve, update or delete a user's specific bucketlist | TRUE |
| POST | `/bucketlists/<id>/items/` | Create a single item in a user's bucketlist | TRUE |
| PUT, DELETE | `/bucketlists/<id>/items/<item_id>` | Update or delete a user's item | TRUE |


### Quick video demo

You can watch a 4 minute video demo on [Youtube](https://youtu.be/Ygoi3rThK38)

### Screenshots

Registering a user:

![POST Register](https://cloud.githubusercontent.com/assets/20615801/20676913/807821fa-b5a2-11e6-91a2-e7fe36fc6f17.png)


Logging a user in:

![POST Login](https://cloud.githubusercontent.com/assets/20615801/20676746/e2820088-b5a1-11e6-8e96-7b9a01d62bbe.png)


All endpoints requiring authentication will require the Token in the Header as below:

![POST Bucketlist Header](https://cloud.githubusercontent.com/assets/20615801/20676982/b1650d50-b5a2-11e6-9415-385dc5e0202a.png)


Creating a new bucketlist

![POST Bucketlist](https://cloud.githubusercontent.com/assets/20615801/20677035/dc5d3190-b5a2-11e6-9d5c-342ad2e9a3c5.png)


Listing all your bucketlists

![GET Bucketlists](https://cloud.githubusercontent.com/assets/20615801/20677096/08363280-b5a3-11e6-8e75-72cf0cd9123d.png)


Getting a single bucketlist

![GET Single Bucketlist](https://cloud.githubusercontent.com/assets/20615801/20677153/3439c432-b5a3-11e6-8dfd-dc7cabc21d61.png)


Updating a bucketlist

![PUT Bucketlist](https://cloud.githubusercontent.com/assets/20615801/20677190/585bb9ec-b5a3-11e6-9cdd-3245c7ab4a57.png)


Deleting a bucketlist

![DELETE Bucketlist](https://cloud.githubusercontent.com/assets/20615801/20677239/83edf6ce-b5a3-11e6-8549-4199b821fd07.png)


Creating a new item within a bucketlist

![POST Item](https://cloud.githubusercontent.com/assets/20615801/20677307/b1e0451e-b5a3-11e6-8878-866b2502afb0.png)


For easy navigation, the response includes a URL to view your newly created item and the rest of your bucketlists:

![URL_FOR New Item](https://cloud.githubusercontent.com/assets/20615801/20677333/c590941a-b5a3-11e6-98ce-f3ccc969d69f.png)


Updating an item

![PUT Item](https://cloud.githubusercontent.com/assets/20615801/20677407/09197238-b5a4-11e6-8cef-ef709ca0686b.png)


Deleting an item

![DELETE Item](https://cloud.githubusercontent.com/assets/20615801/20677545/735ba684-b5a4-11e6-95a8-c9d60400ae12.png)


## Testing

Run the following command from the root folder
```
$ coverage run -m unittest discover
```

Run the following command to see the results in an easy-to-read table 
```
$ coverage report
```
