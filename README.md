# Deploy Manager

A lightweight CLI-based deployment management tool for Docker applications.

Deploy Manager provides a simple command-line interface for managing Docker-based applications, including deployment, version management, backup, rollback, and server monitoring.

The goal of this project is to simplify application deployment workflows on Linux servers while keeping the process controlled, traceable, and easy to operate.

---

## Features

### Deployment Pipeline

Deploy Manager uses a structured deployment workflow:

```
Preflight Check
      ↓
Backup
      ↓
Build Docker Image
      ↓
Create Image Version
      ↓
Deploy Container
      ↓
Health Check
      ↓
Commit Deployment
```

Each deployment stage is tracked to make troubleshooting easier.

---

## Main Features

### Application Management

- Register and manage applications
- View installed applications
- Deploy applications
- Check application status
- View deployment history

### Docker Management

- Docker environment information
- Container inspection
- Docker Compose based deployment
- Image version management

### Version Management

- Store deployment versions
- Activate image versions
- Rollback to previous versions

### Backup and Restore

- Create application backups
- Restore previous configurations
- Track deployment changes

### Registry

Deploy Manager maintains a local registry database containing:

- Applications
- Deployments
- Image versions
- Backup records

---

# Installation

## Recommended Installation (Automatic Installer)

The easiest way to install Deploy Manager is using the automated installer.

Run:

```bash
curl -fsSL https://raw.githubusercontent.com/hesami/deploy-manager/main/scripts/install.sh | bash
```

The installer will:

1. Check required dependencies.
2. Verify Git, Python, Docker, and Docker Compose availability.
3. Download or update Deploy Manager.
4. Install the `deploy-manager` command.
5. Initialize the application registry.

After installation, start Deploy Manager:

```bash
deploy-manager menu
```

---

# Manual Installation

If you prefer to install manually:

## 1. Clone Repository

```bash
git clone https://github.com/hesami/deploy-manager.git

cd deploy-manager
```

---

## 2. Install Command

Make the command executable:

```bash
chmod +x deploy-manager
```

Install it globally:

```bash
sudo cp deploy-manager /usr/local/bin/deploy-manager
```

---

## 3. Initialize Registry

Run:

```bash
deploy-manager registry-init
```

---

## 4. Start Application

```bash
deploy-manager menu
```

---

# Requirements

Deploy Manager requires:

- Linux operating system
- Python 3.10+
- Git
- Docker Engine
- Docker Compose Plugin


---

# Using Deploy Manager

## Interactive Menu

The recommended way to use Deploy Manager:

```bash
deploy-manager menu
```

The interactive interface provides access to:

- Application management
- Deployment operations
- System information
- Registry information


---

# Command Line Usage

Deploy Manager also supports direct commands.

## Server Information

```bash
deploy-manager server-info
```

## Docker Information

```bash
deploy-manager docker-info
```

## List Applications

```bash
deploy-manager list
```

## Import Applications

```bash
deploy-manager import
```

## Registry Status

```bash
deploy-manager registry-status
```

---

# Deployment

Deploy an application:

```bash
deploy-manager deploy <application-name>
```

Example:

```bash
deploy-manager deploy my-app
```

The deployment process automatically performs:

- Pre-deployment checks
- Backup preparation
- Docker image build
- Container deployment
- Health verification
- Deployment registration

---

# Version Management

View application versions:

```bash
deploy-manager versions <application-name>
```

Rollback to a previous version:

```bash
deploy-manager rollback-version <application-name> <version>
```

---

# Backup and Restore

Create backup:

```bash
deploy-manager backup <application-name>
```

List backups:

```bash
deploy-manager backups <application-name>
```

Restore backup:

```bash
deploy-manager restore <application-name> <backup-id>
```

---

# Project Structure

```
deploy-manager/
│
├── core/
│   ├── pipeline.py
│   ├── registry.py
│   ├── manager.py
│   ├── docker_reader.py
│   ├── progress.py
│   └── ui.py
│
├── config/
│   └── server.yaml
│
├── registry/
│
├── scripts/
│   └── install.sh
│
└── deploy-manager
```

---

# Updating

For existing installations:

```bash
cd /opt/deploy-manager

git pull

./scripts/install.sh
```

The installer detects existing installations and updates Deploy Manager without requiring a complete reinstall.

---

# Roadmap

Future improvements:

- Web-based management interface
- Remote server management
- Deployment notifications
- Monitoring dashboard
- Role-based access control


---

# License

MIT License


---

# Author

Mehdi Hesami

GitHub:

https://github.com/hesami
