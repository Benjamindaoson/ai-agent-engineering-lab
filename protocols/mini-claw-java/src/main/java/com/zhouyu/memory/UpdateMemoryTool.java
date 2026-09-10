package com.zhouyu.memory;

import io.agentscope.core.tool.Tool;
import io.agentscope.core.tool.ToolParam;
import lombok.extern.slf4j.Slf4j;

/**
 * 更新长期记忆工具
 * 供 Agent 调用，将重要信息记录到长期记忆中
 */
@Slf4j
public class UpdateMemoryTool {

    private final MemoryService memoryService;

    public UpdateMemoryTool(MemoryService memoryService) {
        this.memoryService = memoryService;
    }

    @Tool(description = "当你认为某些信息需要长期保存时调用此工具。适用于：重要事件、用户偏好、关键决策、经验教训、需要记住的事实。不要为临时信息或日常对话调用此工具。")
    public String updateMemory(
            @ToolParam(name = "content", description = "要记录到长期记忆的内容，应该是简洁清晰的陈述") String content,
            @ToolParam(name = "category", description = "记忆类别：event(事件)、preference(偏好)、decision(决策)、lesson(经验教训)、fact(事实)") String category) {

        if (content == null || content.isEmpty()) {
            return "错误：content 参数不能为空";
        }

        if (category == null || category.isEmpty()) {
            category = "event";
        }

        try {
            // 根据类别记录不同类型的记忆
            switch (category.toLowerCase()) {
                case "preference":
                    memoryService.logSignificantEvent("用户偏好：" + content);
                    break;
                case "decision":
                    memoryService.logDecision(content);
                    break;
                case "lesson":
                    memoryService.logLesson(content);
                    break;
                case "fact":
                    memoryService.logSignificantEvent("重要事实：" + content);
                    break;
                default:
                    memoryService.logSignificantEvent(content);
            }

            log.info("已更新长期记忆：[{}] {}", category, content);
            return "记忆已更新：" + content;
        } catch (Exception e) {
            log.error("更新长期记忆失败：{}", e.getMessage());
            return "更新记忆失败：" + e.getMessage();
        }
    }
}
