<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Money Manager](#money-manager)
  - [Project Overview](#project-overview)
    - [Quality](#quality)
    - [Standards](#standards)
    - [Stats](#stats)
  - [Features](#features)
  - [Usage](#usage)
  - [Tech Stack](#tech-stack)
  - [Tools](#tools)
  - [Installation](#installation)
    - [Webapp](#webapp)
    - [Telegram: Preinstall](#telegram-preinstall)
    - [Telegram: Installation](#telegram-installation)
    - [Testing](#testing)
    - [Code Coverage](#code-coverage)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)
  - [🚀 Future Enhancements](#-future-enhancements)
  - [Contributing](#contributing)
  - [LICENSE](#license)
  - [🤝 Contributors](#-contributors)
  - [Code of Conduct](#code-of-conduct)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Money Manager
<div align="center">
  <img src="docs/logo/logo.png" alt="Project Logo" width="300"/>
</div>

A REST API application for managing expenses. Build your own automation—be it a Telegram bot 🤖, Discord bot, or your own app 📱!

🚨 Spoiler Alert! 🚨 We have built a Telegram bot as a proof of concept! 🤖🎉

<div align="center">
  <img src="http://ForTheBadge.com/images/badges/built-with-love.svg" alt="built_with_love"/>
</div>

---

## Project Overview

https://github.com/user-attachments/assets/91fdf9e0-9489-4e05-ab61-a7599e5463e1

### Quality

[![badge_pytest_status](https://img.shields.io/badge/PyTest-passing-brightgreen?style=plastic&logo=pytest&logoColor=white)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)
[![badge_code_coverage](https://img.shields.io/badge/coverage-92%25-brightgreen?style=plastic)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)
[![badge_total_tests](https://img.shields.io/badge/tests-132-blue?style=plastic&logo=pytest&logoColor=white)](https://github.com/Gunabana/MoneyManager/tree/main/tests)
[![badge_pylint](https://img.shields.io/badge/pylint-10.00-brightgreen?style=plastic)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)
[![badge_black](https://img.shields.io/badge/black_formatter-passing-brightgreen?style=plastic&labelColor=black)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)
[![badge_mypy](https://img.shields.io/badge/mypy-passing-brightgreen?style=plastic)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)
[![badge_bandit](https://img.shields.io/badge/bandit-passing-brightgreen?style=plastic)](https://github.com/Gunabana/MoneyManager/actions/runs/12042743832)

### Standards

![black](https://img.shields.io/badge/code%20style-black-black?style=plastic&)
![license](https://img.shields.io/github/license/Gunabana/MoneyManager?style=plastic&)
![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=plastic&)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14027400.svg)](https://doi.org/10.5281/zenodo.14027400)
<!-- TODO: UPDATED DOI -->

### Stats
![pr_open](https://img.shields.io/github/issues-pr/Gunabana/MoneyManager?style=plastic&)
![pr_close](https://img.shields.io/github/issues-pr-closed/Gunabana/MoneyManager?style=plastic&)
![issue_open](https://img.shields.io/github/issues/Gunabana/MoneyManager.svg?style=plastic&)
![issue_close](https://img.shields.io/github/issues-closed/Gunabana/MoneyManager.svg?style=plastic&)
<!-- TODO: UPDATED # COMMITS -->
![commits_since_last_project](https://img.shields.io/github/commits-since/gitsetgopack/MoneyManager/v2024.f.2-alpha.svg?style=plastic&)
![repo_size](https://img.shields.io/github/repo-size/Gunabana/MoneyManager?style=plastic&)
![forks](https://img.shields.io/github/forks/Gunabana/MoneyManager?style=plastic&)
![stars](https://img.shields.io/github/stars/Gunabana/MoneyManager?style=plastic&)
![downloads](https://img.shields.io/github/downloads/Gunabana/MoneyManager/total?style=plastic&)

#### Tools & Technologies
[![Python](https://img.shields.io/badge/python%203.12-3670A0?logo=python&logoColor=ffdd54)](https://www.python.org/downloads/release/python-3121/)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?logo=github&logoColor=white)](https://github.com/)
[![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)](https://www.linux.org/)
[![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](https://chatgpt.com/)

---

## Features
- **Expense Tracking**: Add, update, and delete expenses. Track expenses by category, date, and account.
- **Data Visualization**: View your expenses over time with customizable charts, including:
  - Monthly and weekly spending trends
  - Categorical expense breakdowns
- **Authentication**: Secure access to your data using token-based authentication.
- **RESTful API**: Access and interact with your financial data programmatically via a FastAPI-powered API.
- **Testing Suite**: Comprehensive tests to ensure stability and reliability across key functionality.
- **Multiple Accounts**: Manage multiple accounts like spending and saving.

## Usage

MoneyManager allows you to take control of your personal finances, providing insights into where your money goes and helping you make informed financial decisions. Whether you're looking to monitor daily spending or analyze broader trends, MoneyManager has the tools you need to stay on top of your finances.

## Tech Stack

- [![Python](https://img.shields.io/badge/Language-Python%203-blue)](https://www.python.org/)
  - The entire application, from managing dependencies to testing, is built using Python 3.

## Tools

- [![Git](https://img.shields.io/badge/Tool-Git-orange)](https://git-scm.com/)
- [![GitHub](https://img.shields.io/badge/Tool-GitHub-lightgrey)](https://github.com/)
- [![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-blue)](https://github.com/features/actions)
- [![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)](https://www.mongodb.com/)
- [![REST API](https://img.shields.io/badge/API-REST-red)](https://restfulapi.net/)
- [![Docker](https://img.shields.io/badge/Containerization-Docker-blue)](https://www.docker.com/)
- [![Telegram](https://img.shields.io/badge/Messaging-Telegram-blue)](https://telegram.org/) - Used as a proof of concept (POC) for messaging integration.

Each tool is an essential part of the development and deployment process, enhancing functionality, reliability, and ease of collaboration.

## Installation

### Webapp
Please refer to the [INSTALL.md](INSTALL.md) file.

### Telegram: Preinstall

You'll need to create a Telegram bot through BotFather:

1. Open the Telegram app (desktop or mobile), search for "BotFather," and click on "Start."
2. Send the following command to BotFather:
```bash
/newbot
```
4. Follow the instructions to:
- Choose a name for your bot.
- Select a username ending with "bot" (required by Telegram).
5. BotFather will confirm your bot's creation and provide an HTTP API access token—save this token for later.

### Telegram: Installation

These instructions guide you through setting up the bot's communication and running it:

1. Clone this repository to your local system.
2. Open a terminal session in the directory where the project was cloned and install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. In the same directory, execute the following bash script to start the Telegram Bot:
  ```bash
  ./run.sh
  ```
  OR
  ```bash
  bash run.sh
  ```
4. When prompted, paste the API token you received from BotFather in step 4 of the pre-requisites.

  A successful run will display the message: "TeleBot: Started polling."

5. In the Telegram app, search for your bot using its username, open it, and type /start or /menu to begin using MoneyManager for expense tracking!

### Testing

This project uses pytest to test all functionalities of the bot:

Run the following command from the project's root directory to execute all unit tests:
  ```bash
  python -m pytest test/
  ```
Currently, the project includes 100+ tests covering all bot functions.

<img width="677" alt="image" src="https://github.com/user-attachments/assets/03d6d77f-7494-424e-bda6-0518ac79b124">

### Code Coverage

Code coverage is assessed as part of each build. Every time new code is pushed, a build runs, and code coverage is computed.

To check code coverage locally:
  ```bash
  coverage run -m pytest test/
  coverage report
  ```

## Configuration

For **users**, no additional configuration is required—just start using MoneyManager!

For **contributors**, we’ve designed the system to be as modular as possible, so that updates to one module won’t impact others. However, there are a few configurable parameters available to help tailor and extend the system:

- Adding and removing categories
- Adjusting graphing options
- Modifying the Telegram bot name, etc.

## Troubleshooting

- **Ensure you have a valid bot token**: You can generate a token by creating a new bot via Telegram’s BotFather.
- **Verify token placement**: Double-check that the token is correctly added to your bot’s code or configuration.
- **Check bot permissions**: Confirm that your bot has the necessary permissions for the intended actions.

Alternatively, you’re welcome to submit a bug report in our repository. Make sure to follow the steps outlined in [CONTRIBUTING.md](CONTRIBUTING.md) for reporting issues.

## 🚀 Future Enhancements

- **External Integrations**: Explore integrations with platforms like Discord, WhatsApp, and Slack to provide seamless notifications and financial management within users' preferred communication apps.
- **UI/Website Development**: Develop a user-friendly web interface to enhance accessibility, offering streamlined access to financial data and resources.
- **Advanced Telegram Bot**: Enhance the current Telegram bot with extensive testing and improvements for greater reliability and comprehensive functionality.
- **Expanded REST Features**:
  - Advanced analytics for deeper insights into financial habits.
  - CSV import/export support for easy data handling.
  - Group expense tracking with features like bill splitting, real-time updates, and integrated payment options.

## Contributing

Thank you for your interest in contributing to MoneyManager! Your contributions are greatly appreciated, and this guide will help you get started. For full details on contributing, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file, which provides comprehensive instructions and guidelines.

## LICENSE

By contributing to MoneyManager, you agree that your contributions will fall under the project’s open-source license. Please take a moment to review and understand the licensing terms before contributing. The specific license details can be found in the [LICENSE](LICENSE) file.

## 🤝 Contributors

Current Team:
- **Brody Bond** ([bbond@ncsu.edu](mailto:bbond@ncsu.edu))
- **Tristan Hall** ([tdhall6@ncsu.edu](mailto:tdhall6@ncsu.edu))
- **Chaitanya Nagulapalli** ([cknagula@ncsu.edu](mailto:cknagula@ncsu.edu))


Prior Team:
- **Abhishek Rao** ([arao23@ncsu.edu](mailto:arao23@ncsu.edu))
- **Astha Bhalodiya** ([abhalod@ncsu.edu](mailto:abhalod@ncsu.edu))
- **Umang Diyora** ([udiyora@ncsu.edu](mailto:udiyora@ncsu.edu))

## Code of Conduct

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to uphold. This ensures that our community remains welcoming and inclusive for everyone.

---

Thank you for using MoneyManager! Follow this page to stay updated on new features and improvements.
