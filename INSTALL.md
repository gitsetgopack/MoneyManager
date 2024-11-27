<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [MoneyManager Installation Guide](#moneymanager-installation-guide)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
  - [Available Make Commands](#available-make-commands)
  - [Additional Information](#additional-information)
  - [Troubleshooting](#troubleshooting)
  - [Running Tests](#running-tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# MoneyManager Installation Guide

Welcome to the **MoneyManager** project! This guide will help you set up the environment and install dependencies to get started.

## Prerequisites

Before beginning the installation, please ensure you have the following installed:

- **Python** (version 3.12.3 or higher)
- **Git** (to clone the repository)
- **Docker** (for running MongoDB in a Docker container during testing)

## Installation Steps

0. **Please Note**

    The Makefile assumes that python3 can be executed with the name of python.

1. **Clone the Repository**

   Begin by cloning the repository to your local machine:

   ```bash
   git clone https://github.com/gitsetgopack/MoneyManager.git
   cd MoneyManager
   ```

2. **Optional: Setup & Running a Virtual Environment**
  While optional, if you are developing MoneyManager, it is recommended to run
  it in a virtual environment. This can be done be done by running the following
  commands.

    #### Setup the Virtual Environment:
    ```bash
      python -m venv myvenv
    ```

    #### Run the Virtual Environment on Mac/Linux:
    ```bash
    source myvenv/bin/activate
    ```

    #### Run the Virtual Environment on Windows:
    ```
    myvenv\Scripts\activate
    ```

3. **Install Dependencies**
  Run the following command to install all required dependencies:

   ```bash
   make install
   ```

   This command will:
   - Upgrade `pip` to the latest version.
   - Install the required Python packages as specified in the `requirements.txt`.
   - Install pre-commit hooks.

4. **Create .env file**

    To properly run this system, you will need to set up an ENV file. To do this, create a `.env` file at the root directory of this project. Inside, the contents should contain:
    ```
    MONGO_URI=
    TOKEN_SECRET_KEY=
    TOKEN_ALGORITHM=
    API_BIND_HOST=
    API_BIND_PORT=
    TELEGRAM_BOT_TOKEN=
    TELEGRAM_BOT_API_BASE_URL=
    DISCORD_TOKEN=
    ```
    * A TOKEN_SECRET_KEY can be generated on Linux using `openssl rand -base64 64`
    * A TOKEN_ALGORITHM of `HS256` is recommended
    * By default, the API host and port will be 0.0.0.0 and 9999 respectively
    * See the README.md regarding the TOKEN and URL for the telegram bot
    * Please follow Discord's instructions on how to setup and obtain a Discord bot token.

5. **Starting Application**

    Please reference Available Make Commands below. If you simply want to run the webapp on a Linux system (or WSL), run the two following commands at the MoneyManager's root directory: 1) `make run` in one terminal and 2) `make start_database` in a second terminal. The webapp will be viewable at http://127.0.0.1:9999/ by default. For testing, especially when developing bots that require
    a non-locally hosted site, there are a few options as listed <a href="https://pinggy.io/blog/best_ngrok_alternatives/">here</a>.



## Available Make Commands

Here are the commands available in the `Makefile` to help you work with the project:

- **help**: Show this help message, displaying all available commands.
  ```bash
  make help
  ```

- **install**: Install dependencies.
  ```bash
  make install
  ```

-  **run**: Runs the application.
    ```bash
    make run
    ```

    You may need to run `export PYTHONPATH=/path/to/MoneyManager/:$PYTHONPATH` if you get an error stating the API doesn't exist.
#export PYTHONPATH=/mnt/c/Users/Trist/OneDrive/Documents/GitHub/MoneyManager:$PYTHONPATH
- **start_database**: Setup and run the non-testing (live) database.
  ```bash
  make start_database
  ```

- **stop_database**: Stop the non-testing (live) database.
  ``` bash
  make stop_database
  ```

- **clear_database**: Clear the non-testing (live) database.
    ``` bash
  make clear_database
  ```

- **test**: Start a MongoDB Docker container, run tests, and clean up after the tests.
  ```bash
  make test
  ```

  This command will:
  - Start a MongoDB container to simulate a database for testing.
  - Run all tests using `pytest`.
  - Stop and remove the MongoDB container after testing is complete.

  You may need to run `export PYTHONPATH=/path/to/MoneyManager/:$PYTHONPATH` if you get an error stating the API doesn't exist.

- **fix**: Run code formatting on the `api` directory using `black` and `isort`.
  ```bash
  make fix
  ```

- **clean**: Clean up Python bytecode files, cache, and MongoDB Docker containers.
  ```bash
  make clean
  ```

  This will:
  - Stop and remove the `mongo-test` Docker container if it exists.
  - Remove Python bytecode files (`.pyc`) and caches like `__pycache__`, `.pytest_cache`, and `.mypy_cache`.

- **no_verify_push**: Stage, commit, and push changes with `--no-verify` to skip pre-commit hooks.
  ```bash
  make no_verify_push
  ```

  This command allows you to quickly commit and push changes without running verification checks. It will prompt you for a commit message.

## Additional Information

- **Makefile**: The `Makefile` includes useful commands to set up, run, and test the project. You can inspect it for more details on available commands.
- **Python Environment**: It’s recommended to create a virtual environment for this project to keep dependencies isolated. Run `python -m venv venv` before `make install` if needed.

## Troubleshooting

- **Python Compatibility**: Ensure Python is in your system’s `PATH` and meets the required version.
- **Dependency Issues**: If you encounter issues, check the `requirements.txt` file for compatibility, or re-run `make install` after activating a virtual environment.
- **Docker Issues**: Make sure Docker is installed and running properly before executing commands that require a MongoDB container.

## Running Tests

To run the tests, ensure Docker is running and then use:

```bash
make test
```

This command will automatically set up the necessary database for testing purposes.

---

Feel free to reach out if you have any issues setting up **MoneyManager**!
