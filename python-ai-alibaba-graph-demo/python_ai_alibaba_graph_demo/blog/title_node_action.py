class TitleNodeAction:
    def apply(self, state: dict[str, object]) -> dict[str, object]:
        subject = str(state["subject"])
        return {"title": f"爆款文章标题：{subject}"}

    def __call__(self, state: dict[str, object], config=None) -> dict[str, object]:
        return self.apply(state)
