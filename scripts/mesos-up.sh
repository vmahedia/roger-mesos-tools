#!/usr/bin/env bash

source scripts/common.sh

# pass in plug in name as first argument
install_plugin() {
  local plugin="$1"
  if ! vagrant plugin list | grep "$plugin" > /dev/null 2>&1; then
    vagrant plugin install "$plugin"
  fi
}

main() {
  local required_plugins=(vagrant-triggers vagrant-hostsupdater)
  for plugin in ${required_plugins[@]}; do
    install_plugin "$plugin"
  done
  vagrant up
  bash scripts/ansble-plays.sh
  bash scripts/vagrant_runner.sh ssh -c \
    "pushd /vagrant && sudo ./scripts/flush_input_chain.sh && popd"
}

main
