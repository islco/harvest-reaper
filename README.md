# Harvest Reaper

Get your harvest data seamlessly from Google.
![Reaper Image](https://github.com/istrategylabs/harvest-reaper/blob/master/harvestreaper/static/img/graveyard-footer-art.png)

---

## Developing

### Requirements

* [Python 3](https://www.python.org) (with [pipenv](http://pipenv.readthedocs.io/en/latest/))
* [foreman](http://ddollar.github.io/foreman/)
* [PostgreSQL](https://www.postgresql.org)
* [nvm](https://github.com/creationix/nvm)
* [Google Application](https://console.developers.google.com/apis/credentials/oauthclient)
* [Harvest OAuth2 Application](https://id.getharvest.com/developers)


### Python and Django

First you need to configure your environment:

```
cp env.example .env
```

Edit *.env* and set the values you need to run the project locally. Foreman will take care
of loading these values into the environment when you execute a command.

Next, create a Python 3 virtual environment and install the requirements:

```
pipenv install --dev --python 3.7
pipenv shell
```

Create the database specified in *.env*, run the initial model migration,
and create a super user:

```
createdb harvestreaper
foreman run python manage.py migrate
foreman run python manage.py createsuperuser
```

### Front End Tools

Use nvm to install the correct version
of Node.js and install the front-end dependencies:

```
nvm install
npm install
```

Do an initial build of assets:

```
npm run build
```


## Running the Project

First load the virtualenv:

```
pipenv shell
```

Then use [foreman](http://ddollar.github.io/foreman/) to run the development processes:

```
foreman start -f Procfile.dev
```

*Procfile.dev* defines the following processes:

* web: the Django development server
* rqworker: the RQ worker process (high, low, and default) - **Not used yet**

`foreman start -f Procfile.dev` will start all of the processes at once. If you
want to run a specific process, you can specify it directly:

```
foreman start -f Procfile.dev web
```


## Deploying the Project
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

After deploying you will need to update both your Site's objects in the Admin to include the correct domain
and add the Google SocialApplication for authentication.
