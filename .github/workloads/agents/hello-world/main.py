"""AgentCore HTTP Hello World (no LLM required)."""
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()


def hello(payload: dict) -> dict:
    return {"message": f"Hello, {payload.get('name', 'world')}!"}


@app.entrypoint
def invoke(payload: dict) -> dict:
    return hello(payload)


if __name__ == "__main__":
    app.run()
