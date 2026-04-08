# ads-service

A service responsible for managing and serving advertisements within the platform.

## Overview

`ads-service` handles the lifecycle of ads, including creation, retrieval, targeting, and delivery. It is designed to integrate with other platform services and exposes a clean API for ad management operations.

## Getting Started

### Prerequisites

- Git
- A compatible runtime environment for your chosen stack (see project dependencies)

### Installation

```bash
git clone https://github.com/port-gh-app-dev/ads-service.git
cd ads-service
```

Install dependencies and follow any additional setup steps specific to your environment.

### Running the Service

Refer to the project's configuration files and environment variables to start the service locally.

## CI/CD

This repository uses GitHub Actions for continuous integration. Workflows run automatically on every `push` and `pull_request`.

| Workflow | Description |
|---|---|
| `ci_workflow_1_1pz5` | Builds and runs tests |
| `ci_workflow_2_hnkp` | Builds and runs tests |

### Workflow Details

- **Trigger:** `push`, `pull_request`
- **Runner:** `ubuntu-latest`
- **Steps:** Checkout → Build/script → Simulate tests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'feat: add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

This project is maintained by [port-gh-app-dev](https://github.com/port-gh-app-dev).
