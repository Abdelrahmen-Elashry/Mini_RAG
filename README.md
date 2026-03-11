# Mini_RAG

This is a modest RAG project supervised by Eng. Abu Bakr Soliman

## Requirments

- Python 3.12

#### Install Python using Miniconda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

2) Create a new environment using the following command:
```bash
$ conda create -n Your-env-name
```
3) Activate the environment:
```bash
$ conda activate Your-env-name
```

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)