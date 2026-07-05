from .deep_research_application import DeepResearchWorkflow


class DeepResearchController:
    def __init__(self, workflow: DeepResearchWorkflow):
        self.workflow = workflow

    def stream(self, input_text: str):
        result = self.workflow.run(input_text)
        for chunk in result.splitlines(keepends=True):
            yield chunk

    def sse(self, input_text: str):
        for chunk in self.stream(input_text):
            yield {"content": chunk}
