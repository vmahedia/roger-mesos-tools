#!/usr/bin/env bash

source scripts/common.sh

main(){
  local temp="$(tempfile)"
  sudo iptables -L INPUT --line-numbers | tee "$temp"
  tac "$temp" | while read line; do
    ! echo "$line" | egrep "^[[:digit:]]" > /dev/null 2>&1 && break
    local num="$(echo $line | awk '{ print $1 }')"
    sudo iptables -D INPUT "$num"
  done
  rm -f "$temp"
}

main
