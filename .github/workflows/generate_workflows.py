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
  check_{service}:
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
  update_{service}:
    name: Deploy service using ansible to first teams
    needs: check_{service}
    runs-on: ubuntu-18.04

    steps:
    - name: install ansible
      run: sudo apt-get install -y ansible

    - name: Checkout repo
      uses: actions/checkout@v2

    - name: change permission for ssh key
      run: chmod 0600 ./vuln_image/keys/id_rsa

    - name: try to deploy {service}
      run: ./vuln_image/update_first_ten_teams.sh {service}

'''

for s in SERVICES:
    with open('check_{}.yml'.format(s), 'w') as f:
        f.write(TEMPLATE.format(service=s))
