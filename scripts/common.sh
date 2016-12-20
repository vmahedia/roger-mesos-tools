#!/usr/bin/env bash

set -eo pipefail
[ ${DEBUG:=0} -eq 1 ] && set -x

export VAGRANT_SERVICE='localmesos-single-cluster'
export VAGRANT_VAGRANTFILE='roger/ansible/Vagrantfile'
export ANSIBLE_CONFIG='roger/ansible/ansible.cfg'
export HOSTS_FILE='roger/ansible/hosts/localmesos-single-cluster'
