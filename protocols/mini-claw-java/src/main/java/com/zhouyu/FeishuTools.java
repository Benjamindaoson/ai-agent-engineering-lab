package com.zhouyu;

import io.agentscope.core.tool.Tool;
import io.agentscope.core.tool.ToolParam;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 飞书助手工具集
 * 作者：IT周瑜
 * 公众号：IT周瑜
 * 微信号：it_zhouyu
 */
public class FeishuTools {

    @Tool(description = "获取当前时间")
    public String getCurrentTime() {
        return "当前时间: " + LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }

    @Tool(description = "获取指定城市的天气信息")
    public String getWeather(@ToolParam(name = "city", description = "城市名称") String city) {
        // 模拟天气数据
        String[] weathers = {"晴天", "多云", "小雨", "大雨", "阴天"};
        String[] temps = {"22°C", "25°C", "28°C", "18°C", "20°C"};

        int index = Math.abs(city.hashCode()) % weathers.length;
        return city + " 的天气：" + weathers[index] + "，温度：" + temps[index];
    }

    @Tool(description = "计算数学表达式")
    public String calculate(@ToolParam(name = "expression", description = "数学表达式，如 '1+2*3'") String expression) {
        try {
            // 简单的计算逻辑（实际应用中可以使用更复杂的表达式解析库）
            expression = expression.replaceAll("\\s+", "");

            // 处理加减乘除
            if (expression.contains("+")) {
                String[] parts = expression.split("\\+");
                double result = Double.parseDouble(parts[0]) + Double.parseDouble(parts[1]);
                return "计算结果: " + result;
            } else if (expression.contains("-") && expression.lastIndexOf("-") > 0) {
                String[] parts = expression.split("-");
                double result = Double.parseDouble(parts[0]) - Double.parseDouble(parts[1]);
                return "计算结果: " + result;
            } else if (expression.contains("*")) {
                String[] parts = expression.split("\\*");
                double result = Double.parseDouble(parts[0]) * Double.parseDouble(parts[1]);
                return "计算结果: " + result;
            } else if (expression.contains("/")) {
                String[] parts = expression.split("/");
                double result = Double.parseDouble(parts[0]) / Double.parseDouble(parts[1]);
                return "计算结果: " + result;
            }

            return "计算结果: " + expression;
        } catch (Exception e) {
            return "计算失败，请检查表达式格式";
        }
    }

    @Tool(description = "生成随机数")
    public String generateRandomNumber(
            @ToolParam(name = "min", description = "最小值") int min,
            @ToolParam(name = "max", description = "最大值") int max) {
        if (min > max) {
            return "错误：最小值不能大于最大值";
        }
        int random = (int) (Math.random() * (max - min + 1)) + min;
        return "随机数: " + random;
    }

    @Tool(description = "翻译文本")
    public String translate(
            @ToolParam(name = "text", description = "要翻译的文本") String text,
            @ToolParam(name = "targetLang", description = "目标语言，如 '英文', '日文', '韩文'") String targetLang) {
        // 模拟翻译（实际应用中可以调用翻译 API）
        return "【模拟翻译】将 \"" + text + "\" 翻译为" + targetLang;
    }
}