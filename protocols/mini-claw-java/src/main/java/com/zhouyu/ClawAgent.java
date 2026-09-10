package com.zhouyu;

import com.zhouyu.memory.MemoryService;
import com.zhouyu.memory.UpdateMemoryTool;
import com.zhouyu.skill.SkillLoader;
import io.agentscope.core.ReActAgent;
import io.agentscope.core.memory.InMemoryMemory;
import io.agentscope.core.memory.Memory;
import io.agentscope.core.memory.autocontext.AutoContextConfig;
import io.agentscope.core.memory.autocontext.AutoContextHook;
import io.agentscope.core.memory.autocontext.AutoContextMemory;
import io.agentscope.core.message.Msg;
import io.agentscope.core.model.DashScopeChatModel;
import io.agentscope.core.model.Model;
import io.agentscope.core.skill.SkillBox;
import io.agentscope.core.tool.Toolkit;
import io.agentscope.core.tool.coding.ShellCommandTool;
import io.agentscope.core.tool.file.ReadFileTool;
import io.agentscope.core.tool.file.WriteFileTool;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

/**
 * ClawAgent - 核心 Agent 实现
 */
@Slf4j
@Component
public class ClawAgent {

    public static final String MAIN_SESSION_ID = "main_session";
    public static final String FEISHU_SESSION_ID = "feishu_session";
    public static final String MAIN_PROMPT_SUFFIX = "\n\n---\n\n交流方式：通过网页与用户交流，用中文交流";
    public static final String FEISHU_PROMPT_SUFFIX = "\n\n---\n\n交流方式：通过飞书与用户交流，用中文交流。";

    private final Map<String, ReActAgent> agentMap = new ConcurrentHashMap<>();
    private final Map<String, Memory> memoryMap = new ConcurrentHashMap<>();
    private DashScopeChatModel chatModel;
    private DashScopeChatModel compressionModel;
    private Toolkit toolkit;
    private final MemoryService memoryService;
    private final SessionStartup sessionStartup;
    private final SkillLoader skillLoader;

    private final JavaClawProperties properties;

    public ClawAgent(JavaClawProperties properties, MemoryService memoryService, SessionStartup sessionStartup, SkillLoader skillLoader) {
        this.properties = properties;
        this.memoryService = memoryService;
        this.sessionStartup = sessionStartup;
        this.skillLoader = skillLoader;
    }

    @PostConstruct
    public void init() {

        // 创建工作空间目录并复制模板文件
        initializeWorkspace();

        // 初始化会话配置（加载 SOUL.md, USER.md 等）
        sessionStartup.initialize();

        // 确保今日笔记存在
        memoryService.ensureTodayNoteExists();

        String workspace = properties.getWorkspaceDir();
        String apiKey = getApiKey();
        String modelName = properties.getModelName();
        String mainAgentName = properties.getMainAgentName();
        String feishuAgentName = properties.getFeishuAgentName();

        // 创建工具集
        toolkit = new Toolkit();
        toolkit.registerTool(new FeishuTools());
        toolkit.registerTool(new ReadFileTool(workspace));
        toolkit.registerTool(new WriteFileTool(workspace));
        toolkit.registerTool(new UpdateMemoryTool(memoryService));
        toolkit.registerTool(new ShellCommandTool(workspace, Set.of("npx", "agent-browser"), null));

        // 创建大模型
        chatModel = DashScopeChatModel.builder()
                .apiKey(apiKey)
                .modelName(modelName)
                .build();

        // 压缩大模型
        compressionModel = DashScopeChatModel.builder()
                .apiKey(apiKey)
                .modelName(modelName)
                .build();

        // 获取基础系统提示词（包含 SOUL、USER、IDENTITY、TOOLS、AGENTS、BOOTSTRAP）
        String baseSysPrompt = sessionStartup.getSystemPrompt();

        // 创建主会话 Agent
        createAgent(MAIN_SESSION_ID, mainAgentName, baseSysPrompt + MAIN_PROMPT_SUFFIX);
        // 并加载历史笔记（包含长期记忆）
        loadNotebooksToAgent(MAIN_SESSION_ID, true);

        // 创建飞书会话 Agent
        createAgent(FEISHU_SESSION_ID, feishuAgentName, baseSysPrompt + FEISHU_PROMPT_SUFFIX);
        // 并加载历史笔记（不包含长期记忆）
        loadNotebooksToAgent(FEISHU_SESSION_ID, false);

        log.info("ClawAgent 初始化完成 - 主会话和飞书会话已就绪");
    }



