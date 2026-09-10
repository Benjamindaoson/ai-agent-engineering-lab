package com.zhouyu;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * JavaClaw 配置属性
 */
@Data
@Component
@ConfigurationProperties(prefix = "javaclaw")
public class JavaClawProperties {

    /**
     * 工作空间目录
     */
    private String workspaceDir = "java-claw/workspace";

    /**
     * 会话存储目录
     */
    private String sessionsDir = "java-claw/sessions";

    /**
     * 模型名称
     */
    private String modelName = "qwen3-max";

    /**
     * API 密钥（也可通过环境变量 DASHSCOPE_API_KEY 设置）
     */
    private String apiKey;

    /**
     * 飞书 APP_ID
     */
    private String feishuAppId;

    /**
     * 飞书 APP_SECRET
     */
    private String feishuAppSecret;

    /**
     * WebSocket 端口
     */
    private int websocketPort = 8887;

    /**
     * 系统提示词前缀
     */
    private String syspromptPrefix = "你是一个有帮助的 AI 助手";

    /**
     * 主会话助手名称
     */
    private String mainAgentName = "网页助手";

    /**
     * 飞书会话助手名称
     */
    private String feishuAgentName = "飞书助手";
}
