import json

from python_ai_data.dto import TableInfo


class TableInfoRecallNode:
    def __init__(self, table_infos: list[TableInfo]):
        self.table_infos = table_infos

    def apply(self, state: dict) -> dict:
        keywords = json.loads(state["keywordsExtractResult"]).get("keywords", [])
        lowered = [str(keyword).lower() for keyword in keywords]
        result = []
        for table in self.table_infos:
            haystack = " ".join(
                [table.table_name, table.table_comment]
                + [column.column_name + " " + column.column_comment for column in table.column_info_list]
            ).lower()
            if any(keyword in haystack for keyword in lowered):
                result.append(table)
        return {"tableInfoRecallResult": result or self.table_infos}
