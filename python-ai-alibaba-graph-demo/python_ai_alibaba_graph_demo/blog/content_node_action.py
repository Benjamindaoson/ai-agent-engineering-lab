class ContentNodeAction:
    def apply(self, state: dict[str, object]) -> dict[str, object]:
        title = str(state["title"])
        return {"content": f"content:爆款文章：围绕 {title} 写一段简短内容"}

    def __call__(self, state: dict[str, object], config=None) -> dict[str, object]:
        return self.apply(state)
