Last updated: 2025-05-01

# Docker files 

- [./chainlit_dev.Dockerfile](./chainlit_dev.Dockerfile)

    Base image for an environmnet container based on [../chatbot_reqs.txt](../chatbot_reqs.txt), requirements ossibly a bit bloated

- [./chatbot_deploy.Dockerfile](./chatbot_deploy.Dockerfile)

    App container image, based on the environemnt image

# Local deployment

- from within the cloned repo, the app can be started using [../docker_call](../docker_call), if the necessary environment variables are set correctly.

# CI/CD

## Google Cloud Build / Run

- Google Cloud Build is configured in the github applications of the repo and builds [./chatbot_deploy.Dockerfile](./chatbot_deploy.Dockerfile)
on each push to `main`

- Two versions are deployed using Google Cloud Run : one using Gemini and another using Azure OpenAI, both currently suspended due to incurred costs beyond the free tier

- The following secrets are set as environment variables in the Google Cloud Run configuration:

    - LANGFUSE_{AZURE/GEMINI}_SECRET_KEY
    - LANGFUSE_{AZURE/GEMINI}_PUBLIC_KEY
    - SERVICE1_PROVIDER (azure or gemini)
    - OPENAI_API_KEY
    - 0PENROUTER_API_KEY

https://www.perplexity.ai/search/how-to-deploy-a-chainlit-app-o-1_qhFwFxTsO0VFOksS67.Q

https://www.perplexity.ai/search/make-a-minimal-viable-example-zL9hudIbRZCFEjMqaJhiww

## Azure Pipelines / Container Apps, Services

exact Azure Service to be used TBD

https://www.perplexity.ai/search/what-would-be-de-equivalent-of-IBve3EyyTs.n5K_BY65.xw

- Azure Pipelines is granted access to the repo
- cannot build at the moment due to quota issues
