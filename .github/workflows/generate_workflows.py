#!/usr/bin/env python3

SERVICES = [
  'sesame',
  'office',
  'keeper',
  'crypto',
  'carpetradar24',
  'mumbler'
]


TEMPLATE = '''
name: Check {service}
on:
  push:
    branches:
      - main
    paths:
      - 'services/{service}/**'
      - 'checkers/{service}/**'
  workflow_dispatch: {{}}

jobs:
  check_services:
    name: Check {service}
    runs-on: ubuntu-18.04

    steps:
    - name: Checkout repo
      uses: actions/checkout@v2

    - name: Setup {service}
      run: (cd ./services/{service} && docker-compose pull && docker-compose build && docker-compose up --build -d)

    - name: Prepare python for checker
      uses: actions/setup-python@v2
      with:
        python-version: 3.8.5

    - name: Setup checker libraries
      run: if [ -f checkers/{service}/requirements.txt ]; then python -m pip install -r checkers/{service}/requirements.txt; fi

    - name: Test checker on service
      run: checkers/{service}/checker.py TEST 127.0.0.1

'''

for s in SERVICES:
    with open('check_{}.yml'.format(s), 'w') as f:
        f.write(TEMPLATE.format(service=s))
