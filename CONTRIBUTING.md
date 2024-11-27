<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Contributing to Money Manager](#contributing-to-money-manager)
  - [Getting Started](#getting-started)
    - [1. Fork the Repository](#1-fork-the-repository)
    - [2. Clone Your Fork](#2-clone-your-fork)
    - [3. Set Up Environment](#3-set-up-environment)
    - [4. Create a Branch](#4-create-a-branch)
    - [5. Make Changes](#5-make-changes)
    - [6. Run Formatters and Linters](#6-run-formatters-and-linters)
    - [7. Commit Changes](#7-commit-changes)
    - [8. Push Changes](#8-push-changes)
    - [9. Submit a Pull Request](#9-submit-a-pull-request)
  - [Code of Conduct](#code-of-conduct)
  - [Guidelines](#guidelines)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Contributing to Money Manager

Thank you for considering contributing to **MoneyManager**! We welcome all types of contributions, whether you're fixing a bug, adding a feature, improving documentation, or suggesting an idea.

## Getting Started

To get started with contributing to this project, please follow these guidelines.

### 1. Fork the Repository

Start by forking the main repository on GitHub. This creates a copy of the repository under your GitHub account.

- Navigate to [MoneyManager GitHub Repo](https://github.com/gitsetgopack/MoneyManager)
- Click the **Fork** button in the top-right corner.

### 2. Clone Your Fork

Once you've forked the repository, clone your fork locally:

```bash
git clone https://github.com/your-username/MoneyManager.git
cd MoneyManager
```

Replace `your-username` with your GitHub username.

### 3. Set Up Environment

To set up the environment, use the following command to install dependencies:

```bash
make install
```

This will install all necessary Python packages and set up the pre-commit hooks.

### 4. Create a Branch

It's good practice to create a new branch for each change. This makes it easier to submit pull requests.

```bash
git checkout -b feature/new-feature
```

Replace `feature/new-feature` with a meaningful name for your branch.

### 5. Make Changes

Make your changes to the codebase. Ensure you write unit tests if applicable.

To run tests locally:

```bash
make test
```

### 6. Run Formatters and Linters

Before committing, make sure your code is formatted correctly:

```bash
make fix
```

This command will run `black` and `isort` to ensure the code style is consistent.

### 7. Commit Changes

Commit your changes with a descriptive commit message:

```bash
git add .
git commit -m "Added a new feature to manage categories"
```

### 8. Push Changes

Push your changes to your forked repository:

```bash
git push origin feature/new-feature
```

### 9. Submit a Pull Request

Once you've pushed your changes, go to the main repository on GitHub and submit a pull request (PR) from your forked repository.

- Navigate to your fork on GitHub.
- Click **Compare & Pull Request**.
- Provide a clear and concise description of your changes in the PR description.

## Code of Conduct

We expect all contributors to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please respect others' work and efforts, and let's collaborate effectively to improve **MoneyManager** together.

## Guidelines

- Write clear, concise commit messages.
- Test your changes thoroughly.
- Include tests for any new functionality.
- If you have any questions, please open an issue or contact the maintainers.

Thank you for your contributions and for making **Money Manager** better!
