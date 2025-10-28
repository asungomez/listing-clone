<!-- TOC start -->

- [Listings clone](#listings-clone)
  - [Back-end](#back-end)
    - [Running the application in your host machine](#running-the-application-in-your-host-machine)
      - [Installing Python and creating a virtual environment](#installing-python-and-creating-a-virtual-environment)
      - [Running the application](#running-the-application)
    - [Validating the code](#validating-the-code)
      - [Installing test dependencies](#installing-test-dependencies)
      - [Running the tests](#running-the-tests)
      - [Pre-commit hook](#pre-commit-hook)
    - [Running the application using Docker](#running-the-application-using-docker)
      - [Importing self-signed certificates](#importing-self-signed-certificates)
      - [Spinning up the container](#spinning-up-the-container)
  - [Front-end](#front-end)
    - [Running the application as a Node process](#running-the-application-as-a-node-process)
      - [Installing Node.js](#installing-nodejs)
      - [Installing dependencies](#installing-dependencies)
      - [Running the application](#running-the-application-1)
    - [Running the application using Docker](#running-the-application-using-docker-1)
      - [Importing self-signed certificates](#importing-self-signed-certificates-1)
      - [Spinning up the container](#spinning-up-the-container-1)
  - [End to end tests](#end-to-end-tests)
    - [Setting up the e2e tests](#setting-up-the-e2e-tests)
    - [Running the e2e tests](#running-the-e2e-tests)

<!-- TOC end -->

<!-- TOC --><a name="listings-clone"></a>

# Listings clone

This is a clone of the MyListings project with just the basic functionality implemented, where I try out new ideas and implementations, kind of a living POC of new features.

<!-- TOC --><a name="back-end"></a>

## Back-end

The back-end uses Django and Django REST Framework. It is structured to allow for easy addition of new features and functionalities.

<!-- TOC --><a name="running-the-application-in-your-host-machine"></a>

### Running the application in your host machine

The application can run either on a Docker container or in your host machine. Host machine allows some perks such as VSCode debugging. Docker container is more portable and can be used in a CI/CD pipeline, but for local development adds more overhead.

<!-- TOC --><a name="installing-python-and-creating-a-virtual-environment"></a>

#### Installing Python and creating a virtual environment

This application uses Python 3.13. It is recommended to use a virtual environment to run this application.

You can install python3.13 from the official website: https://www.python.org/downloads/ or using pyenv:

```bash
pyenv install 3.13.1
```

To create a new virtual environment, you can use the following command:

```bash
python3.13 -m venv venv
```

Enable the virtual environment:

```bash
source venv/bin/activate
```

For a freshly created virtual environment, it is recommended to upgrade pip:

```bash
pip install --upgrade pip
```

<!-- TOC --><a name="running-the-application"></a>

#### Running the application

The dependencies for running the application can be installed using the following command:

```bash
pip install -r requirements.txt
```

You need a DB to run the application. You can create a DB container by running:

```bash
docker compose up db -d
```

The app needs an src/.env file like the following:

```env
DEBUG=True
DB_HOST=localhost
DB_NAME=django_course
DB_USER=django_course
DB_PASSWORD=django_course
DJANGO_SECRET_KEY="django-insecure-trkc%c14mv8b%95!spl5n&sg51f7wsyvasx%7ddl$07-f-iynh"
ENCRYPTION_KEY='HqvJK8Ur9q_ZFZlnM-1TOKu7sK4HidccP6NnmMdCEVo='
OKTA_DOMAIN=<Okta domain>
OKTA_CLIENT_ID=<Okta client ID>
OKTA_CLIENT_SECRET=<Okta client secret>
OKTA_LOGIN_REDIRECT=http://localhost:8000/users/login-callback
FRONT_END_URL=http://localhost:5173
```

Then you can run a dev server using:

```bash
cd src
python manage.py runserver 0.0.0.0:8000
```

<!-- TOC --><a name="validating-the-code"></a>

### Validating the code

The dependencies for validations can be installed using:

```bash
pip install -r requirements.dev.txt
```

To run the linter, you can use the following command:

```bash
flake8
```

And to run the static type checker, you can use the following command:

```bash
mypy . --strict
```

<!-- TOC --><a name="installing-test-dependencies"></a>

#### Installing test dependencies

If you want to run the tests, you can install the test dependencies using the following command:

```bash
pip install -r requirements.test.txt
```

<!-- TOC --><a name="running-the-tests"></a>

#### Running the tests

To run the tests, you can use the following command:

```bash
pytest
```

If you want to run a single test case, you can use the -k option:

```bash
pytest -k "test_case_name"
```

<!-- TOC --><a name="pre-commit-hook"></a>

#### Pre-commit hook

To ensure that the code is properly formatted and validated before committing, you can use pre-commit hooks. To install the pre-commit hooks, run:

```bash
pre-commit install
```

<!-- TOC --><a name="running-the-application-using-docker"></a>

### Running the application using Docker

The benefits of using Docker is that the application will run in the exact same environment it would when deployed, making it easier to debug issues. It also doesn't require you to install Python or create a virtual environment. It does not integrate easily with VSCode debugging, though.

<!-- TOC --><a name="importing-self-signed-certificates"></a>

#### Importing self-signed certificates

When working on a company computer, there are self-signed certificates that can make the Docker image build to fail. To prevent this, follow the steps below:

- Enter JLL Self-Service
- Execute the Netskope Developer Tool Configuration
- Create a directory at the in the `back-end` directory called `.certs`
- Copy the certificate file netskope-cert-bundle.pem into `.certs/netskope-cert-bundle.pem`

<!-- TOC --><a name="spinning-up-the-container"></a>

#### Spinning up the container

To spin up the container, you can use the following command:

```bash
docker compose up app
```

<!-- TOC --><a name="front-end"></a>

## Front-end

The front-end uses React, Typescript and Vite.

<!-- TOC --><a name="running-the-application-as-a-node-process"></a>

### Running the application as a Node process

You need to have Node.js installed. It is recommended to use Node.js 22.x.

<!-- TOC --><a name="installing-nodejs"></a>

#### Installing Node.js

Follow the instructions on the official website to install Node.js: https://nodejs.org/en/download/

<!-- TOC --><a name="installing-dependencies"></a>

#### Installing dependencies

To install the dependencies, you can use the following command:

```bash
yarn install
```

#### Setting up environment variables

Create a `.env.local` file in the `front-end` directory with the following content:

```env
VITE_OKTA_DOMAIN=<Okta domain>
VITE_OKTA_CLIENT_ID=<Okta client ID>
VITE_OKTA_LOGIN_REDIRECT=http://localhost:8000/users/login-callback
VITE_API_URL=http://localhost:8000
```

<!-- TOC --><a name="running-the-application-1"></a>

#### Running the application

To run the application, you can use the following command:

```bash
yarn dev
```

The application will be available at http://localhost:5173.

<!-- TOC --><a name="running-the-application-using-docker-1"></a>

### Running the application using Docker

The front-end can also be run using Docker. This is useful for testing the application in a production-like environment.

<!-- TOC --><a name="importing-self-signed-certificates-1"></a>

#### Importing self-signed certificates

When working on a company computer, there are self-signed certificates that can make the Docker image build to fail. To prevent this, follow the steps below:

- Enter JLL Self-Service
- Execute the Netskope Developer Tool Configuration
- Create a directory at the in the `back-end` directory called `.certs`
- Copy the certificate file netskope-cert-bundle.pem into `.certs/netskope-cert-bundle.pem`

<!-- TOC --><a name="spinning-up-the-container-1"></a>

#### Spinning up the container

To spin up the container, you can use the following command:

```bash
docker compose up app
```

<!-- TOC --><a name="end-to-end-tests"></a>

## End to end tests

The e2e tests are written in Playwright and use pytest as the test runner.

<!-- TOC --><a name="setting-up-the-e2e-tests"></a>

### Setting up the e2e tests

You'll need a virtual environment inside the `e2e-tests` directory. You can create it using the following command:

```bash
python3.13 -m venv venv
```

Enable the virtual environment:

```bash
source venv/bin/activate
```

Install the dependencies for the e2e tests using:

```bash
pip install -r requirements.txt
```

And finally, install the Playwright browsers:

```bash
playwright install
```

<!-- TOC --><a name="running-the-e2e-tests"></a>

### Running the e2e tests

To run the e2e tests in the command-line, you can use the following command:

```bash
pytest
```

To open a browser and debug the tests, you can use the `--headed` option:

```bash
pytest --headed
```
