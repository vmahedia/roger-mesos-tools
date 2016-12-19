#!/usr/bin/env bash

set -e -o pipefail
[ ${DEBUG:=0} -eq 1 ] && set -x

main() {
  export VAGRANT_VAGRANTFILE='roger-mesos/vagrant/single_node/Vagrantfile'
  vagrant "$@"
}

main "$@"
