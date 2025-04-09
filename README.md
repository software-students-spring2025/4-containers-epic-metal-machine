![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Team Members
[Alex Wang](https://github.com/alw9411), [Kurt Luko](https://github.com/kl3641), [Sophia Wang](https://github.com/s-m-wang), [Johnny Ding](https://github.com/yd2960)

# Project Description
Our project recognizes text in images and transcribes it to plaintext. This is useful to people who may want to copy paste large chunks of texts from images, and also is useful to people who use screen readers in order to read text. Only Latin characters are supported.


# Running the app
Boot your docker app\
Orchestrate the containers using
```
docker compose up --build
```
The web app now runs on [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Mongodb connection string
After booting the app, use ```mongodb://localhost:27017``` to connect to the database


# Development pipeline
These instructions need further work
1. Go to either ```/machine-learning-client``` or ```/web-app``` folder
1. Run ```source venv/bin/activate``` to boot virtual environment
1. Run ```pipenv run pylint modified_file.py``` to ensure you score 10/10
1. Run ```pipenv run black modified_file.py``` to format code

Otherwise, the CI linting will most likely fail, resulting in a nasty red cross on your commit.