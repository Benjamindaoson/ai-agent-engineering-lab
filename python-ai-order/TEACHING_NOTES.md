# 教学注释：python-ai-order

这一关讲业务 Agent。它不只是聊天，而是必须遵守订单业务规则。

## 这一关学什么

- 商品搜索
- 创建订单
- 支付确认
- 退款规则
- 业务异常
- 客服知识库查询

## 先看哪些文件

1. `python_ai_order/service/order_service.py`：订单业务规则。
2. `python_ai_order/tool/order_tool.py`：给 Agent 调用的业务工具。
3. `python_ai_order/controller/order_controller.py`：接口层如何包装业务结果。
4. `python_ai_order/parser/order_document_parser.py`：售后知识如何被解析。
5. `python_ai_order/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

重点讲“业务 Agent 的核心是守规则”。比如没有确认不能支付，待付款订单不能退款。
