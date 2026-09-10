#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CrewAI 活动邀请邮件案例使用的自定义工具。"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from pathlib import Path

from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INVITATION_FILE = BASE_DIR / "invite.txt"


def _read_required_env(name: str) -> str:
    """读取必需环境变量，缺失时给出清晰错误。"""
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"缺少环境变量：{name}")
    return value


def _is_valid_email(address: str) -> bool:
    """进行适合教学案例的基础邮箱格式校验。"""
    _, parsed_address = parseaddr(address)
    return bool(parsed_address and "@" in parsed_address)


@tool("保存活动邀请邮件")
def save_invitation_email(content: str) -> str:
    """将编辑完成的活动邀请邮件保存为本地 invite.txt 文件。"""
    cleaned_content = content.strip()
    if not cleaned_content:
        return "保存失败：邀请邮件内容为空。"

    try:
        INVITATION_FILE.write_text(cleaned_content, encoding="utf-8")
        return f"邀请邮件已保存：{INVITATION_FILE}"
    except OSError as exc:
        return f"保存失败：{exc}"


@tool("发送活动邀请邮件")
def send_invitation_email(recipient_email: str, subject: str) -> str:
    """读取 invite.txt，并通过 SMTP 发送给指定收件人。"""
    recipient_email = recipient_email.strip()
    subject = subject.strip()

    if not _is_valid_email(recipient_email):
        return f"发送失败：收件邮箱格式不正确：{recipient_email}"
    if not subject:
        return "发送失败：邮件主题不能为空。"
    if not INVITATION_FILE.exists():
        return f"发送失败：未找到邀请邮件文件：{INVITATION_FILE}"

    try:
        body = INVITATION_FILE.read_text(encoding="utf-8").strip()
        if not body:
            return "发送失败：邀请邮件文件内容为空。"

        smtp_host = os.getenv("EMAIL_HOST", "smtp.163.com").strip()
        smtp_port = int(os.getenv("EMAIL_PORT", "465"))
        sender_email = _read_required_env("EMAIL_USER")
        sender_password = _read_required_env("EMAIL_PASSWORD")
        sender_name = os.getenv("EMAIL_FROM_NAME", "AI 活动邀请助手").strip()
        dry_run = os.getenv("EMAIL_DRY_RUN", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        if not _is_valid_email(sender_email):
            return f"发送失败：发件邮箱格式不正确：{sender_email}"

        message = EmailMessage()
        message["From"] = formataddr((sender_name, sender_email))
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body, subtype="plain", charset="utf-8")

        if dry_run:
            return (
                "模拟发送成功：EMAIL_DRY_RUN=true，邮件未真正发出。\n"
                f"收件人：{recipient_email}\n"
                f"主题：{subject}\n"
                f"正文文件：{INVITATION_FILE}"
            )

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            smtp_host,
            smtp_port,
            context=context,
            timeout=20,
        ) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(message)

        return f"活动邀请邮件发送成功，收件人：{recipient_email}"

    except ValueError as exc:
        return f"发送失败：{exc}"
    except (OSError, smtplib.SMTPException) as exc:
        return f"发送失败：{type(exc).__name__}: {exc}"
