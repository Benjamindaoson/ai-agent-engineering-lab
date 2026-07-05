from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnInfo:
    column_name: str
    column_type: str
    column_comment: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "ColumnInfo":
        return cls(
            str(data.get("columnName") or data.get("column_name") or ""),
            str(data.get("columnType") or data.get("column_type") or ""),
            str(data.get("columnComment") or data.get("column_comment") or ""),
        )

    def to_dict(self) -> dict:
        return {"columnName": self.column_name, "columnType": self.column_type, "columnComment": self.column_comment}
