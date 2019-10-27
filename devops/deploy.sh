#!/bin/bash

# This script deploy cloudformation take the first parameter as path of config file
# and copy that file to ``${dir_devops}/config-raw.json``, then deploy it with
# master cloudformation template

#set -e

# Resolve path
dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
dir_project_root=$(dirname "${dir_here}")

source "${dir_project_root}/bin/lbd/lambda-env.sh"

$bin_python ${dir_project_root}/config/switch-env dev
$bin_python ${dir_project_root}/tat_aws_creator_auto_tag/devops/config_init.py
bash ${dir_bin}/lbd/deploy-lbd-all-func.sh
