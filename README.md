[![Build Status](https://travis-ci.com/seomoz/roger-mesos-tools.svg?token=6DpHsyxZF1vHyofoTmq1&branch=master)](https://travis-ci.com/seomoz/roger-mesos-tools)

# roger-mesos-tools

Tools to connect to and work with [RogerOS](https://github.com/seomoz/roger-mesos), Moz's cluster OS based on mesos.

### Build
`$ python setup.py build`

### Run tests
`$ python setup.py test`

### Generate source distribution
`$ python setup.py sdist`

### Install
`$ python setup.py install`

### Use
* `roger -h`
* `roger <command> -h`

### With virtualenv
```
virtualenv venv
source venv/bin/activate
python setup.py install
# run roger commands
deactivate
```
