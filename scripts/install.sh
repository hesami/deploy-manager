#!/bin/bash

set -e

APP_NAME="Deploy Manager"
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


echo
echo "================================="
echo "$APP_NAME Installation"
echo "================================="
echo


# Root check

if [ "$EUID" -ne 0 ]; then
    error "Please run installer as root"
fi


# Check Linux

if [ "$(uname)" != "Linux" ]; then
    error "Only Linux systems are supported"
fi


# Check command

check_command()
{
    command_name=$1

    if command -v "$command_name" >/dev/null 2>&1
    then
        version=$($command_name --version 2>/dev/null | head -n 1)
        info "$command_name already installed: $version"
        return 0
    else
        return 1
    fi
}


echo "Checking requirements..."
echo


# Git

if ! check_command git
then
    warn "Git is not installed"

    if command -v apt >/dev/null 2>&1
    then
        apt update
        apt install -y git
    else
        error "Please install Git manually"
    fi
fi


# Python

if ! check_command python3
then
    warn "Python3 is not installed"

    if command -v apt >/dev/null 2>&1
    then
        apt update
        apt install -y python3
    else
        error "Please install Python3 manually"
    fi
fi


# Docker

if ! check_command docker
then
    warn "Docker is not installed"
    warn "Please install Docker before using Deploy Manager"
else

    if docker compose version >/dev/null 2>&1
    then
        info "Docker Compose available"
    else
        warn "Docker Compose plugin not found"
    fi

fi


echo
echo "Preparing Deploy Manager..."
echo


# Clone or update

if [ -d "$INSTALL_DIR/.git" ]
then

    info "Existing installation found"

    cd "$INSTALL_DIR"

    git pull

else

    if [ -d "$INSTALL_DIR" ]
    then
        warn "$INSTALL_DIR exists but is not a git repository"
    else

        git clone \
        "$REPO_URL" \
        "$INSTALL_DIR"

        info "Repository cloned"

    fi

fi


cd "$INSTALL_DIR"


# Permissions

chmod +x deploy-manager


# Install global command

if [ -L "$BIN_PATH" ] || [ -f "$BIN_PATH" ]
then

    rm -f "$BIN_PATH"

fi


ln -s \
"$INSTALL_DIR/deploy-manager" \
"$BIN_PATH"


info "Command installed: deploy-manager"


echo
echo "================================="
echo "Installation completed"
echo "================================="
echo

echo "Location:"
echo "$INSTALL_DIR"

echo

echo "Run:"
echo

echo "deploy-manager --help"

echo
