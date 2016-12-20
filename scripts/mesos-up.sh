#!/usr/bin/env bash

set -e -o pipefail
[ ${DEBUG:=0} -eq 1 ] && set -x

# pass in plug in name as first argument
install_plugin () {
  local plugin="$1"
  if ! vagrant plugin list | grep "$plugin" > /dev/null 2>&1; then
    vagrant plugin install "$plugin"
  fi

}


main () {
  local required_plugins=(vagrant-triggers vagrant-hostsupdater)
  for plugin in ${required_plugins[@]}; do
    install_plugin "$plugin"
  done
  export VAGRANT_VAGRANTFILE='roger-mesos/vagrant/single_node/Vagrantfile'
  vagrant up
  bash scripts/ansble-plays.sh
  vagrant ssh -c "sudo iptables -F"
}



main
