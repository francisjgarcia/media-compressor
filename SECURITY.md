# Security Policy

## Supported Versions

We actively support the following versions of the project:

Version | Supported
-|-
≥ v1.0.0 | ✅

## Reporting a Vulnerability

If you discover a security vulnerability, we encourage you to notify us as soon as possible. We will work with you to quickly address the issue. To report a vulnerability, please follow these steps:

1. **Contact Us:**
   - Please report any potential vulnerabilities via email to [contacto@francisjgarcia.es](mailto:contacto@francisjgarcia.es).
   - Include as much information as possible to help us understand the severity and scope of the issue.

2. **Details Required:**
   - A detailed description of the vulnerability.
   - Steps to reproduce the vulnerability.
   - If applicable, proof of concept code (if it's a technical issue).
   - Any potential security implications you foresee.

3. **Response Time:**
   - We will respond within 3 business days to confirm that we have received your report and are assessing the issue.
   - If the issue is verified, we will aim to provide a fix or mitigation as quickly as possible. We will keep you informed of the progress.

4. **Disclosure Policy:**
   - Please do not disclose the details of the vulnerability publicly until we have had a reasonable time to address it.
   - Once the issue is resolved, we may credit you for the discovery, with your permission.

## Security Best Practices

For users deploying this project, we recommend the following best practices to maintain security:

- **Keep Dependencies Updated**: Ensure that all dependencies (listed in `requirements.txt`) are regularly updated to the latest secure versions.

- **Using Secrets in GitHub Actions**: When working with sensitive data, such as API keys, tokens, or passwords, it is crucial not to expose these secrets in the codebase or configuration files. Instead, GitHub provides a secure way to manage secrets using **GitHub Actions Secrets**.


## Additional Resources

- [Common Vulnerabilities and Exposures (CVE) List](https://cve.mitre.org/)
- [OWASP Top Ten Security Risks](https://owasp.org/www-project-top-ten/)

