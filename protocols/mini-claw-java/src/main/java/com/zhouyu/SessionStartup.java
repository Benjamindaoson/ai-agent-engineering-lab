package com.zhouyu;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 会话启动配置服务 - 加载 SOUL、USER、IDENTITY 等配置文件
 */
@Slf4j
@Component
public class SessionStartup {

    private final Path workspacePath;
    private final Path soulPath;
    private final Path userPath;
    private final Path identityPath;
    private final Path toolsPath;
    private final Path bootstrapPath;
    private final Path agentsPath;

    private String soulContent;
    private String userContent;
    private String identityContent;
    private String toolsContent;
    private String agentsContent;
    private String bootstrapContent;

    public SessionStartup() {
        this.workspacePath = Paths.get("./workspace");
        this.soulPath = workspacePath.resolve("SOUL.md");
        this.userPath = workspacePath.resolve("USER.md");
        this.identityPath = workspacePath.resolve("IDENTITY.md");
        this.toolsPath = workspacePath.resolve("TOOLS.md");
        this.bootstrapPath = workspacePath.resolve("BOOTSTRAP.md");
        this.agentsPath = workspacePath.resolve("AGENTS.md");

        // 工作空间目录已在 ClawAgent.initializeWorkspace() 中创建
    }

    /**
     * 初始化配置 - 启动时调用
     */
    public void initialize() {
        log.info("开始加载会话配置...");

        // 检查是否有 BOOTSTRAP.md，如果有则需要引导流程
        boolean needsBootstrap = Files.exists(bootstrapPath);

        // 加载所有配置文件
        loadSoul();
        loadUser();
        loadIdentity();
        loadTools();
        loadAgents();
        loadBootstrap();

        if (needsBootstrap) {
            log.info("检测到 BOOTSTRAP.md，需要执行引导流程");
        } else {
            log.info("会话配置加载完成");
        }
    }

    /**
     * 加载 SOUL.md
     */
    public void loadSoul() {
        if (Files.exists(soulPath)) {
            try {
                soulContent = Files.readString(soulPath);
                log.info("已加载 SOUL.md");
            } catch (IOException e) {
                log.error("加载 SOUL.md 失败：{}", e.getMessage());
                soulContent = "";
            }
        } else {
            log.error("SOUL.md 不存在，请检查模板文件是否正确复制");
            soulContent = "";
        }
    }

    /**
     * 加载 USER.md
     */
    public void loadUser() {
        if (Files.exists(userPath)) {
            try {
                userContent = Files.readString(userPath);
                log.info("已加载 USER.md");
            } catch (IOException e) {
                log.error("加载 USER.md 失败：{}", e.getMessage());
                userContent = "";
            }
        } else {
            log.error("USER.md 不存在，请检查模板文件是否正确复制");
            userContent = "";
        }
    }

    /**
     * 加载 IDENTITY.md
     */
    public void loadIdentity() {
        if (Files.exists(identityPath)) {
            try {
                identityContent = Files.readString(identityPath);
                log.info("已加载 IDENTITY.md");
            } catch (IOException e) {
                log.error("加载 IDENTITY.md 失败：{}", e.getMessage());
                identityContent = "";
            }
        } else {
            log.error("IDENTITY.md 不存在，请检查模板文件是否正确复制");
            identityContent = "";
        }
    }

    /**
     * 加载 TOOLS.md
     */
    public void loadTools() {
        if (Files.exists(toolsPath)) {
            try {
                toolsContent = Files.readString(toolsPath);
                log.info("已加载 TOOLS.md");
            } catch (IOException e) {
                log.error("加载 TOOLS.md 失败：{}", e.getMessage());
                toolsContent = "";
            }
        } else {
            log.error("TOOLS.md 不存在，请检查模板文件是否正确复制");
            toolsContent = "";
        }
    }

    /**
     * 加载 AGENTS.md - 工作空间行为规范
     */
    public void loadAgents() {
        if (Files.exists(agentsPath)) {
            try {
                agentsContent = Files.readString(agentsPath);
                log.info("已加载 AGENTS.md");
            } catch (IOException e) {
                log.error("加载 AGENTS.md 失败：{}", e.getMessage());
                agentsContent = "";
            }
        } else {
            log.error("AGENTS.md 不存在，请检查模板文件是否正确复制");
            agentsContent = "";
        }
    }

    /**
     * 加载 BOOTSTRAP.md - 引导文件（如果存在）
     */
    public void loadBootstrap() {
        if (Files.exists(bootstrapPath)) {
            try {
                bootstrapContent = Files.readString(bootstrapPath);
                log.info("已加载 BOOTSTRAP.md");
            } catch (IOException e) {
                log.error("加载 BOOTSTRAP.md 失败：{}", e.getMessage());
                bootstrapContent = "";
            }
        } else {
            bootstrapContent = null;
        }
    }

    /**
     * 删除 BOOTSTRAP.md（引导完成后调用）
     */
    public void deleteBootstrap() {
        try {
            if (Files.exists(bootstrapPath)) {
                Files.delete(bootstrapPath);
                log.info("已删除 BOOTSTRAP.md - 引导流程完成");
            }
        } catch (IOException e) {
            log.error("删除 BOOTSTRAP.md 失败：{}", e.getMessage());
        }
    }

    /**
     * 获取系统提示词（包含所有配置文件的整合）
     */
    public String getSystemPrompt() {
        StringBuilder prompt = new StringBuilder();

        // 添加 AGENTS.md - 工作空间行为规范
        prompt.append("# 工作空间规范\n\n");
        prompt.append(agentsContent);
        prompt.append("\n\n---\n\n");

        // 如果有 BOOTSTRAP.md，优先添加引导内容
        if (bootstrapContent != null && !bootstrapContent.isEmpty()) {
            prompt.append("# 引导任务\n\n");
            prompt.append(bootstrapContent);
            prompt.append("\n\n---\n\n");
        }

        // 添加 SOUL.md - 核心信条
        prompt.append("# 核心信条\n\n");
        prompt.append(soulContent);
        prompt.append("\n\n---\n\n");

        // 添加 USER.md - 用户信息
        prompt.append("# 用户信息\n\n");
        prompt.append(userContent);
        prompt.append("\n\n---\n\n");

        // 添加 IDENTITY.md - 身份定义
        prompt.append("# 身份定义\n\n");
        prompt.append(identityContent);
        prompt.append("\n\n---\n\n");

        // 添加 TOOLS.md - 本地工具配置
        prompt.append("# 本地工具配置\n\n");
        prompt.append(toolsContent);

        return prompt.toString();
    }
}
