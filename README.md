# Team Members
[Alex Wang](https://github.com/alw9411), [Kurt Luko](https://github.com/kl3641), [Sophia Wang](https://github.com/s-m-wang), [Johnny Ding](https://github.com/yd2960)

# Project Description
Our project recognizes text in images and transcribes it to plaintext.

# Lint Free version
![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)


## Installing development environment
Create and activate python virtual environment
```
cd web-app
python3 -m venv venv
source venv/bin/activate
```

Install pipenv
```
pip3 install pipenv
```

Install library dependencies with repsect to ```Pipfile```
```
pipenv install
```

Install tesseract binary:\
for Mac OSX:
```
brew install tesseract
```

for Linux:
```
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

Run the web app on [http://127.0.0.1:8000](http://127.0.0.1:8000)
```
python3 app.py
```

## Development pipeline
1. Write new code
1. Run ```pipenv run pylint modified_file.py``` to ensure you score 10/10
1. Run ```pipenv run black app.py``` to format code

Otherwise, the CI linting will most likely fail, resulting in a nasty red cross on your commit.