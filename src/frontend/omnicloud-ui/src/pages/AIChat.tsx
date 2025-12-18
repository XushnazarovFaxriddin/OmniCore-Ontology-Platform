import { useState, useRef, useEffect } from 'react';
import { aiApi } from '../api/client';
import type { ChatMessage } from '../types';

function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'system',
      content: 'OmniCore AI Assistant tayyor. Ontologiya, bilim muhandisligi va semantik texnologiyalar bo\'yicha savollaringizga javob beraman.',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [context, setContext] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const chatHistory = messages
        .filter((m) => m.role !== 'system')
        .concat(userMessage)
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await aiApi.chat(chatHistory, context || undefined);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        metadata: {
          model: response.model_id,
          confidence: response.confidence,
          tokens: response.tokens_used,
          latency: response.latency_ms,
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    { label: 'Root turini aniqlash', prompt: 'Menga root turini aniqlashda yordam bering' },
    { label: 'Kauzal aloqalar', prompt: 'Ikki entity o\'rtasidagi kauzal aloqalarni qanday topish mumkin?' },
    { label: 'Epistemik annotatsiya', prompt: 'Epistemik annotatsiya nima va qanday ishlatiladi?' },
    { label: 'Ontologiya sifati', prompt: 'Ontologiya sifatini qanday baholash mumkin?' },
  ];

  const clearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: 'system',
        content: 'Chat tozalandi. Yangi suhbat boshlang.',
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  return (
    <div className="ai-chat-container">
      <div className="ai-chat-header">
        <h1>AI Chat</h1>
        <p>OmniCore AI Assistant bilan suhbatlashing</p>
        <div className="chat-controls">
          <input
            type="text"
            placeholder="Kontekst (ixtiyoriy)..."
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="context-input"
          />
          <button onClick={clearChat} className="btn-secondary">
            Tozalash
          </button>
        </div>
      </div>

      <div className="quick-actions">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => setInput(action.prompt)}
            className="quick-action-btn"
          >
            {action.label}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.role}`}
          >
            <div className="message-header">
              <span className="message-role">
                {message.role === 'user' ? 'Siz' : message.role === 'assistant' ? 'AI' : 'Tizim'}
              </span>
              <span className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              {message.content}
            </div>
            {message.metadata && (
              <div className="message-meta">
                <span>Model: {message.metadata.model as string}</span>
                <span>Ishonch: {((message.metadata.confidence as number) * 100).toFixed(0)}%</span>
                <span>Tokenlar: {message.metadata.tokens as number}</span>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Xabaringizni yozing..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
          {isLoading ? 'Yuborilmoqda...' : 'Yuborish'}
        </button>
      </form>

      <style>{`
        .ai-chat-container {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 100px);
          max-width: 900px;
          margin: 0 auto;
        }

        .ai-chat-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .ai-chat-header h1 {
          margin: 0 0 0.5rem 0;
          color: var(--primary-color, #2563eb);
        }

        .ai-chat-header p {
          margin: 0 0 1rem 0;
          color: var(--text-secondary, #666);
        }

        .chat-controls {
          display: flex;
          gap: 0.5rem;
        }

        .context-input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
        }

        .quick-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: var(--bg-secondary, #f5f5f5);
        }

        .quick-action-btn {
          padding: 0.4rem 0.8rem;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 16px;
          cursor: pointer;
          font-size: 0.85rem;
          transition: all 0.2s;
        }

        .quick-action-btn:hover {
          background: var(--primary-color, #2563eb);
          color: white;
          border-color: var(--primary-color, #2563eb);
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          max-width: 80%;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
          align-self: flex-end;
          background: var(--primary-color, #2563eb);
          color: white;
        }

        .message.assistant {
          align-self: flex-start;
          background: var(--bg-secondary, #f0f0f0);
        }

        .message.system {
          align-self: center;
          background: var(--warning-bg, #fff3cd);
          color: var(--warning-text, #856404);
          font-size: 0.9rem;
          max-width: 90%;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
          font-size: 0.75rem;
          opacity: 0.8;
        }

        .message-content {
          white-space: pre-wrap;
          line-height: 1.5;
        }

        .message-meta {
          display: flex;
          gap: 1rem;
          margin-top: 0.5rem;
          font-size: 0.7rem;
          opacity: 0.7;
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 0.5rem;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: var(--primary-color, #2563eb);
          border-radius: 50%;
          animation: bounce 1.4s infinite both;
        }

        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        .chat-input-form {
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          border-top: 1px solid var(--border-color, #e0e0e0);
          background: white;
        }

        .chat-input {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 24px;
          font-size: 1rem;
          outline: none;
          transition: border-color 0.2s;
        }

        .chat-input:focus {
          border-color: var(--primary-color, #2563eb);
        }

        .send-btn {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #2563eb);
          color: white;
          border: none;
          border-radius: 24px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.2s;
        }

        .send-btn:hover:not(:disabled) {
          background: var(--primary-dark, #1d4ed8);
        }

        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          padding: 0.5rem 1rem;
          background: transparent;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-secondary:hover {
          background: var(--bg-secondary, #f5f5f5);
        }
      `}</style>
    </div>
  );
}

export default AIChat;
