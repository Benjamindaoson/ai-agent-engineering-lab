class KeywordsExtractNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        prompt = 'Extract keywords and return JSON like {"keywords":["keyword"]}.'
        return {"keywordsExtractResult": self.chat_client.complete(prompt, state["input"])}
