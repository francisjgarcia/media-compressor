# Media Compressor

In this project, we aim to create a media compressor that can compress media files (series and movies) using the x264 encoder. The project will be able to compress media files stored on a Samba share and save the compressed files back to the share.

Our objective is to create a simple and efficient media compressor that can be used to automate the compression process for a lot of media files. The project will be designed to be easy to use and configure.

The project will be developed using Python and Docker, with GitHub Actions for CI/CD to build and test the application.

## Table of Contents

- [Media Compressor](#media-compressor)
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
  - [Documentation](#documentation)
  - [Source Code](#source-code)
  - [Tests](#tests)
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
│   │   └── cicd.yml                        # CI/CD pipeline configuration using GitHub Actions
│   ├── dependabot.yml                      # Dependabot configuration for dependency updates
│   └── release.yml                         # Automatic release generation on GitHub
├── docker/
│   ├── .env.example                        # Example environment variables file for Docker
│   ├── Dockerfile                          # Dockerfile to build the project image
│   ├── Dockerfile.local                    # Dockerfile to run the project locally
│   └── compose.yml                         # Docker Compose file to define services and networks
├── docs/
│   └── STYLEGUIDE.md                       # Guidelines for code style and formatting
├── src/
│   ├── .env.example                        # Example environment variables file for Docker
│   ├── main.py                             # Main script of the project
│   └── requirements.txt                    # Python dependencies file
├── tests/ (*)                              # Directory for test scripts (actual no tests, will be added in the future)
├── .dockerignore                           # File to exclude files from Docker context
├── .editorconfig                           # Configuration for code formatting in compatible editors
├── .gitignore                              # File to exclude files and directories from version control
├── AUTHORS                                 # List of authors and contributors to the project
├── CHANGELOG.md                            # History of changes and versions of the project
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
python src/main.py <parameters>
```

### Running with Docker

You can use Docker and Docker Compose to run the project in a container. Ensure Docker and Docker Compose are installed.

1. Navigate to the src directory, rename the `.env.example` file to `.env`, and adjust the environment variables as needed.

```bash
SMB_USERNAME=""       # Username for the SMB share
SMB_PASSWORD=""       # Password for the SMB share
SMB_INPUT_SERIES=""   # Path to the input series folder on the samba share
SMB_OUTPUT_SERIES=""  # Path to the output series folder on the samba share
SMB_INPUT_MOVIES=""   # Path to the input movies folder on the samba share
SMB_OUTPUT_MOVIES=""  # Path to the output movies folder on the samba share
CRF=""                # Constant Rate Factor (CRF) for the x264 encoder (0-51)
PRESET=""             # Preset for the x264 encoder (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
```

2. Build and run the services with Docker Compose:

```bash
compose up -d --build
```
This will build the container image according to the Dockerfile and start the services defined in `compose.yml`.

3. Access to the container and run the main script:

```bash
docker exec -it media-compressor sh
python main.py <parameters>
```

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

## Documentation

The `docs` directory contains additional documentation for the project:

**STYLEGUIDE.md**: Contains guidelines for code style and formatting, including best practices for writing clean, readable code.

## Source Code

The `src` directory contains the project's source code:

**main.py**: The main script that runs the application. This is where the project's entry point is located.

**requirements.txt**: File listing the Python dependencies needed for the project. This file is used to install the required libraries via pip.

**.env.example**: Example environment variables file for Docker. This file should be renamed to `.env` and adjusted with the necessary values.

## Tests

The `tests` directory contains the project's test scripts. These tests can be run using the following command:

```bash
pytest src/tests/
```
> [!NOTE]
> Actually there are no tests but they will be added in the future.

The tests are automatically run as part of the CI/CD pipeline to ensure the project's functionality is maintained.
