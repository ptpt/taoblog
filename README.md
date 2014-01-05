Taoblog
=======

Taoblog is just another lightweight blog system.


Dependencies
===========

1. Flask
2. SQLAlchemy
3. hoedown (super fast markdown parser)
4. rauth (OAuth support)
5. pygments (highlight your code)


How to use
===========

Install dependencies:

    pip install -r requirements.txt

Run demo locally:

    python run.py

Visit `localhost:5000` to see what happened.

Most of time, you probably need to do some configuration to meet your
requirements. A configuration file can be specified by the environment
variable `TAOBLOG_CONFIG_PATH`, for example:

    TAOBLOG_CONFIG_PATH="/absolute/path/to/config_file" python run.py

If you would like to deploy it in the production environment, import
`application` module from the provided `taoblog` package, and pass it
to any WSGI server. See
[http://flask.pocoo.org/docs/deploying/](http://flask.pocoo.org/docs/deploying/)
for more details.


Configuration
=============

--------------------------

### `SECRET_KEY`

Keep it complex and secret.

For example:

```python
SECRET_KEY = u'永远是个密秘'.encode('utf-8')
```



--------------------------

### `SERVER_NAME`

Your server name, a string of pattern `address:port`. It must be set
to your actual server name in the production environment.

For example:

```python
server_name = 'example.com' # default port 80
```



--------------------------

### `DEBUG`

If True, it will render debug information when you get exceptions.




--------------------------

### `DATABASE_ECHO`

If True, it will log all statements to your console.





--------------------------

### `DATABASE_URI`

See: [http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#database-urls](http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#database-urls)

For example:

```python
DATABASE_URI = 'sqlite:////path/to/your/taoblog.db'
```




--------------------------

### `ADMIN_EMAIL`

It can be a single email string or a list of email string, or a single
`*`, which means all registered users can be admin.

For example:

```python
ADMIN_EMAIL = 'your@email.com'
ADMIN_EMAIL = '*'        ## WARN: it means EVERY registered users can manage your blog
ADMIN_EMAIL = ['jerry@email.com', 'tom@gmail.com']
```


--------------------------

### `GOOGLE_ANALYTICS_ID`

Your Google analytics ID. If provided, the Google Analytics code will
be embedded in your pages.

For example:

```python
GOOGLE_ANALYTICS_ID = 'UA-35730532-1'
```


--------------------------

### `POST_PERPAGE`

How many posts you want to show per page.



--------------------------

### `FACEBOOK_CONSUMER` and `GOOGLE_CONSUMER`

A tuple stores your consumer info.

For example:

```python
## facebook consumer pairs
FACEBOOK_CONSUMER = ('XXXXX', 'XXXXXX')
```

Licence
=======

Taoblog is under the MIT License. See LICENSE file for full license text.
