#!/bin/bash
function color {
    if [ -n "$1" ]; then
        echo -e -n "\033[$1;1m"
    else
        echo -e -n "\033[m"
    fi
}
green=`color 32`
blue=`color 34`
red=`color 31`
normal=`color`

function error {
    echo ${red}${1}${normal}
    exit 1
}

path="/usr/local/bin"
files="input-tester input-generator input-sample"
for f in $files; do
    cmd="sudo rm $path/$f"
    echo $cmd
    $cmd || error "Failed"
done

echo "${green}Done${normal}"
