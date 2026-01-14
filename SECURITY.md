# Security Policy

## Supported Versions

We release security patches for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security tab](https://github.com/seanbarlow/doit/security/advisories)
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email**
   - Send details to: [sbarlow@barlowtech.com](mailto:sbarlow@barlowtech.com)
   - Use subject line: `[SECURITY] doit vulnerability report`

### What to Include

Please include as much of the following information as possible:

- Type of vulnerability (e.g., command injection, path traversal, etc.)
- Full paths of affected source files
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact assessment (what could an attacker do?)
- Any suggested fixes (optional)

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Within 7 days with assessment
- **Resolution Target**: Within 30 days for critical issues

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Assessment**: We'll evaluate the severity and impact
3. **Communication**: We'll keep you informed of our progress
4. **Fix**: We'll develop and test a fix
5. **Disclosure**: We'll coordinate disclosure timing with you
6. **Credit**: We'll credit you in the security advisory (unless you prefer anonymity)

## Security Considerations for Do-It

### What Do-It Does

Do-It is a CLI tool that:

- Reads and writes files in the project directory
- Copies templates to initialize projects
- Interacts with the file system within the working directory

### Potential Security Areas

#### File System Operations

- Do-It operates within the current working directory
- Template files are copied from the package installation
- No network requests are made by default

#### User Input

- Command arguments are processed by the CLI
- File paths are validated before operations

#### Dependencies

- We monitor dependencies for known vulnerabilities
- Updates are applied promptly when security issues are identified

## Security Best Practices for Users

1. **Review Templates**: Inspect template files before using in production
2. **Keep Updated**: Use the latest version for security fixes
3. **Verify Source**: Install only from official PyPI package
4. **Check Permissions**: Review file permissions after initialization

## Out of Scope

The following are generally not considered security vulnerabilities:

- Issues requiring physical access to the user's machine
- Social engineering attacks
- Vulnerabilities in dependencies (report to upstream)
- Issues in unsupported versions
- Theoretical issues without demonstrated impact

## Security Updates

Security updates are released as patch versions (e.g., 0.1.1 -> 0.1.2) and announced via:

- GitHub Security Advisories
- Release notes in CHANGELOG.md
- PyPI release notifications

## Acknowledgments

We thank the security researchers who have responsibly disclosed vulnerabilities:

*No vulnerabilities have been reported yet.*

---

Thank you for helping keep Do-It and its users safe!
