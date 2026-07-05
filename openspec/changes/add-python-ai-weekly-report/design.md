## Design

`python-ai-weekly-report` mirrors the Java module:

- `git_tool.py`: reads local `git config user.name` and weekly `git log`.
- `email_tool.py`: converts Markdown report content to simple HTML and sends email, dry-run by default.
- `weekly_report_controller.py`: exposes an `sse(chat_id, message)` generator that yields `{"content": token}` chunks like the Java SSE endpoint.
- `weekly_report_application.py`: wires `ChatClient`, `GitTool`, `EmailTool`, and `WeeklyReportController`.

The Python controller keeps the Java flow: project path message -> Git tool -> model-generated Markdown report -> memory by chat id -> human confirmation -> email tool.

## Verification

Tests create a temporary Git repository, verify commit-log filtering, verify dry-run email HTML output, and verify the generate-then-confirm controller flow.
