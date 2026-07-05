from datetime import datetime

from .alarm_request import AlarmRequest


class ZhouyuTools:
    def __init__(self):
        self.alarms: list[AlarmRequest] = []
        self.saved_code: list[str] = []

    def get_current_date_time(self) -> datetime:
        return datetime.now()

    def set_alarm(self, alarm_request: AlarmRequest) -> str:
        self.alarms.append(alarm_request)
        address = alarm_request.address or ""
        return f"地址：{address}，闹钟时间为：{alarm_request.time}"

    def save_code(self, code: str) -> str:
        self.saved_code.append(code)
        return f"保存代码：{code}"
