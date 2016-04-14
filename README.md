[![Build Status](https://travis-ci.com/seomoz/roger-mesos-tools.svg?token=6DpHsyxZF1vHyofoTmq1&branch=master)](https://travis-ci.com/seomoz/roger-mesos-tools)

# roger-mesos-tools

Tools to connect to and work with [RogerOS](https://github.com/seomoz/roger-mesos), Moz's cluster OS based on mesos.

### Build
`$ python setup.py build`

### Run tests
`$ python setup.py test`

### Generate source distribution
`$ sudo python setup.py sdist`

### Install
```
  # Create the python source distribution
  echo "Creating distribution..."
  sudo pip install -e . --no-deps
  sudo python setup.py sdist
  sudo python setup.py bdist_wheel --universal

  # If the package creation was successful then unzip and copy to /opt/roger-mesos-tools
  if [ -d "dist/" ]; then
      # Extract the tar
      echo "Extracing..."
      sudo mkdir ./extracted && sudo tar -xvf dist/*.tar.gz -C ./extracted/

      echo "Moving extracted files..."
      sudo mkdir -p /opt/ && sudo mv ./extracted/* /opt/roger-mesos-tools

      # Create the new symlink.
      echo "Adding symlink..."
      sudo ln -s /opt/roger-mesos-tools/bin/roger /usr/local/bin/roger
  fi
```

### Use
* `roger -h`
* `roger <command> -h`
