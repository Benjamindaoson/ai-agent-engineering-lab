import html
import os
import smtplib
from dataclasses import dataclass
from datetime import date
from email.mime.text import MIMEText


@dataclass
class EmailSendResult:
    to_email: str
    subject: str
    html_content: str
    dry_run: bool


class EmailTool:
    def __init__(
        self,
        to_email: str | None = None,
        from_email: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        password: str | None = None,
        dry_run: bool | None = None,
    ):
        self.to_email = to_email or os.getenv("TO_EMAIL", "")
        self.from_email = from_email or os.getenv("FROM_EMAIL") or os.getenv("MAIL_USERNAME", "")
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.qq.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "465"))
        self.password = password or os.getenv("MAIL_PASSWORD", "")
        self.dry_run = dry_run if dry_run is not None else os.getenv("WEEKLY_REPORT_EMAIL_DRY_RUN", "true").lower() != "false"
        self.sent_messages: list[EmailSendResult] = []

    def send_email(self, report_content: str) -> EmailSendResult:
        subject = f"{date.today().isoformat()}周报"
        html_content = markdown_to_html(report_content)
        result = EmailSendResult(self.to_email, subject, html_content, self.dry_run)
        self.sent_messages.append(result)
        if self.dry_run:
            return result
        if not self.to_email or not self.from_email or not self.password:
            raise RuntimeError("SMTP sending requires TO_EMAIL, FROM_EMAIL/MAIL_USERNAME, and MAIL_PASSWORD.")
        message = MIMEText(html_content, "html", "utf-8")
        message["From"] = self.from_email
        message["To"] = self.to_email
        message["Subject"] = subject
        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
            smtp.login(self.from_email, self.password)
            smtp.send_message(message)
        return result


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_list = False
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        else:
            html_lines.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)
