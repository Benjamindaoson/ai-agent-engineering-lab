package com.zhouyu.memory;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * 记忆服务 - 管理每日笔记和长期记忆
 * 作者：IT周瑜
 * 公众号：IT周瑜
 * 微信号：it_zhouyu
 */
@Slf4j
@Service
public class MemoryService {

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter DATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final Path workspacePath;
    private final Path memoryDir;
    private final Path memoryMdPath;

    public MemoryService() {
        this.workspacePath = Paths.get("./workspace");
        this.memoryDir = workspacePath.resolve("memory");
        this.memoryMdPath = workspacePath.resolve("MEMORY.md");

        // 确保目录存在
        try {
            Files.createDirectories(memoryDir);
        } catch (IOException e) {
            log.error("创建记忆目录失败：{}", e.getMessage());
        }
    }

    /**
     * 获取今日日期字符串
     */
    public String getTodayDate() {
        return LocalDate.now().format(DATE_FORMATTER);
    }

    /**
     * 获取昨日日期字符串
     */
    public String getYesterdayDate() {
        return LocalDate.now().minusDays(1).format(DATE_FORMATTER);
    }

    /**
     * 获取今日笔记文件路径
     */
    public Path getTodayNotePath() {
        return memoryDir.resolve(getTodayDate() + ".md");
    }

    /**
     * 获取指定日期的笔记文件路径
     */
    public Path getNotePath(String date) {
        return memoryDir.resolve(date + ".md");
    }

    /**
     * 获取长期记忆文件路径
     */
    public Path getMemoryMdPath() {
        return memoryMdPath;
    }

    /**
     * 读取今日笔记
     */
    public String readTodayNote() {
        Path path = getTodayNotePath();
        if (!Files.exists(path)) {
            return "";
        }
        try {
            return Files.readString(path);
        } catch (IOException e) {
            log.error("读取今日笔记失败：{}", e.getMessage());
            return "";
        }
    }

    /**
     * 读取昨日笔记
     */
    public String readYesterdayNote() {
        Path path = getNotePath(getYesterdayDate());
        if (!Files.exists(path)) {
            return "";
        }
        try {
            return Files.readString(path);
        } catch (IOException e) {
            log.error("读取昨日笔记失败：{}", e.getMessage());
            return "";
        }
    }

    /**
     * 读取长期记忆
     */
    public String readMemoryMd() {
        if (!Files.exists(memoryMdPath)) {
            return "";
        }
        try {
            return Files.readString(memoryMdPath);
        } catch (IOException e) {
            log.error("读取长期记忆失败：{}", e.getMessage());
            return "";
        }
    }

    /**
     * 追加内容到今日笔记
     */
    public void appendToTodayNote(String content) {
        try {
            Path todayPath = getTodayNotePath();

            // 如果文件不存在，先创建并写入标题
            if (!Files.exists(todayPath)) {
                String header = "# " + getTodayDate() + "\n\n";
                Files.writeString(todayPath, header, StandardOpenOption.CREATE);
            }

            // 追加内容
            String timestampedContent = String.format("[%s] %s\n",
                LocalDateTime.now().format(DATETIME_FORMATTER), content);
            Files.writeString(todayPath, timestampedContent, StandardOpenOption.APPEND);

            log.info("已写入今日笔记：{}", content.substring(0, Math.min(30, content.length())));
        } catch (IOException e) {
            log.error("写入今日笔记失败：{}", e.getMessage());
        }
    }

    /**
     * 追加内容到长期记忆
     */
    public void appendToMemoryMd(String content) {
        try {
            if (!Files.exists(memoryMdPath)) {
                String header = "# 长期记忆\n\n最后更新：" +
                    LocalDateTime.now().format(DATETIME_FORMATTER) + "\n\n";
                Files.writeString(memoryMdPath, header, StandardOpenOption.CREATE);
            }

            String timestampedContent = String.format("[%s] %s\n",
                LocalDateTime.now().format(DATETIME_FORMATTER), content);
            Files.writeString(memoryMdPath, timestampedContent, StandardOpenOption.APPEND);

            log.info("已写入长期记忆：{}", content.substring(0, Math.min(30, content.length())));
        } catch (IOException e) {
            log.error("写入长期记忆失败：{}", e.getMessage());
        }
    }

    /**
     * 更新长期记忆（覆盖整个文件）
     */
    public void updateMemoryMd(String content) {
        try {
            String fullContent = "# 长期记忆\n\n最后更新：" +
                LocalDateTime.now().format(DATETIME_FORMATTER) + "\n\n" + content;
            Files.writeString(memoryMdPath, fullContent, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            log.info("已更新长期记忆");
        } catch (IOException e) {
            log.error("更新长期记忆失败：{}", e.getMessage());
        }
    }

    /**
     * 记录对话到今日笔记
     */
    public void logConversation(String role, String content) {
        String log = String.format("### %s\n%s\n", role, content);
        appendToTodayNote(log);
    }

    /**
     * 记录重要事件到长期记忆
     */
    public void logSignificantEvent(String event) {
        appendToMemoryMd("## 事件\n" + event);
    }

    /**
     * 记录决策到长期记忆
     */
    public void logDecision(String decision) {
        appendToMemoryMd("## 决策\n" + decision);
    }

    /**
     * 记录经验教训到长期记忆
     */
    public void logLesson(String lesson) {
        appendToMemoryMd("## 经验教训\n" + lesson);
    }

    /**
     * 获取最近 N 天的笔记
     */
    public List<String> getRecentNotes(int days) {
        return LocalDate.now().minusDays(days)
                .datesUntil(LocalDate.now().plusDays(1))
                .map(date -> date.format(DATE_FORMATTER))
                .map(this::readNote)
                .filter(content -> !content.isEmpty())
                .toList();
    }

    /**
     * 读取指定日期的笔记
     */
    public String readNote(String date) {
        Path path = getNotePath(date);
        if (!Files.exists(path)) {
            return "";
        }
        try {
            return Files.readString(path);
        } catch (IOException e) {
            log.error("读取笔记失败 [{}]：{}", date, e.getMessage());
            return "";
        }
    }

    /**
     * 检查是否需要创建新日期的笔记
     */
    public void ensureTodayNoteExists() {
        Path todayPath = getTodayNotePath();
        if (!Files.exists(todayPath)) {
            try {
                String header = "# " + getTodayDate() + "\n\n";
                Files.writeString(todayPath, header, StandardOpenOption.CREATE);
                log.info("已创建今日笔记文件：{}", todayPath);
            } catch (IOException e) {
                log.error("创建今日笔记失败：{}", e.getMessage());
            }
        }
    }
}