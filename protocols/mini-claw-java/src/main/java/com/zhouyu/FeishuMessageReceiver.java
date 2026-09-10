package com.zhouyu;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import com.lark.oapi.Client;
import com.lark.oapi.event.EventDispatcher;
import com.lark.oapi.service.im.ImService;
import com.lark.oapi.service.im.v1.model.*;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;

/**
 * 飞书消息接收器
 * 作者：IT周瑜
 * 公众号：IT周瑜
 * 微信号：it_zhouyu
 */
@Slf4j
@Component
public class FeishuMessageReceiver {

    @Autowired
    private ClawAgent clawAgent;

    @PostConstruct
    public void start() {
        try {

            Client apiClient = Client.newBuilder(
                    "cli_a93ca78f80789cb2",
                    "3u6mHhDnplqdWw42MxPClfmPVM3Xjx7z").build();

            // 初始化事件处理器
            EventDispatcher eventHandler = EventDispatcher.newBuilder("", "")
                    .onP2MessageReceiveV1(new ImService.P2MessageReceiveV1Handler() {
                        @Override
                        public void handle(P2MessageReceiveV1 event) throws Exception {
                            log.info("收到新消息");

                            String eventId = event.getHeader().getEventId();

                            // 异步处理业务逻辑
                            CompletableFuture.runAsync(() -> {
                                try {
                                    processAndReplyMessage(apiClient, event);
                                    log.info("事件处理完成: {}", eventId);
                                } catch (Exception e) {
                                    log.error("事件处理失败: {}", eventId, e);
                                }
                            });


                        }
                    })
                    .build();

            // 初始化长连接客户端
            com.lark.oapi.ws.Client wsClient = new com.lark.oapi.ws.Client.Builder(
                    "cli_a93ca78f80789cb2",
                    "3u6mHhDnplqdWw42MxPClfmPVM3Xjx7z")
                    .eventHandler(eventHandler)
                    .build();

            wsClient.start();
            log.info("飞书消息接收器已启动...");

        } catch (Exception e) {
            log.error("启动失败：{}", e.getMessage(), e);
        }
    }

    public void processAndReplyMessage(Client apiClient, P2MessageReceiveV1 event) {
        try {
            String messageId = event.getEvent().getMessage().getMessageId();
            String chatType = event.getEvent().getMessage().getChatType();
            String content = event.getEvent().getMessage().getContent();
            String textContent = parseTextContent(content);

            log.info("消息 ID: {}", messageId);
            log.info("会话类型：{}", chatType);
            log.info("内容：{}", textContent);

            // 获取发送者信息
            P2MessageReceiveV1Data eventData = event.getEvent();
            String senderOpenId = eventData.getSender().getSenderId().getOpenId();
            String senderUserId = eventData.getSender().getSenderId().getUserId();

            log.info("发送者 OpenID: {}", senderOpenId);
            log.info("发送者 UserID: {}", senderUserId);

            // 检查是否为新会话命令
            String replyText;
            if ("/new".equals(textContent.trim())) {
                clawAgent.newSession(ClawAgent.FEISHU_SESSION_ID);
                replyText = "已重置会话，我们可以开始新的对话了！";
            } else {
                // 使用飞书会话进行回复
                replyText = clawAgent.feishuChat(textContent);
            }

            if ("p2p".equals(chatType)) {
                replyInPrivate(apiClient, senderOpenId, replyText);
            } else if ("group".equals(chatType)) {
                replyInGroup(apiClient, messageId, replyText);
            }

        } catch (Exception e) {
            log.error("处理消息失败：{}", e.getMessage(), e);
        }
    }

    /**
     * 私聊回复 - 直接发送新消息
     */
    private void replyInPrivate(Client apiClient, String senderOpenId, String replyText) {
        try {
            JSONObject messageContent = new JSONObject();
            messageContent.put("text", replyText);

            CreateMessageReq createReq = CreateMessageReq.newBuilder()
                    .receiveIdType("open_id")
                    .createMessageReqBody(CreateMessageReqBody.newBuilder()
                            .receiveId(senderOpenId)
                            .msgType("text")
                            .content(messageContent.toJSONString())
                            .build())
                    .build();

            CreateMessageResp createResp = apiClient.im().v1().message().create(createReq);

            if (createResp.success()) {
                log.info("私聊回复成功，消息 ID: {}", createResp.getData().getMessageId());
            } else {
                log.error("私聊回复失败：{}, 错误码：{}", createResp.getMsg(), createResp.getCode());
            }

        } catch (Exception e) {
            log.error("私聊回复异常：{}", e.getMessage(), e);
        }
    }

    /**
     * 群聊回复 - 引用回复
     */
    private void replyInGroup(Client apiClient, String messageId, String replyText) {
        try {
            JSONObject replyContent = new JSONObject();
            replyContent.put("text", replyText);

            ReplyMessageReq replyReq = ReplyMessageReq.newBuilder()
                    .messageId(messageId)
                    .replyMessageReqBody(ReplyMessageReqBody.newBuilder()
                            .content(replyContent.toJSONString())
                            .msgType("text")
                            .build())
                    .build();

            ReplyMessageResp replyResp = apiClient.im().v1().message().reply(replyReq);

            if (replyResp.success()) {
                log.info("群聊回复成功，消息 ID: {}", replyResp.getData().getMessageId());
            } else {
                log.error("群聊回复失败：{}, 错误码：{}", replyResp.getMsg(), replyResp.getCode());
            }

        } catch (Exception e) {
            log.error("群聊回复异常：{}", e.getMessage(), e);
        }
    }

    /**
     * 解析文本内容
     */
    private String parseTextContent(String jsonContent) {
        try {
            JSONObject content = JSON.parseObject(jsonContent);
            if (content.containsKey("text")) {
                return content.getString("text");
            }
            return "[非文本消息]";
        } catch (Exception e) {
            return "[无法解析的内容]";
        }
    }

    public static void main(String[] args) throws IOException {
        FeishuMessageReceiver feishuDemo = new FeishuMessageReceiver();
        feishuDemo.start();
        System.in.read();
    }
}