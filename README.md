# Full Stack Developer Capstone Project

## Bot Server API

This is a capstone project I made during my studies at Udacity's Full Stack Developer Nanodegree. My main idea was to make a web app using RESTful APIs of a platform handling the set up of trading bots, at the will of Quant Managers and Traders. For the purpose of this project, only basic functionality will be covered, including setting up database entries of strategies offered and bots. The app is hosted in [`https://rj-capstone.heroku.com`](https://rj-capstone.heroku.com), and features external authentication with [`Auth0`](http://auth0.com).

## Getting Started

The tech stack used relies mainly on:
- Python 3
- Postgresql

You'll need to intall these before proceeding.

In order to run this web app, it is recommended to install create a virtual environment (I recommend installing [`Anaconda`](http://conda.com)) and creating a virtual environment. After creating the environment, activate it, install pip, and the requirements in the `requirements.txt` file inside the project folder:

```bash
conda create your_virtual_env_name
conda activate your_virtual_env_name
conda instal pip
pip install -r requirements.txt
```

If you plan to test the app locally, you need to set up some environment variables. For this however, you will need to setup a local Postgres database and change the `DATABASE_URL` variable in the `setup.sh` file. In order to ease the process of exporting variables, simply source the variables provided using a Terminal:

```bash
source setup.sh
```

Also for convenience, FLASK_APP and FLASK_ENV variables have already been set up in the `setup.sh` file, so if you've sourced it, there is no need to define these afterwards. After going through the steps before, run the server by simply typing on a Terminal:

```bash
flask run
```

## Models

The main models can be found in the file [`models.py`](.models.py), and the ones in place are the `Bot` and the `Strategy`. 

- The `Bot` model features information regarding active status, bot id, name, timeframe, strategy_id used (foreign key) and parameter values. 

- The `Strategy` model features an id, name and parameter names.

## Authentication

This project features external authentication with [`Auth0`](http://auth0.com) using bearer tokens. An authentication script is provided in the `auth.py` file. To try the authenticated endpoints, you will need to add provided bearer tokens in the `setup.sh` file.

The authentication file relies on environment variables sourced from the `setup.sh` file, specifically the AUTH_DOMAIN, ALGORITHMS, and API_AUDIENCE. The file features the following:

- Standard authentication error handler
- Method to get the JWT token header from requests
- Method to check availability and get permissions out of the token
- Method to verify the signature of the JWT token
- Decorator method that is used later in the `app.py` file to enforce route authentication

The endpoints `/strategies` and `/bots` are the only public endpoints. For all other endpoints users must sign into the app and have one role assigned. In order to test endpoints needing authentication, JWT tokens are provided in the `setup.sh` file as environment variables.

## Permissions

There are two types of users in this app with permissions to access different endpoints of the app. The roles available are the `Trader` and the `Quant Manager`.

1. Trader:
    Can get the details of the strategies and bots used, but has only permission to edit bots, so he can change their active status and params for trading. 
    - `get:strategies`
    - `get:bots`
    - `patch:bots`

2. Quant Manager: 
    Can get details and post, patch and delete strategies and bots. In general this manager designs strategies and bots that can be later used by the trader.
    - `get:strategies`
    - `post:strategies`
    - `patch:strategies`
    - `delete:strategies`
    - `get:bots`
    - `post:bots`
    - `patch:bots`
    - `delete:bots`

Active tokens for both roles are provided in the `setup.sh` file in order to test all endpoints needing authentication.

## API Endpoints

All API endpoints are detailed in the [`app.py`](.app.py) file. When running this app locally, the default port is `localhost:5000`. The app is also hosted in Heroku at the URL: [`https://rj-capstone.heroku.com`](https://rj-capstone.heroku.com).

### Public Endpoints

These two endpoints provide limited information from the strategies and bots available, since they do not need authentication. 

GET
- `/strategies`
- `/bots`

### Private Endpoints

The following endpoints need authentication, as described in the permissions chapter from this README file. The Authentication header must contain a JWT token bearer with necessary to succeed.

GET
- `/strategies-detail`
- `/bots-detail`

POST
- `/strategies/create`
- `/bots/create`

PATCH & DELETE
- `/strategies/{id}`
- `/bots/{id}`

### Example API response

All API responses feature JSON encoding. An example public (limited) response has the following example structure:

```python
{
    "active": true, 
    "bot_name": "Great Bot!", 
    "id": 1
  },
{
    "active": true, 
    "bot_name": "Moving Average bot", 
    "id": 2
  }, 
  {
    "active": false, 
    "bot_name": "RSI bot", 
    "id": 3
  }
```

### Example Error response

Error handling is included in the API for most errors and all endpoint errors should return responses in JSON format. An example error response is provided below.

```python
{
  "error": 401,
  "message": "Authorization header is missing.",
  "success": false
}
```

## Testing

In order to run tests, a `test_app.py` file is provided, featuring tests from all endpoints and most errors. This file can be convenientl run through the Terminal the following way:

```bash
python test_app.py
```

As an addition, API endpoint testing can also be done using `Postman`, which also enables seing authenticated responses very conveniently. An importable request collection is also provided within the application directory.

## Acknowledgements

I'd like to thank my darling wife for supporting me all the way in this challenging, but rewarding Nanodegree. Without her support and understanding this experience would have been very different for me, since I also had to work 8-12 hours a day during my studies. I'd also like to thank Udacity, and its community of incredible tutors and fellow students who are always there to help each other when stuck. The set up of the courses was really intended for an immersive, hands-on learning experience, which I've really come to appreciate.
