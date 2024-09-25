# Python Template Repository

This repository serves as a base template for Python projects, providing an organized folder structure, integration with Docker, Ansible, Terraform, Helm, and a fully configured CI/CD pipeline using GitHub Actions.

## Table of Contents

- [Python Template Repository](#python-template-repository)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Cloning the Repository](#cloning-the-repository)
    - [Local Development](#local-development)
    - [Running with Docker](#running-with-docker)
  - [Docker](#docker)
    - [Dockerfile](#dockerfile)
    - [Docker Compose](#docker-compose)
  - [GitHub Actions](#github-actions)
    - [CI/CD Pipeline](#cicd-pipeline)
    - [Deploy to server](#deploy-to-server)
    - [Remove deploy from server](#remove-deploy-from-server)
  - [Secrets Configuration](#secrets-configuration)
  - [Documentation](#documentation)
  - [Source Code](#source-code)
  - [Tests](#tests)
  - [Issue Templates](#issue-templates)
  - [File details](#file-details)
    - [.dockerignore](#dockerignore)
    - [.editorconfig](#editorconfig)
    - [.gitignore](#gitignore)
    - [AUTHORS](#authors)
    - [CHANGELOG.md (\*)](#changelogmd-)
    - [CODE\_OF\_CONDUCT.md](#code_of_conductmd)
    - [CONTRIBUTING.md](#contributingmd)
    - [GOVERNANCE.md](#governancemd)
    - [LICENSE](#license)
    - [README.md](#readmemd)
    - [SECURITY.md](#securitymd)
    - [SUPPORT.md](#supportmd)
    - [.github/dependabot.yml](#githubdependabotyml)
    - [.github/pull\_request\_template.md](#githubpull_request_templatemd)
    - [.github/release.yml](#githubreleaseyml)
  - [Additional Information](#additional-information)
    - [Hardcoded Values](#hardcoded-values)
---

## Project Structure

```plaintext
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── 0_bug_report.yml                # Template for reporting bugs or issues
│   │   ├── 1_feature_request.yml           # Template for requesting new features
│   │   ├── 2_improvement_request.yml       # Template for suggesting improvements
│   │   ├── 3_performance_issue.yml         # Template for reporting performance issues
│   │   ├── 4_refactor_request.yml          # Template for requesting code refactoring
│   │   ├── 5_documentation_update.yml      # Template for suggesting documentation updates
│   │   ├── 6_security_vulnerability.yml    # Template for reporting security vulnerabilities
│   │   ├── 7_tests_requests.yml            # Template for requesting new tests
│   │   ├── 8_question.yml                  # Template for asking questions
│   │   └── config.yml                      # Configuration file for issue templates
│   ├── workflows/
│   │   ├── cicd.yml                        # CI/CD pipeline configuration using GitHub Actions
│   │   ├── deploy.yml                      # Deploy to server workflow
│   │   └── remove-deploy.yml               # Remove deploy from server workflow
│   ├── dependabot.yml                      # Dependabot configuration for dependency updates
│   └── release.yml                         # Automatic release generation on GitHub
├── docker/
│   ├── .env.example                        # Example environment variables file for Docker
│   ├── Dockerfile                          # Dockerfile to build the project image
│   ├── Dockerfile.local                    # Dockerfile to run the project locally
│   └── compose.yml                         # Docker Compose file to define services and networks
├── docs/
│   ├── SECRETS.md                          # Documentation about secrets needed for deployment
│   └── STYLEGUIDE.md                       # Guidelines for code style and formatting
├── src/
│   ├── main.py                             # Main script of the project
│   └── requirements.txt                    # Python dependencies file
├── .dockerignore                           # File to exclude files from Docker context
├── .editorconfig                           # Configuration for code formatting in compatible editors
├── .gitignore                              # File to exclude files and directories from version control
├── AUTHORS                                 # List of authors and contributors to the project
├── CHANGELOG.md (*)                        # History of changes and versions of the project (Created after first main deploy)
├── CODE_OF_CONDUCT.md                      # Code of conduct for project contributors
├── CONTRIBUTING.md                         # Guidelines for contributing to the project
├── GOVERNANCE.md                           # Project governance model and decision-making process
├── LICENSE                                 # Information about the project's license
├── README.md                               # Main documentation of the project
├── SECURITY.md                             # Documentation about project security
└── SUPPORT.md                              # Information on how to get support for the project
```

---

## Prerequisites
Before you begin, make sure you have the following installed in your environment:

- git (obligatory)
- docker (optional, if you want to run the project with Docker)
- docker-compose (optional, if you want to run the project with Docker)
- python (optional, if you want to run the project locally)

## Usage

### Cloning the Repository

To use this template to create a new project, you can clone the repository using the following steps:

1. Click on the "Use this template" button at the top of the repository.
2. Enter the repository name, description, and visibility.
3. Click on the "Create repository from template" button.
4. Clone the newly created repository to your local machine.

```bash
git clone
```

5. Navigate to the cloned repository directory.

```bash
cd <repository-name>
```

6. Start working on your new project!

### Local Development

To develop and test the project locally, follow these steps:

1. Install the dependencies:

```bash
pip install -r src/requirements.txt
```

2. Run the main script:

```bash
python src/main.py
```

### Running with Docker

You can use Docker and Docker Compose to run the project in a container. Ensure Docker and Docker Compose are installed.

1. Navigate to the docker directory, rename the `.env.example` file to `.env`, and adjust the environment variables as needed.

```bash
# Environment variables for Docker Compose
COMPOSE_PROJECT_NAME=template
COMPOSE_FILE=compose.yml

# Port on which the application will be accessible
APP_PORT=5000

# Environment variables for the application
MY_VAR1=Hello, World!
```
- **COMPOSE_PROJECT_NAME**: Name of the Docker Compose project.
- **COMPOSE_FILE**: Docker Compose configuration file.
- **APP_PORT**: Port on which the application will be accessible.
- **MY_VAR1**: Environment variable for the application.

2. Build and run the services with Docker Compose:

```bash
compose up -d --build
```
This will build the container image according to the Dockerfile and start the services defined in `compose.yml`.

## Docker

### Dockerfile

The `Dockerfile` in the `docker` directory is used to build the Docker image for the project. The file contains instructions to create the image, including the base image, dependencies, and commands to run the application.

The `Dockerfile.local` is used to run the project locally with Docker. This file is used to build the image and run the container locally.

### Docker Compose

The `compose.yml` file in the `docker` directory defines the services and networks for the project using Docker Compose. This file specifies the container image, environment variables, ports, and volumes needed to run the application.

## GitHub Actions

### CI/CD Pipeline

This repository includes a fully automated CI/CD pipeline using `cicd.yml` GitHub Actions. The pipeline is configured to run on each push to the main or development branches and performs the following tasks:

1. **Setup**: Generates the necessary variables for use in the subsequent tasks.
2. **Build**: Builds the Docker image and saves it locally.
3. **Test**: Runs the tests for the application.
4. **Scan**: Scans the Docker image for vulnerabilities using Trivy.
5. **Push**: Pushes the Docker image to the GitHub Container Registry.
6. **Release**: Automatically generates the changelog and creates a new release on GitHub if deploying to `main`.
7. **Merge**: Merges changes from `main` into the `development` branch if a direct push to `main` occurs.
8. **Deploy**: Deploys the application to remote servers using SSH if deploying to `main`.
9. **Register**: Register DNS record in Cloudflare.

### Deploy to server

To deploy an specific version of the application to a remote server. You can use the `deploy.yml` workflow. This workflow is triggered by a manual event. Only the `main` branch and tags are allowed to trigger this workflow.

1. **Setup**: Generates the necessary variables for use in the subsequent tasks.
2. **Deploy**: Deploys the application to remote servers using SSH.
3. **Register**: Register DNS record in Cloudflare.

### Remove deploy from server

To remove the application from the remote server, you can use the `remove-deploy.yml` workflow. This workflow is triggered by a manual event. Only the `main` branch is allowed to trigger this workflow.

1. **Setup**: Generates the necessary variables for use in the subsequent tasks.
2. **Remove deploy**: Removes the application from remote servers using SSH.
3. **Remove record**: Removes DNS record in Cloudflare.

## Secrets Configuration

To properly enable the pipeline and deployment, you need to configure the following secrets in GitHub:

- **CLOUDFLARE_API_TOKEN**: API token used to authenticate requests to the Cloudflare API.
- **DEPLOY_SERVER**: Address of the server where the application will be deployed.
- **SSH_PRIVATE_HOST**: Hostname or IP address of the private SSH server.
- **SSH_PRIVATE_KEY**: Private key for SSH authentication on remote servers.
- **SSH_PRIVATE_PORT**: SSH connection port.
- **SSH_PRIVATE_USER**: SSH user for the server.
- **SSH_PROXY_HOST**: Hostname or IP address of the proxy server.
- **SSH_PROXY_PORT**: Proxy port.
- **SSH_PROXY_USER**: Proxy user.

More details about these secrets can be found in the [SECRETS.md](docs/SECRETS.md) file.

## Documentation

The `docs` directory contains additional documentation for the project:

**SECRETS.md**: Provides information on the secrets needed for deployment, including the required environment variables and their configuration.

**STYLEGUIDE.md**: Contains guidelines for code style and formatting, including best practices for writing clean, readable code.

## Source Code

The `src` directory contains the project's source code:

**main.py**: The main script that runs the application. This is where the project's entry point is located.

**requirements.txt**: File listing the Python dependencies needed for the project. This file is used to install the required libraries via pip.

## Tests

The `tests` directory contains the project's test scripts. These tests can be run using the following command:

```bash
pytest src/tests/
```

The tests are automatically run as part of the CI/CD pipeline to ensure the project's functionality is maintained.

## Issue Templates

The `.github/ISSUE_TEMPLATE` directory contains templates for creating new issues in the repository. These templates provide a structured format for submitting bug reports, feature requests, and other types of issues. The templates help ensure that important information is included in each issue, making it easier for contributors to understand and address the problem.

- **0_bug_report.yml**: Template for reporting bugs or issues in the project.
- **1_feature_request.yml**: Template for requesting new features or enhancements.
- **2_improvement_request.yml**: Template for suggesting improvements or optimizations.
- **3_performance_issue.yml**: Template for reporting performance-related issues.
- **4_refactor_request.yml**: Template for requesting code refactoring or cleanup.
- **5_documentation_update.yml**: Template for suggesting updates or improvements to the documentation.
- **6_security_vulnerability.yml**: Template for reporting security vulnerabilities.
- **7_tests_requests.yml**: Template for requesting new tests or test coverage.
- **8_question.yml**: Template for asking questions or seeking clarification.
- **config.yml**: Configuration file for issue templates.

These templates help streamline the issue creation process and ensure that important details are included in each issue.

## File details

### [.dockerignore](.dockerignore)
Specifies files and directories to exclude from the Docker build context. This prevents unnecessary files from being copied into the Docker container, reducing image size and improving build efficiency.

### [.editorconfig](.editorconfig)
Configures code formatting rules for compatible editors. Defines standards such as indentation size, use of spaces versus tabs, and other style guidelines to ensure consistency throughout the project.

### [.gitignore](.gitignore)
Lists files and directories to be ignored by Git. Includes configurations to exclude automatically generated files, environment dependencies, and other content that should not be tracked in the repository.

### [AUTHORS](AUTHORS)
Lists the authors and contributors to the project. Provides credit to individuals who have contributed to the codebase and helps maintain a record of project contributors.

### [CHANGELOG.md](CHANGELOG.md) (*)
Records the project's change history and version updates. Documents all significant changes and modifications made over time. This file is created after the first main deploy.

### [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
Defines the code of conduct for project contributors. It sets expectations for behavior and communication within the community, fostering an inclusive and respectful environment for all participants.

### [CONTRIBUTING.md](CONTRIBUTING.md)
Guidelines for contributing to the project. Outlines the process for submitting issues, feature requests, and code changes, as well as the project's coding standards and best practices.

### [GOVERNANCE.md](GOVERNANCE.md)
Describes the project's governance model and decision-making process. Outlines how decisions are made, who has authority over the project, and how the community can participate in project governance.

### [LICENSE](LICENSE)
Outlines the licensing terms for the project. Specifies the conditions under which users can use, modify, and distribute the source code. It’s important to review and understand the terms provided in this file.

### [README.md](README.md)
Offers an overview of the project, including development and usage instructions, configuration details, and information about the CI/CD pipeline. Serves as the main reference document for anyone working with the repository.

### [SECURITY.md](SECURITY.md)
Provides guidelines for maintaining project security. Includes information on reporting security vulnerabilities, best practices for code security, and procedures for handling security issues. Ensures contributors and users understand how to address and report security concerns.

### [SUPPORT.md](UPPORT.md)
Contains information on how to get support for the project. Includes details on where to find help, how to report issues, and how to contact the project maintainers. Helps users and contributors access the resources they need to resolve problems and get assistance.

### [.github/dependabot.yml](.github/dependabot.yml)
Configures Dependabot for the repository. Dependabot automatically creates pull requests to update library and tool versions, helping to keep the project secure and up-to-date with the latest dependencies.

### [.github/pull_request_template.md](.github/pull_request_template.md)
Provides a template for creating pull requests in the repository. The template includes sections for describing the changes, marking the type of change, and checking off a list of items to ensure the pull request meets the project's guidelines.

### [.github/release.yml](.github/release.yml)
Automatically generates a new release on GitHub when changes are merged into the `main` branch. The release includes a changelog of the changes made since the last release, providing a summary of new features, bug fixes or improvements.

## Additional Information

### Hardcoded Values

This repository template contains several hardcoded values that should be updated when cloning the repository for a new project. Please review the following sections and modify accordingly:
1. **Author Information**:
    - Located in:
      - `AUTHORS`: Update the author's name.
      - `LICENSE`: Change the author's name to reflect the new project.

2. **Email Address**:
    - Located in:
      - `AUTHORS`: Update the author's email address.
      - `CODE_OF_CONDUCT.md`: Replace the email address in the enforcement section.
      - `SECURITY.md`: Update the contact email for reporting vulnerabilities.
      - `SUPPORT.md`: Modify the email address in the contact section.

3. **GitHub Repository name**:
    - Found in:
      - `SUPPORT.md`: Update the link to point to the new repository.
      - `CONTRIBUTING.md`: Modify the URL to reflect the new repository.
      - `docker/compose.yml`: Change the docker service name, container name and image build.

4. **Username**:
    - Found in:
      - `GOVERNANCE.md`: Change the username as needed.
      - `.github/ISSUE_TEMPLATE/*.yml`: Change the username on all yaml templates.

5. **Date**:
    - Located in:
      - `LICENSE`: Updates the year to current date.

Make sure to search for these instances throughout the repository to ensure proper configuration.
