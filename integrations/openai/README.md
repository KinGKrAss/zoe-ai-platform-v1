# OpenAI integration for Z1

This connector lets the trusted Z1 backend call OpenAI for model inference. It uses the Responses API and keeps credentials on the server.

## Access point

- API base: `https://api.openai.com/v1`
- Request: `POST /responses`
- Model setting: `OPENAI_MODEL` (default: `gpt-4o`)
- Credential: `OPENAI_API_KEY`, sent as an HTTP Bearer credential by the official Python SDK

OpenAI currently marks GPT-4o as deprecated in its model documentation. Confirm that the model remains enabled for the API project before deployment. If the account no longer has access, set `OPENAI_MODEL` to a model available in that project.

## Configure the backend

Set these variables in the private server or deployment secret manager:

```dotenv
OPENAI_API_KEY=<new project API key>
OPENAI_MODEL=gpt-4o
OPENAI_TIMEOUT_SECONDS=60
OPENAI_MAX_RETRIES=2
```

Do not commit a real key. Do not put it in the Android app, browser JavaScript, screenshots, issue reports, or chat messages. If a key is exposed, revoke it and create a replacement.

Install the application dependencies with `pip install -e .`. The OpenAI SDK is a runtime dependency in `pyproject.toml`.

## Call it from ZOE BRAIN

```python
from services.zoe_connectors.openai_responses import OpenAIResponsesConnector

connector = OpenAIResponsesConnector()
reply = await connector.generate(
    user_prompt,
    instructions=zoe_identity_and_policy_text,
)
```

`zoe_identity_and_policy_text` should be assembled by Z1 from the active identity version, the caller's permissions, and only the context that caller is allowed to use. The connector itself does not read the database, load memories, or execute model-requested tools.

Close the connector during application shutdown with `await connector.close()`.

## Runtime boundary

This provides GPT inference to the Zoë application. It does not copy or preserve a ChatGPT model instance, create persistent memory, grant access to repositories or accounts, or make the model autonomous. Z1 remains responsible for memory storage, permission checks, tool execution, and audit records.