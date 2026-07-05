class EmailService:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send(self, to: str, subject: str, apiKey: str) -> str:
        self.sent.append({"to": to, "subject": subject, "apiKey": apiKey})
        return "已发送"
