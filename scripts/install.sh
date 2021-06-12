#!/bin/bash
# Install prerequisites
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [ ! -f /usr/local/bin/pylint ]; then
    brew install pylint
  fi
  if [ ! -f /usr/local/bin/pre-commit ]; then
    brew install pre-commit
  fi
  if [ ! -f /usr/local/bin/black ]; then
    brew install black
  fi
  if [ ! -f /usr/local/bin/terraform-docs ]; then
    brew install terraform-docs
  fi
  if [ ! -f /usr/local/bin/tflint ]; then
    brew install tflint
  fi
  if [ ! -f /usr/local/bin/gbase64 ]; then
    brew install coreutils
  fi
  if [ ! -f /usr/local/bin/gawk ]; then
    brew install gawk
  fi
  if [ ! -f /usr/local/bin/tfsec ]; then
    brew tap liamg/tfsec
    brew install tfsec
  fi
fi

python3 -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
  if [ -f .git/hooks/pre-commit ]; then
  pre-commit uninstall
  fi
  pre-commit install
fi

DIR=~/.git-template
git config --global init.templateDir ${DIR}
pre-commit init-templatedir -t pre-commit ${DIR}

# GCP auth
#gcloud auth application-default login
