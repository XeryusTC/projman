Project management
==================
[![Build Status](https://travis-ci.org/XeryusTC/projman.svg?branch=master)](https://travis-ci.org/XeryusTC/projman)
[![Coverage Status](https://coveralls.io/repos/XeryusTC/projman/badge.svg?branch=master&service=github)](https://coveralls.io/github/XeryusTC/projman?branch=master)

A website which helps keeping track of projects and to do lists.

# Deployment

All of the deployment is automated through a Fabric script, it will take
care of all the necessary steps to deploy the code. The only requirement
is that a server runs Debian 7+ (or Ubuntu or similar) that you have root
priveledges on. It will automagically take care of the required software.

## Requirements

All non-python binaries that are necessary are installed via the Fabric
script. If you want to install them manually you can do so by running the
following command:

```
apt-get install nginx git python3 python3-pip postgresql-server-dev-9.4
```

automatic installation can be done via

```
fab requirements --host=<domain>
```

where `<domain>` is the server where you want to install the website on.

As you can see ProjMan needs Nginx and PostgreSQL, if you have a different
setup then you will have to do provisioning manually. You will also need
to edit the default configuration files.

## Provisioning

Provisioning is done by running the command

```
fab provision --host=<domain>
```

where `<domain>` is both the server where the website is to be installed
and the url via which it is usable. When using a domain like
`staging.example.com` this will mean that Fabric will connect to the
server at `example.com` and the website will be available through
`http://staging.example.com`.

The command will start the majority of the Fabric script, including the
steps under deployment. It will require root access since it will create
directories, databases, etc. It first asks questions about the
configuration, if it finds a pre-existing configuration it will ask you
if you want to update it.

The Fabric script will also ask about SSL configuration, if you want to
enable this then you will have to deploy SSL settings manually. An example
configuration can be found in `deploy/ssl.conf-example`, you need to place
it on your server as the file `<nginx-dir>/snippets/ssl.conf`, where
`nginx-dir` is the configuration directory of Nginx, this should be
`/etc/nginx/` by default. The SSL configuration is able to achieve the
highest grade on [SSL labs](https://www.ssllabs.com/ssltest/)'s server SSL
test. It is not perfect since it lacks certain features like OCSP stapling.

After configuration the script will create the necessary directories and
databases if they do not exist yet. After that it will deploy the settings.
The directories that it will create are `/etc/gunicorn/` where the error
and access logs for Gunicorn go. The main storage for the source and
virtualenc is in `/var/www/sites/<domain>/` where `<domain>` is taken
from the invocation command. The settings are stored in the directory
`/etc/www/` in the `gunicorn-<domain>` file.

After this the code is downloaded according to the steps in the Deployment
section. After that step the configuration files are build and stored in
the right location. Finally the necessary services are (re)started.

If you opted not to deploy enable the website then the configuration files
will still be generated but not uploaded. They are stored in
`/tmp/<domain>/` on your local machine. This way you can still check and
edit them before uploading them to the server, just make sure that you
place the right files in the right location.

## Deployment

Deployment consists of updating the source, some files and applying the
latest database migrations. All of these steps can be done without root
priveledges. Unfortunately the Gunicorn service needs to be restarted
before updating takes full effect, fortunately we have a command for this
as well. The commands to update and restart are the following:

```
fab update --host=<domain>
fab restart --host=<domain>
```

The first line is to update the files on the server while the second line
is to restart the necessary services.

## SSL configuration

The supplied SSL configuration is designed to work together with
[Let's Encrypt](https://www.letsencrypt.com), but it is possible to use
any SSL certificate supplier you want if you edit the file correctly. The
settings in the file are designed to be as secure as possible, but they
are still incomplete. The settings do get an A+ on
[SSL Labs](https://www.ssllabs.com/ssltest/). If you do not want to enable
SSL you can ignore this file, however it is recommended to use Let's
Encrypt since it is a free and easy to use service.

# Testing

Testing is done through the Django buildin facilities. If you want to run
the tests then you will have to have the testing packages, these can be
installed using:

```
pip install -r requirements/testing.txt
```

The tests can be run simply by using the command

```
python manage.py test
```

It is also possible to run subsections of the tests by using the name of
the application, more information can be found on the
[Django documentation](https://docs.djangoproject.com/en/1.8/topics/testing/).
It is recommended to not run the tests in the `functional_tests` app
since it will take several minutes to run this test suite. These tests are
also ran by [Travis CI](https://travis-ci.org/XeryusTC/projman) which
automates the testing so that you can continue working while the tests are
ran online.

## Testing against a staging server

Staging servers are equal or very similar to the configuration of the
production server. These staging servers allow running the functional
tests on a server to test if everything works well. Functional tests
should never be ran against the production server since it will destroy
all your data.

Only the functional tests can be ran against the staging server, so it is
only possible to check if the interface works correctly and not if all the
code does work on the server. Fortunately CI takes care of this by being a
near duplicate of the expected configuration.

To run the functional tests against the staging server there are several
steps required. The first is to specify some environment variables so that
sending emails can be tested. You need to have the following environment
variables specified: `PROJMAN_TEST_EMAIL_HOST`,
`PROJMAN_TEST_EMAIL_ACCOUNT` and `PROJMAN_TEST_EMAIL_PASSWORD`, all of
these settings are quite self explanatory. The next step is to have a
public SSH key on your server, guides on how to do this can be found
online. This is recommended because the functional tests will execute
several commands for every test; like resetting the database and creating
accounts.

Finally you can run the functional tests against the staging server by
issueing the following command:

```
python manage.py test functional_tests --settings=projman.settings.testing --liveserver=<domain>
```

where `<domain>` is the same as used for deployment. Note that you need to
use the domain where the website can be accessed, so use
`staging.example.com` instead of `example.com` if you deployed the site
to `staging.example.com`. Now you can sit back and watch your machine test
the website. If you get no errors then that means that your server is set
up to run the ProjMan website!

## Coverage

Coverage can be created by using the `coverage` script, more information
on how to use this utility can be found on the
[Coverage](https://coverage.readthedocs.org/en/coverage-4.0.3/)
documentation. A coverage report is also automatically generated by
Travis, it can be found on [coveralls.io](https://coveralls.io/github/XeryusTC/projman).
