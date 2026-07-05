class AguiClient {
    constructor(endpoint) {
        this.endpoint = endpoint;
        this.abortController = null;
    }

    abort() {
        if (this.abortController) this.abortController.abort();
    }

    async run(input, callbacks = {}) {
        this.abortController = new AbortController();
        const response = await fetch(this.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
            body: JSON.stringify(input),
            signal: this.abortController.signal
        });
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split(/\r?\n\r?\n/);
            buffer = parts.pop();
            for (const part of parts) this.handleMessage(part, callbacks);
        }
        if (buffer.trim()) this.handleMessage(buffer, callbacks);
        this.abortController = null;
    }

    handleMessage(message, callbacks) {
        for (const line of message.split(/\r?\n/)) {
            if (!line.startsWith('data:')) continue;
            const event = JSON.parse(line.slice(5).trim());
            this.handleEvent(event, callbacks);
        }
    }

    handleEvent(event, callbacks) {
        if (event.type === 'RUN_STARTED') callbacks.onRunStarted?.(event.threadId, event.runId);
        if (event.type === 'TEXT_MESSAGE_START') callbacks.onTextMessageStart?.(event.messageId, event.role);
        if (event.type === 'TEXT_MESSAGE_CONTENT') callbacks.onTextContent?.(event.delta || '', event.messageId);
        if (event.type === 'TEXT_MESSAGE_END') callbacks.onTextMessageEnd?.(event.messageId);
        if (event.type === 'RUN_FINISHED') callbacks.onRunFinished?.(event.threadId, event.runId);
        if (event.type === 'RAW' && event.rawEvent?.error) callbacks.onError?.(event.rawEvent.error);
    }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { AguiClient };