    private String getApiKey() {
        // 优先从环境变量获取
        String envKey = System.getenv("DASHSCOPE_API_KEY");
        if (envKey != null && !envKey.isEmpty()) {
            return envKey;
        }
        return properties.getApiKey();
    }

    /**
     * 创建新的 Agent 实例
     */
    public void createAgent(String sessionId, String name, String sysPrompt) {
//        InMemoryMemory memory = new InMemoryMemory();

        AutoContextConfig config = AutoContextConfig.builder()
                .msgThreshold(10)  // 触发压缩的消息数量阈值
                .lastKeep(2)
                .build();
        AutoContextMemory memory = new AutoContextMemory(config, compressionModel);
        memoryMap.put(sessionId, memory);

        // 创建工具集和 SkillBox
        SkillBox skillBox = new SkillBox(toolkit);
        // 加载所有可用技能
        skillLoader.loadAllSkills(skillBox);

        ReActAgent agent = ReActAgent.builder()
                .name(name)
                .sysPrompt(sysPrompt)
                .model(chatModel)
                .toolkit(toolkit)
                .skillBox(skillBox)
                .memory(memory)
                .hook(new AutoContextHook())
                .build();

        agentMap.put(sessionId, agent);
        log.info("创建会话：{} ({})", sessionId, name);
    }

    /**
     * 新建会话 - 删除之前的会话并重新创建
     */
    public void newSession(String sessionId) {
        try {
            // 删除内存中的旧会话
            agentMap.remove(sessionId);
            memoryMap.remove(sessionId);

            // 重新创建新的 Agent
            String name = sessionId.equals(MAIN_SESSION_ID) ? properties.getMainAgentName() : properties.getFeishuAgentName();
            String sysprompt = sessionId.equals(MAIN_SESSION_ID) ? MAIN_PROMPT_SUFFIX: FEISHU_PROMPT_SUFFIX;
            createAgent(sessionId, name, sysprompt);

            // 记录到每日笔记
            String sessionName = sessionId.equals(MAIN_SESSION_ID) ? "网页会话" : "飞书会话";
            memoryService.logConversation("系统", sessionName + "已重置，开始新对话");

            // 新会话不加载历史笔记
            log.info("会话已重置：{}", sessionId);
        } catch (Exception e) {
            log.error("新建会话失败：{}", e.getMessage());
        }
    }

    /**
     * 加载今日和昨日笔记到 Agent 记忆
     * @param sessionId 会话 ID
     * @param loadMemory 是否加载长期记忆（MEMORY.md）
     */
    private void loadNotebooksToAgent(String sessionId, boolean loadMemory) {
        ReActAgent agent = agentMap.get(sessionId);
        if (agent == null) {
            return;
        }

        Memory memory = memoryMap.get(sessionId);

        // 加载昨日笔记
        String yesterdayNote = memoryService.readYesterdayNote();
        if (!yesterdayNote.isEmpty()) {
            Msg msg = Msg.builder()
                    .textContent("【昨日对话回顾】\n" + yesterdayNote)
                    .build();
            memory.addMessage(msg);
            log.info("已加载昨日笔记到会话：{}", sessionId);
        }

        // 加载今日笔记
        String todayNote = memoryService.readTodayNote();
        if (!todayNote.isEmpty()) {
            Msg msg = Msg.builder()
                    .textContent("【今日对话记录】\n" + todayNote)
                    .build();
            memory.addMessage(msg);
            log.info("已加载今日笔记到会话：{}", sessionId);
        }

        // 加载长期记忆（仅主会话）
        if (loadMemory) {
            String memoryMd = memoryService.readMemoryMd();
            if (!memoryMd.isEmpty()) {
                Msg msg = Msg.builder()
                        .textContent("【长期记忆】\n" + memoryMd)
                        .build();
                memory.addMessage(msg);
                log.info("已加载长期记忆到会话：{}", sessionId);
            }
        }

        log.info("会话 {} 加载完成，当前消息数：{}", sessionId, memory.getMessages().size());
    }

