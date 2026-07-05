# python-ai-weekly-report

A Python teaching project for automation agents: Git activity collection, weekly report generation, and email dry-run delivery.

## Run order for class

```powershell
cd python-ai-weekly-report
python -m unittest discover -s tests -v
python -m python_ai_weekly_report.self_check
python -m python_ai_weekly_report.offline_demo
python -m python_ai_weekly_report
```

The first three commands are offline. Email sending is dry-run by default.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Real SMTP

```powershell
$env:WEEKLY_REPORT_EMAIL_DRY_RUN="false"
$env:TO_EMAIL="student@example.com"
$env:FROM_EMAIL="teacher@example.com"
$env:MAIL_PASSWORD="smtp-password"
```
