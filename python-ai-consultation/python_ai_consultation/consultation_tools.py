class ConsultationTools:
    def __init__(self):
        self.registrations: list[str] = []

    def register(self, department_name: str) -> str:
        self.registrations.append(department_name)
        return "挂号成功，请等待医生处理"
