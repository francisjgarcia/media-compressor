# Secrets Configuration

This file contains sensitive configurations necessary for the integration and deployment of the application. Make sure to keep this information secure and do not share it publicly.

## Github Actions

- **`CLOUDFLARE_API_TOKEN`**:
  - **Description**: The API token used to authenticate requests to the Cloudflare API.
  - **Example**: `your-cloudflare-api-token`

- **`DEPLOY_SERVER`**:
  - **Description**: The address of the server where the application will be deployed.
  - **Example**: `deploy.example.com`

- **`SSH_PRIVATE_HOST`**:
  - **Description**: The hostname or IP address of the private SSH server you need to connect to.
  - **Example**: `ssh.example.com`

- **`SSH_PRIVATE_KEY`**:
  - **Description**: The private SSH key used for authentication when accessing remote servers.
  - **Example**: `-----BEGIN OPENSSH PRIVATE KEY----- ... -----END OPENSSH PRIVATE KEY-----`

- **`SSH_PRIVATE_PORT`**:
  - **Description**: The port number on the private SSH server to connect to.
  - **Example**: `22`

- **`SSH_PRIVATE_USER`**:
  - **Description**: The username for authentication on the private SSH server.
  - **Example**: `deploy`

- **`SSH_PROXY_HOST`**:
  - **Description**: The hostname or IP address of the proxy server.
  - **Example**: `proxy.example.com`

- **`SSH_PROXY_PORT`**:
  - **Description**: The port number on the proxy server to connect to.
  - **Example**: `8080`

- **`SSH_PROXY_USER`**:
  - **Description**: The username for authentication on the proxy server.
  - **Example**: `proxyuser`
