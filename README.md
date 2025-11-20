# git-cicd-demo

![SparkAI Logo](sparkai_logo.jpg)

This is a demo repo to showcase:

✅ Python Flask app  
✅ Unit tests with pytest  
✅ CI/CD with GitHub Actions  
✅ Environment-specific deployments:
- DEV
- UAT
- PROD

## Quick Start

## Install dependencies:

`pip install -r requirements.txt`

## Run locally:

`python app/routes.py`

## Run tests:
`pytest`


## Branch Strategy

- **develop** → development changes
- **release/** → UAT builds
- **main** → production deployments

## CI/CD Pipeline

Each environment deploys automatically when you push to:

- develop → DEV
- release/* → UAT
- main → PROD

## Code Owners

See `.github/CODEOWNERS`

## PR Template

See `.github/PULL_REQUEST_TEMPLATE.md`

---

**Created by SparkAI Solutions**



