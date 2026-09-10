package com.zhouyu;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import jakarta.websocket.*;
import jakarta.websocket.server.ServerEndpoint;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * WebSocket 处理器 - 用于网页对话
 */
@Slf4j
@Component
@ServerEndpoint("/ws/chat")
public class WebSocketHandler {

    private ClawAgent clawAgent;

    private static ClawAgent getClawAgent() {
        return SpringContextUtils.getBean(ClawAgent.class);
    }

    @OnOpen
    public void onOpen(Session session) {
        log.info("新的 WebSocket 连接已建立：{}", session.getId());
    }

    @OnClose
    public void onClose(Session session) {
        log.info("WebSocket 连接已关闭：{}", session.getId());
    }

    @OnMessage
    public void onMessage(String message, Session session) {
        try {
            if (clawAgent == null) {
                clawAgent = getClawAgent();
            }

            // 解析用户消息
            JSONObject msg = JSON.parseObject(message);
            String userMessage = msg.getString("message");

            log.info("收到网页消息：{}", userMessage);

            String reply;
            // 检查是否为新会话命令
            if ("/new".equals(userMessage.trim())) {
                clawAgent.newSession(ClawAgent.MAIN_SESSION_ID);
                reply = "已重置会话，我们可以开始新的对话了！";
            } else {
                // 使用主会话进行回复
                reply = clawAgent.mainChat(userMessage);
            }

            // 发送回复
            JSONObject response = new JSONObject();
            response.put("type", "reply");
            response.put("message", reply);
            session.getBasicRemote().sendText(response.toJSONString());

        } catch (Exception e) {
            log.error("处理消息失败：{}", e.getMessage());
            try {
                JSONObject error = new JSONObject();
                error.put("type", "error");
                error.put("message", "处理失败：" + e.getMessage());
                session.getBasicRemote().sendText(error.toJSONString());
            } catch (IOException ex) {
                // ignore
            }
        }
    }

    @OnError
    public void onError(Throwable t) {
        log.error("WebSocket 错误：{}", t.getMessage(), t);
    }
}