    /**
     * 调用 Agent 处理用户消息
     */
    public String chat(String sessionId, String userMessage) {
        ReActAgent agent = agentMap.get(sessionId);
        if (agent == null) {
            throw new RuntimeException("Agent不存在，请检查原因");
        }

        try {
            Msg userMsg = Msg.builder()
                    .textContent(userMessage)
                    .build();

            Mono<Msg> mono = agent.call(userMsg);
            Msg response = mono.block();

            if (response != null && response.getTextContent() != null) {
                return response.getTextContent();
            }
            return "抱歉，我暂时无法回答您的问题。";
        } catch (Exception e) {
            log.error("Agent 处理失败：{}", e.getMessage());
            return "抱歉，处理您的请求时出现错误，请稍后重试。";
        }
    }

    /**
     * 主会话聊天（网页对话）
     */
    public String mainChat(String userMessage) {
        String reply = chat(MAIN_SESSION_ID, userMessage);

        // 记录对话到记忆系统
        memoryService.logConversation("用户", userMessage);
        memoryService.logConversation("助手", reply);

        return reply;
    }

    /**
     * 飞书会话聊天
     */
    public String feishuChat(String userMessage) {
        String reply = chat(FEISHU_SESSION_ID, userMessage);

        // 记录对话到记忆系统
        memoryService.logConversation("飞书用户", userMessage);
        memoryService.logConversation("飞书助手", reply);

        return reply;
    }

    /**
     * 初始化工作空间 - 创建目录并复制模板文件
     */
    private void initializeWorkspace() {
        Path workspacePath = Paths.get(properties.getWorkspaceDir());
        Path templateDir = Paths.get("./src/main/resources/template");

        try {
            // 创建工作空间目录
            Files.createDirectories(workspacePath);

            // 需要复制的模板文件（不复制 _CN.md 文件）
            String[] templates = {
                    "SOUL.md",
                    "USER.md",
                    "IDENTITY.md",
                    "TOOLS.md",
                    "BOOTSTRAP.md",
                    "AGENTS.md"
            };

            for (String template : templates) {
                Path sourcePath = templateDir.resolve(template);
                Path destPath = workspacePath.resolve(template);

                // 如果文件不存在，则从 template 目录复制
                if (!Files.exists(destPath) && Files.exists(sourcePath)) {
                    Files.copy(sourcePath, destPath);
                    log.info("已创建模板文件：{}", template);
                }
            }

            // 复制 skills 目录（如果存在）
            Path templateSkillsDir = templateDir.resolve("skills");
            Path workspaceSkillsDir = workspacePath.resolve("skills");
            if (Files.exists(templateSkillsDir)) {
                if (!Files.exists(workspaceSkillsDir)) {
                    skillLoader.initializeSkillRepository(workspaceSkillsDir);
                }

                // 复制所有技能
                Files.list(templateSkillsDir)
                        .filter(Files::isDirectory)
                        .forEach(skillDir -> {
                            String skillName = skillDir.getFileName().toString();
                            Path destSkillDir = workspaceSkillsDir.resolve(skillName);

                            if (!Files.exists(destSkillDir)) {
                                try {
                                    copyDirectory(skillDir, destSkillDir);
                                    log.info("已复制技能：{}", skillName);
                                } catch (IOException e) {
                                    log.error("复制技能失败 [{}]: {}", skillName, e.getMessage());
                                }
                            }
                        });
            }


        } catch (IOException e) {
            log.error("初始化工作空间失败：{}", e.getMessage());
        }
    }

    /**
     * 递归复制目录
     */
    private void copyDirectory(Path source, Path target) throws IOException {
        Files.createDirectories(target);

        Files.list(source).forEach(path -> {
            Path targetPath = target.resolve(source.relativize(path));
            try {
                if (Files.isDirectory(path)) {
                    copyDirectory(path, targetPath);
                } else {
                    Files.copy(path, targetPath);
                }
            } catch (IOException e) {
                log.error("复制文件失败 [{} -> {}]: {}", path, targetPath, e.getMessage());
            }
        });
    }
}