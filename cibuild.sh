#!/bin/bash
QPAKMAN_URL="https://github.com/bunder/qpakman/archive/refs/tags/v0.67.tar.gz"
FTEQCC_URL="https://www.fteqcc.org/dl/fteqcc_linux64.zip"
ERICW_TOOL_URL="https://github.com/ericwa/ericw-tools/releases/download/2.0.0-alpha6/ericw-tools-2.0.0-alpha6-Linux.zip"

repo_root=$(pwd)

sudo apt-get update
sudo apt-get install -y wget unzip build-essential cmake libz-dev libpng-dev python3

# Install QPAKMAN
QPAKMAN_DIR="$(mktemp -d)"
mkdir -p "$QPAKMAN_DIR"
cd "$QPAKMAN_DIR"
wget -O qpakman.tar.gz "$QPAKMAN_URL"
tar --strip-components 1 -xf qpakman.tar.gz
cmake .
make
export PATH="$QPAKMAN_DIR:$PATH"

# Install FTEQCC
FTEQCC_DIR="$(mktemp -d)"
mkdir -p "$FTEQCC_DIR"
cd "$FTEQCC_DIR"
wget -O fteqcc.zip "$FTEQCC_URL"
unzip fteqcc.zip
ln -s fteqcc64 fteqcc
export PATH="$FTEQCC_DIR:$PATH"

# Install ericw-tools
ERICW_TOOL_DIR="$(mktemp -d)"
mkdir -p "$ERICW_TOOL_DIR"
cd "$ERICW_TOOL_DIR"
wget -O ericw-tools.zip "$ERICW_TOOL_URL"
unzip ericw-tools.zip
export PATH="$ERICW_TOOL_DIR:$PATH"

