package com.zhouyu.skill;

import io.agentscope.core.skill.AgentSkill;
import io.agentscope.core.skill.SkillBox;
import io.agentscope.core.skill.repository.AgentSkillRepository;
import io.agentscope.core.skill.repository.FileSystemSkillRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * 技能加载器 - 从 workspace/skills 目录加载技能
 */
@Slf4j
@Service
public class SkillLoader {

    private Path skillsDir;
    private AgentSkillRepository skillRepository;

    /**
     * 初始化技能仓库
     */
    public void initializeSkillRepository(Path skillsDir) {
        try {
            // 确保 skills 目录存在
            if (!Files.exists(skillsDir)) {
                Files.createDirectories(skillsDir);
                log.info("创建技能目录：{}", skillsDir.toAbsolutePath());
            }

            // 创建文件系统技能仓库
            this.skillsDir = skillsDir;
            this.skillRepository = new FileSystemSkillRepository(skillsDir);
            log.info("技能仓库初始化完成：{}", skillsDir.toAbsolutePath());
        } catch (Exception e) {
            log.error("初始化技能仓库失败：{}", e.getMessage(), e);
        }
    }

    /**
     * 加载所有可用技能到 SkillBox
     * @param skillBox 要加载技能的 SkillBox
     */
    public void loadAllSkills(SkillBox skillBox) {
        if (skillRepository == null) {
            log.warn("技能仓库未初始化，跳过技能加载");
            return;
        }

        List<String> loadedSkills = new ArrayList<>();

        try {
            // 扫描 skills 目录下的所有子目录（每个子目录是一个技能）
            Files.list(skillsDir)
                    .filter(Files::isDirectory)
                    .forEach(skillDir -> {
                        String skillName = skillDir.getFileName().toString();
                        try {
                            AgentSkill skill = skillRepository.getSkill(skillName);
                            if (skill != null) {
                                skillBox.registerSkill(skill);
                                loadedSkills.add(skillName);
                                log.info("已加载技能：{}", skillName);
                            } else {
                                log.warn("技能文件无效：{}", skillName);
                            }
                        } catch (Exception e) {
                            log.error("加载技能失败 [{}]: {}", skillName, e.getMessage());
                        }
                    });

            log.info("技能加载完成，共加载 {} 个技能：{}", loadedSkills.size(), loadedSkills);
        } catch (Exception e) {
            log.error("扫描技能目录失败：{}", e.getMessage(), e);
        }
    }

    /**
     * 获取指定技能
     * @param skillName 技能名称
     * @return 技能实例，如果不存在则返回 null
     */
    public AgentSkill getSkill(String skillName) {
        if (skillRepository == null) {
            log.warn("技能仓库未初始化");
            return null;
        }

        try {
            AgentSkill skill = skillRepository.getSkill(skillName);
            if (skill != null) {
                log.info("已获取技能：{}", skillName);
            } else {
                log.warn("技能不存在：{}", skillName);
            }
            return skill;
        } catch (Exception e) {
            log.error("获取技能失败 [{}]: {}", skillName, e.getMessage());
            return null;
        }
    }

    /**
     * 检查指定技能是否存在
     * @param skillName 技能名称
     * @return 是否存在
     */
    public boolean hasSkill(String skillName) {
        if (skillRepository == null) {
            return false;
        }

        Path skillPath = skillsDir.resolve(skillName);
        return Files.exists(skillPath);
    }

    /**
     * 获取技能目录路径
     * @return 技能目录的绝对路径
     */
    public Path getSkillsDir() {
        return skillsDir.toAbsolutePath();
    }
}
