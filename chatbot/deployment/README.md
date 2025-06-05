Last updated: 2025-06-05

# Docker files 

- [./python_uv_node.Dockerfile](./python_uv_node.Dockerfile)

    Customisation of the UI required forking [`chainlit`](https://github.com/kantundpeterpan/chainlit), this container contains the base environment for building directly from the fork repo (`(p)npm`)

- [./chainlit_dev.Dockerfile](./chainlit_dev.Dockerfile)

    Based on the `python_uv_node` image,  for an environment container based on [../chatbot_reqs.txt](../chatbot_reqs.txt), requirements possibly a bit bloated

- [./chatbot_deploy.Dockerfile](./chatbot_deploy.Dockerfile)

    App container image, based on the environment image

# Local deployment

- from within the cloned repo, the app can be started using [../docker_call](../docker_call), if the necessary environment variables are set correctly.

# CI/CD

## Google Cloud Build / Run

- Google Cloud Build is configured in the github applications of the repo and builds [./chatbot_deploy.Dockerfile](./chatbot_deploy.Dockerfile)
on each push to `main`

- Currently a single version is running, using the `generativelanguage` API of Google Cloud
- Model: `gemini-flash-2.0`
- The following secrets are set as environment variables in the Google Cloud Run configuration:

    - LANGFUSE_{AZURE/GEMINI}_SECRET_KEY
    - LANGFUSE_{AZURE/GEMINI}_PUBLIC_KEY
    - SERVICE1_PROVIDER (azure or gemini)
    - OPENAI_API_KEY
    - OPENROUTER_API_KEY
    - GOOGLE_API_KEY
    - GOOGLE_PROJECT_ID
    - GOOGLE_PRIVATE_KEY
    - GOOGLE_CLIENT_EMAIL
    - GOOGLE_BUCKET_NAME

https://www.perplexity.ai/search/how-to-deploy-a-chainlit-app-o-1_qhFwFxTsO0VFOksS67.Q

https://www.perplexity.ai/search/make-a-minimal-viable-example-zL9hudIbRZCFEjMqaJhiww

## Azure Pipelines / Container Apps, Services

exact Azure Service to be used TBD

https://www.perplexity.ai/search/what-would-be-de-equivalent-of-IBve3EyyTs.n5K_BY65.xw

- Azure Pipelines is granted access to the repo
- cannot build at the moment due to quota issues
