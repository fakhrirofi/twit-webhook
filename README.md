# twit-webhook
Simple Twitter webhook to manage multiple accounts using
[twitivity](https://github.com/twitivity/twitivity). <br>
Supported **Python** versions: **3.7**, **3.8**, and **3.9**.

## Installation

```bash
git clone https://github.com/fakhrirofi/twit-webhook.git
cd twit-webhook
python3 -m venv venv
. venv/bin/activate # linux
# venv\Scripts\activate # windows
pip3 install -r requirements.txt
```

## Set up the environment

Rename **.env.example** to **.env** and edit the contents.
- You can get the **ENV_NAME** by creating Account Activity API (AAPI) dev
environment at https://developer.twitter.com/en/account/environments.
- There are two options to port forwarding using ngrok:
    * command line
        ```bash
        ngrok http 8080
        ```
    * using pyngrok
        ```python
        >>> from pyngrok import ngrok
        >>> http = ngrok.connect(8080, bind_tls=True)
        >>> url = http.public_url
        >>> print(url)
        ```
    The url (https scheme) will be used to [Register webhook](#register-webhook-to-twitter).
    Don't close the ngrok process.
    
    You can run examples/configure.py as well. Copy that to the root folder,
    then run by using syntax: `python3 configure.py`. It will automatically
    [Register webhook](#register-webhook-to-twitter) and
    [Create subscription](#add-subscription-to-the-webhook).

## Play time!

### Run the webhook

Serve flask app by using syntax:
```bash
flask run --port 8080
```

### Register webhook to twitter

```python
>>> from twitivity import Activity
>>> from dotenv import load_dotenv
>>> import os

>>> load_dotenv('.env')

>>> reg = Activity(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'],
>>>               os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'],
>>>               os.environ['ENV_NAME'])
# because we use ngrok (dynamic url) to run the webhook, we should delete all
# of the previous webhooks before registering a new webhook url
>>> reg.delete_all()
>>> reg.register_webhook(f"NGROK_URL/callback/name_of_the_webhook")
```
- Replace **NGROK_URL** with your new webhook url.
- The reason there is `/callback/` on the last line is because the
**callback_route** argument on **Event** object (at app.py) is `callback`. For more
detail look at [Event class](#event-class).
- `name_of_the_webhook` is the name of webhook. Look at [Webhook variable](#webhook-variable)
for more detail.

### Add subscription to the webhook

```python
>>> reg.subscribe()
```

Send DM to the account, the json data from twitter will be printed on the
terminal screen. Yeay!

### Why [register](#register-webhook-to-twitter) and [subscribe](#add-subscription-to-the-webhook) are different?

If you look at [subscriptions dashboard](https://developer.twitter.com/en/account/subscriptions),
you will see this graph.

![](assets/subscription-graph.jpg)

One AAPI dev environment can only be used to register one webhook. The owner 
(with access token) of Twitter Dev App who can only register the webhook.
Don't forget to edit the **webhook** variable before registering a new webhook.

> Look at [Register webhook](#register-webhook-to-twitter), there is 
**reg.delete_all()**. The purpose is to delete all of the previous webhook. So
we can register a new webhook.

One (free) AAPI dev environment can be used to subscribe up to 15
accounts. To do that, look at [Multiple subscriptions](#multiple-subscriptions).

## Automation example

Copy examples/automation.py to the root folder, then run by using syntax:
`python3 automation.py`.

If you want to forward port using Ngrok for a long time, you should create a
ngrok account. Without Ngrok Auth Token, the ngrok session time is limited.
Copy the Ngrok Auth Token from https://dashboard.ngrok.com/get-started/your-authtoken,
then set the pyngrok auth token by adding this code.
```python
ngrok.set_auth_token('NGROK_AUTH_TOKEN')
```

## Auth

### Generate TOKEN using OAuth

```python
>>> from twitter_auth import TwitterOAuth
>>> auth = TwitterOAuth('CONSUMER_KEY', 'CONSUMER_SECRET')
>>> url = auth.get_url()
>>> print(url)
# open the url, authorize, and copy the PIN
>>> token = auth.get_token('PIN')
>>> print(token)
```

### Generate TOKEN using XAuth
```python
>>> from twitter_auth import get_xauth_access_token
>>> token = get_xauth_access_token('XAUTH_CONSUMER_KEY', 'XAUTH_CONSUMER_SECRET',
>>>                                'TWITTER_USERNAME', 'TWITTER_PASSWORD')
>>> print(token)
```

### (Un)Official Consumer Key
Reference: https://gist.github.com/shobotch/5160017
```
# Twitter for iPhone (XAuth)
Consumer key:    IQKbtAYlXLripLGPWd0HUA
Consumer secret: GgDYlkSvaPxGxC4X8liwpUoqKwwr3lCADbz8A7ADU

# Twitter for iPad (XAuth)
Consumer key:    CjulERsDeqhhjSme66ECg
Consumer secret: IQWdVyqFxghAtURHGeGiWAsmCAGmdW3WmbEx6Hck

# Twitter for Mac (OAuth)
Consumer key:    3rJOl1ODzm9yZy63FACdg
Consumer secret: 5jPoQ5kQvMJFDYRNE8bQ4rHuds4xJqhvgNJM4awaE8
```
**Account that using (Un)Official Consumer Key can't be used to create subscription**,
because we need **ENV_NAME** to register webhook and create subscription.

## Tests

Rename **test.env.example** to **test.env** and edit the contents.<br>
Run the test by using syntax:
```bash
pytest tests/
```
> I don't know why **test_twitivity.py** doesn't work on Github actions, so I
don't test that on Github.

## Customize app.py to manage multiple accounts

### **webhook** variable

The **webhook** template is something like this.
```python
{
    'name_of_the_webhook': 'CONSUMER_SECRET',
}
```
- **name_of_the_webhook** will be used as flask app route. You can add many
webhooks by adding data to the **webhook** dictionary.

### **Event** class

**Event(callback_route, webhook, on_data)**

- **callback_route** is the route that will receives data from twitter. Not
like flask app route, it doesn't need slash '/'. Example: `callback`
- **webhook** is [webhook variable](#webhook-variable).
- **on_data** is a callable that will be called when the webhook receives data.
    It only has one parameter. The argument will be dict (json type), reference:
    https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/account-activity-data-objects.

#### **get_wsgi** method

This method has no parameter and returns flask WSGI app.

### Multiple subscriptions

```python
>>> user1 = Activity('CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN_1',
>>>                  'ACCESS_TOKEN_SECRET_1', 'ENV_NAME')
>>> user1.subscribe()
>>> user2 = Activity('CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN_2',
>>>                  'ACCESS_TOKEN_SECRET_2', 'ENV_NAME')
>>> user2.subscribe()
```
Look at [Auth](#auth) to generate access key with the same webhook.

## Deploy to Heroku

- Add `gunicorn==20.1.0` and `psycopg2==2.8.6` to requirements.txt.

- Create Procfile file
    ```
    # Procfile
    web: gunicorn app:app
    ```

- Configure Heroku app
    ```bash
    heroku git:remote -a your-heroku-app-name
    heroku config:set CONSUMER_SECRET=your-credential
    ```
    You can set the config vars from your app's **Settings** tab in the Heroku
    dashboard as well.

- Push to Heroku
    ```bash
    git add .
    git commit -m 'initial commit'
    git push heroku main
    ```

- [Register](#register-webhook-to-twitter) and [Subscribe](#add-subscription-to-the-webhook)
the webhook.
