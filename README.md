# Gimme

Gimme is an App Engine app that can be used to temporarily escalate people's
access to resources in GCP. It does this by leveraging GCP's IAM conditions.

The escalations are stored in Datastore and if not approved expire after
10 minutes.

## Usage

Open up Gimme and fill in the form on the home page to request acces to a
resource. The approver will receive an email informing them of the request
and pointing them to the "Pending Requests" page where they can review and
approve their requests. You can check on the progress of your requsets on
that same page, as well as see if there's any requests awaiting your
approval.

When the request is approved an attempt is made to change the IAM policy
of the target resource and add a condition granting the requester access
at the requested level for the requested time. In order for this request
to succeed the approver needs to have the necessary privileges to set an
IAM policy on the requested resource.

When the request is denied it is simply expired from the data.

When the request is reported it is expired from the database and an email
is sent to the Security teams informing them of a potential malicious
attempt to escalate one's privileges.

## Installation

Because this is an App Engine application only Python 2.7 is supported for
development, as that is the App Engine Python runtime that is in use.

Getting a GAE application to run locally is a bit painful b/c you can't just
`pip install appengine` and be good to go. Some of the client libraries and
support tooling have to be installed through the Google Cloud SDK, aka
`gcloud`.

1. Clone the project
2. `pipenv shell` to create/activate a new virtualenv
3. `pipenv install` to install the app's dependencies (except for AppEngine stuff)

Now comes the magic:

```sh
$ pipenv run pip install -r <(pipenv lock -r) --target lib/
...
Successfully installed click-6.7 flask-1.0.2 ...
```

This will have installed the dependencies a second time but now specifically into
the `lib/` folder. This is automatically prepended to the Python path based on the
code in `appengine_config.py`. Essentially we've just vendored the dependencies. This
is what makes things work in App Engine. Note that it only works for native Python
dependencies, no C extensions.

You'll need to execute the above command whenever you install a new dependency or
update an existing one.

## Configuration

Gimme doesn't have a lot of nobs worth tweaking and those that you can tweak are
available as environment variables.

* `GIMME_PLEASE_NOTE`: path to a file containing HTML that will get injected on
  the index page. It should detail any constraints imposed by Gimme.
* `GIMME_ABOUT_ACCESS`: path to a file containing HTML that will get injected on
  the index page. It should detail what values the access field in the form
  supports.
* `DISABLE_GAE_AUTH`: disables the code paths that use the App Engine Python SDK
  to get (or fake) a proper user as we would see when the application is deployed
  on App Engine. This is useful in development if you can't get, or don't want to,
  install the App Engine Python SDK.

  Setting `DISABLE_GAE_AUTH=yes` in production is an Extremely Bad Idea™ and defaults
  to `False` without respecting the value of `DISABLE_GAE_AUTH` in the production
  configuration settings.
* `GIMME_SETTINGS`: path to a `.py` file with contents similar to one of the `Config`
  classes from `settings.py`. This gives you complete control over all settings and
  circumvents any safeguards we might have built-in when it comes to handling those.
  Use with caution.

## Deploying

In order to deploy this app to App Engine you need to be a Google Cloud
customer. We recommend creating a separate project for this application so
it can live in its own, isolated environment.

Once that's done you can run a `gcloud --project=<YOUR PROJECT> app deploy
app.yaml` to deploy the application. Once that's done a `gcloud --project=<YOUR
PROJECT> app browse` will open up a browser for you present you with your
deployed application.

For further information on how to deploy to App Engine, how to use the preview
environment, do rolling deploys etc. please review the `gcloud app` help and
documentation.

## Development

Please note that with rare exception, pull requests will not be accepted
without tests to cover the changed or new behaviour.

Whichever way you start Flask, ensure you have `FLASK_DEBUG` set to `true`
and `FLASK_ENV` set to `development`. Additionally `GIMME_DEV` must be
set to `true` in order to fully load all development settings.

### Without App Engine Python SDK

You can start Gimme with `DISABLE_GAE_AUTH=yes FLASK_ENV=development
FLASK_APP=autoapp.py flask run`. By disabling GAE authentication support we
also don't import anything from the `google.*` Python namespace so you can
run entirely from within a virtualenv.

### With App Engine Python SDK

First, deactivate your virtualenv. This is important. If your virtualenv is still active,
this will not work.

Ensure you have `gcloud` installed and run `gcloud components install app-engine-python`
and `gcloud components install app-engine-python-extras`. The latter is needed in order to
be able to use functionality from the SSL module (amongst other things).

Now try: `dev_appserver.py app.yaml`, that should show you something like:

```text
INFO     2018-06-15 22:08:58,614 devappserver2.py:120] Skipping SDK update check.
INFO     2018-06-15 22:08:58,688 api_server.py:274] Starting API server at: http://localhost:33999
INFO     2018-06-15 22:08:58,710 dispatcher.py:270] Starting module "default" running at: http://localhost:8080
INFO     2018-06-15 22:08:58,711 admin_server.py:152] Starting admin server at: http://localhost:8000
```

The "admin server" is a special component of the GAE SDK, it lets you do things like look
at data in the built-in Datastore and Memcached.

Authentication is enabled and enforced for this app. When running in development mode it
will show you a login screen in which you can just enter an email and it will fake a
user. In production you'll see a properly configured consent screen once you set that
up. If you log in with an invalid user you can browse to `/_ah/logout` to remove that
session and try again.

### Testing

Gimme comes with a suite of unit tests powered by pytest. We additionally check and
enforce a number of things through flake8 and a few of its plugins.

In order to run the tests you can:

```sh
$ pytest --verbose -x --flake8 --cov=gimme --cov-report=term tests/

============================ test session starts ============================
platform linux2 -- Python 2.7.14, pytest-3.6.2, py-1.5.3, pluggy-0.6.0 -- /home/daenney/.local/share/virtualenvs/gimme-IW0Pxo7A/bin/python2.7
cachedir: .pytest_cache
rootdir: /home/daenney/Development/spotify/gimme, inifile: setup.cfg
plugins: flake8-1.0.1, cov-2.5.1

[..]
---------- coverage: platform linux2, python 2.7.14-final-0 ----------
Name                Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------
gimme/forms.py          9      0      0      0   100%
gimme/helpers.py       28     11      6      1    53%
gimme/settings.py      28      0      2      0   100%
gimme/views.py         34      1      2      1    94%
-----------------------------------------------------
TOTAL                  99     12     10      2    83%


==================== 18 passed, 4 skipped in 0.50 seconds ====================
```