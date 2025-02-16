#!/bin/env bash

# TODO: Add the commands to install the Bril environment tools.
# Make sure your script installs Deno, Flit, and the Bril tools.
# Ensure the script works on any machine and sets up the PATH correctly.

# Ubuntu
apt update
apt install curl -y
apt install git -y
apt install zip -y
apt install python3-pip -y

cd /tmp
curl -fsSL https://deno.land/install.sh | sh
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

git clone https://github.com/sampsyo/bril
cd bril

deno install -g brili.ts

pip install --user flit
cd bril-txt
FLIT_ROOT_INSTALL=1 flit install --symlink --user
cd ..
cd brench
FLIT_ROOT_INSTALL=1 flit install --symlink --user
cd ..

deno install -g --allow-env --allow-read ts2bril.ts
deno install -g brilck.ts

pip install --user turnt


cat >> $HOME/.bashrc << 'STOP'
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
STOP


