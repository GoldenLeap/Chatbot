/**
 * Lógica AJAX do Chatbot Guaxinim
 * Lê a URL de envio a partir do atributo data-send-url do contêiner de mensagens.
 */
(function () {    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    if (!chatMessages || !chatForm) return;

    const SEND_URL = chatMessages.dataset.sendUrl;
    
    // Configura o parser de Markdown
    marked.use({ gfm: true, breaks: true });

    scrollToBottom();
    renderExistingBotMessages();

    /**
     * Rola suavemente o contêiner de chat para o final.
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        const d = document.createElement('div');
        d.appendChild(document.createTextNode(text));
        return d.innerHTML;
    }

    function nowTime() {
        return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Alterna o estado visual dos botões de envio durante o processamento.
     */
    function setLoading(loading) {
        sendBtn.disabled = loading;
        messageInput.disabled = loading;
        sendBtn.style.opacity = loading ? '0.6' : '1';
    }

    function updateTitle(newTitle) {
        document.title = newTitle + ' - Assistente Academico';
        const h3 = document.querySelector('.chat-info h3');
        if (!h3) return;
        h3.style.transition = 'opacity 0.3s ease';
        h3.style.opacity = '0';
        setTimeout(() => {
            h3.textContent = newTitle;
            h3.style.opacity = '1';
        }, 300);
    }

    function renderExistingBotMessages() {
        document.querySelectorAll('.message-bot .message-bubble p').forEach(p => {
            const raw = p.textContent;
            const md = document.createElement('div');
            md.className = 'md-content';
            md.innerHTML = DOMPurify.sanitize(marked.parse(raw));
            p.replaceWith(md);
            renderMath(md); // Renderiza o KaTeX após o markdown
        });
    }

    function renderMath(el) {
        if (!window.renderMathInElement) return;
        
        // Substituímos <br> por quebras de linha reais dentro do elemento 
        // para que o KaTeX consiga casar os delimitadores $$ mesmo se o Markdown
        // tiver inserido tags <br> no meio.
        const brs = el.querySelectorAll('br');
        brs.forEach(br => br.replaceWith('\n'));
        
        renderMathInElement(el, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '\\[', right: '\\]', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false }
            ],
            throwOnError: false,
            ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
        });
    }

    function createMessageEl(role, content, time) {
        const wrapper = document.createElement('div');
        wrapper.className = `message ${role === 'user' ? 'message-user' : 'message-bot'}`;
        const bodyHtml = role === 'bot'
            ? `<div class="md-content">${DOMPurify.sanitize(marked.parse(content))}</div>`
            : `<p>${escapeHtml(content)}</p>`;
        wrapper.innerHTML = `
            <div class="message-bubble">
                <span class="message-sender">${role === 'user' ? 'Você' : 'Guaxinim'}</span>
                ${bodyHtml}
                <span class="message-time">${time}</span>
            </div>`;
        
        if (role === 'bot') {
            const mdContent = wrapper.querySelector('.md-content');
            if (mdContent) renderMath(mdContent);
        }

        return wrapper;
    }

    function createTypingIndicator() {
        const el = document.createElement('div');
        el.className = 'message message-bot';
        el.id = 'typing-indicator';
        el.innerHTML = `
            <div class="message-bubble">
                <span class="message-sender">Guaxinim</span>
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>`;
        return el;
    }

    function createErrorEl() {
        const el = document.createElement('div');
        el.className = 'message message-bot';
        el.innerHTML = `
            <div class="message-bubble" style="border-color:rgba(239,68,68,0.4)">
                <p style="color:#fca5a5">Ops! Não consegui me conectar. Tente novamente 🦝</p>
            </div>`;
        return el;
    }


    /**
     * Trata o envio do formulário, envia via Fetch API e atualiza a UI.
     */
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const content = messageInput.value.trim();
        if (!content) return;


        const emptyChat = document.getElementById('empty-chat');
        if (emptyChat) emptyChat.remove();

        chatMessages.appendChild(createMessageEl('user', content, nowTime()));
        messageInput.value = '';
        setLoading(true);

        const typingEl = createTypingIndicator();
        chatMessages.appendChild(typingEl);
        scrollToBottom();

        try {
            const res = await fetch(SEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            typingEl.remove();

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let isFirstChunk = true;
            let botMessageWrapper = null;
            let mdContent = null;
            let currentContent = '';
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                let lines = buffer.split('\n\n');
                buffer = lines.pop(); // Mantém o que não terminou com \n\n no buffer

                for (let line of lines) {
                    if (line.startsWith('data: ')) {
                        let jsonStr = line.substring(6);
                        if (!jsonStr.trim()) continue;
                        
                        try {
                            const data = JSON.parse(jsonStr);

                            if (data.new_title) {
                                updateTitle(data.new_title);
                            }

                            if (data.chunk !== undefined) {
                                currentContent += data.chunk;

                                if (isFirstChunk) {
                                    isFirstChunk = false;
                                    botMessageWrapper = createMessageEl('bot', '', nowTime());
                                    chatMessages.appendChild(botMessageWrapper);
                                    mdContent = botMessageWrapper.querySelector('.md-content');
                                }

                                if (mdContent) {
                                    mdContent.innerHTML = DOMPurify.sanitize(marked.parse(currentContent));
                                    scrollToBottom();
                                }
                            }

                            if (data.done) {
                                // Finaliza o stream renderizando KaTeX
                                if (mdContent) {
                                    renderMath(mdContent);
                                }
                            }
                        } catch(e) {
                            console.error("Erro ao fazer parse do chunk JSON:", e, jsonStr);
                        }
                    }
                }
            }

            // Garantia final
            if (!botMessageWrapper && !isFirstChunk){
                 // Caso ocorra problema, renderizamos no finally ou cai no catch
            }

        } catch (err) {
            console.error('[chat.js]', err);
            if(document.getElementById('typing-indicator')) typingEl.remove();
            chatMessages.appendChild(createErrorEl());
        } finally {
            setLoading(false);
            scrollToBottom();
            messageInput.focus();
        }
    });

    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

}());
