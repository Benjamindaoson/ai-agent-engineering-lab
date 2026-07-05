from dataclasses import dataclass, field

from .column_info import ColumnInfo


@dataclass
class TableInfo:
    table_name: str
    table_comment: str = ""
    column_info_list: list[ColumnInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "TableInfo":
        return cls(
            str(data.get("tableName") or data.get("table_name") or ""),
            str(data.get("tableComment") or data.get("table_comment") or ""),
            [ColumnInfo.from_dict(item) for item in data.get("columnInfoList", [])],
        )

    def to_dict(self) -> dict:
        return {
            "tableName": self.table_name,
            "tableComment": self.table_comment,
            "columnInfoList": [column.to_dict() for column in self.column_info_list],
        }
