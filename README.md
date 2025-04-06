![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)


## Installing development environment
Create and activate python virtual environment
```
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
python3 web-app/app.py
```