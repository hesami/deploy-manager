#!/bin/bash

set -e

INSTALL_DIR="/opt/deploy-manager"
BIN_PATH="/usr/local/bin/deploy-manager"
REPO_URL="https://github.com/hesami/deploy-manager.git"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

info()
{
    echo -e "${GREEN}✓${NC} $1"
}

warn()
{
    echo -e "${YELLOW}!${NC} $1"
}

error()
{
    echo -e "${RED}✗${NC} $1"
    exit 1
}


if [ "$EUID" -ne 0 ]; then
    error "Run installer as root"
fi


echo
echo "================================="
echo "Deploy Manager Installer"
echo "================================="
echo


check_command()
{
    if command -v $1 >/dev/null 2>&1
    then
        info "$1 already installed"
    else
        return 1
    fi
}


check_command git || error "Git is required"

check_command python3 || error "Python3 is required"

check_command docker || error "Docker is required"


if docker compose version >/dev/null 2>&1
then
    info "Docker Compose available"
else
    error "Docker Compose is required"
fi


echo
echo "Installing Deploy Manager..."
echo


if [ -d "$INSTALL_DIR/.git" ]
then

    info "Existing installation found"

    cd "$INSTALL_DIR"

    git pull

else

    git clone \
    "$REPO_URL" \
    "$INSTALL_DIR"

    info "Repository cloned"

fi


cd "$INSTALL_DIR"


chmod +x deploy-manager


if [ -f "$BIN_PATH" ] || [ -L "$BIN_PATH" ]
then
    rm -f "$BIN_PATH"
fi


ln -s "$INSTALL_DIR/deploy-manager" "$BIN_PATH"


info "Command installed"


python3 deploy-manager registry-init


echo
echo "================================="
echo "Installation Completed"
echo "================================="
echo

echo "Run:"
echo

echo "deploy-manager menu"
echo

deploy-manager menu
