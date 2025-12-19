import { useState, useRef, useEffect } from 'react';
import { aiApi } from '../api/client';
import type { ChatMessage } from '../types';

// OmniCore Project Context for AI
const OMNICORE_CONTEXT = `
You are OmniCore AI Assistant - an intelligent assistant for the OmniCore Ontology Platform v10.

## About OmniCore Platform
OmniCore is a comprehensive ontology management and knowledge engineering platform designed for:
- Managing semantic knowledge bases with RDF/OWL support
- Multi-modal ontology integration and harmonization
- AI-powered entity classification and relationship extraction
- Epistemic reasoning with certainty tracking

## Core Features
1. **Root Management**: Classify entities into 4 fundamental types:
   - EXTANT: Physical, observable entities (electrons, trees, buildings)
   - ABSTRACT: Non-physical concepts (democracy, mathematics, justice)
   - MENTAL: Mind-dependent entities (beliefs, emotions, thoughts)
   - FICTIVE: Fictional entities (unicorns, superheroes)

2. **Causality Engine**: Track causal relationships with 5 types:
   - EFFICIENT: Direct cause-effect (fire causes heat)
   - FINAL: Purpose/goal-oriented (studying for graduation)
   - MATERIAL: Constituent causation (atoms form molecules)
   - FORMAL: Structural causation (DNA determines traits)
   - EMERGENT: Complex system behaviors

3. **Epistemic Annotations**: Track knowledge certainty with bases:
   - Axiomatic: Self-evident truths
   - Empirical: Observation-based knowledge
   - Consensus: Community-agreed facts
   - Speculative: Hypothetical knowledge

4. **MMO (Meta-Meta Ontology)**: Quality metrics system tracking:
   - Completeness, Coverage, Coherence, Utility, Inclusivity

5. **AI/SLM Services**: Powered by local Ollama models for:
   - Root type inference
   - Causality extraction
   - Conflict resolution via multi-agent debate
   - Strategic planning

## Developer Capabilities
- RESTful API with FastAPI backend
- React + TypeScript frontend
- PostgreSQL/SQLite database support
- Docker & Kubernetes deployment ready
- Extensible plugin architecture

## How to Help Users
- Answer questions about ontology concepts
- Explain platform features and usage
- Guide through API endpoints
- Help with entity classification
- Assist with troubleshooting
`;

function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'system',
      content: 'OmniCore AI Assistant ready. Ask me anything about ontology management, knowledge engineering, or the OmniCore platform features.',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showContext, setShowContext] = useState(false);
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

      const response = await aiApi.chat(chatHistory, OMNICORE_CONTEXT);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        metadata: {
          model: response.model_used,
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
        content: 'Connection error. Please ensure the SLM service is running (Ollama recommended). Check /ai/models for status.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    { label: 'What is OmniCore?', prompt: 'What is the OmniCore platform and what are its main features?' },
    { label: 'Root Types', prompt: 'Explain the 4 root types (EXTANT, ABSTRACT, MENTAL, FICTIVE) with examples' },
    { label: 'Causality Types', prompt: 'What are the 5 causality types and when to use each?' },
    { label: 'API Guide', prompt: 'Give me an overview of the main API endpoints available' },
    { label: 'Getting Started', prompt: 'How do I get started with OmniCore as a developer?' },
    { label: 'MMO Metrics', prompt: 'Explain the MMO quality metrics system' },
  ];

  const clearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: 'system',
        content: 'Chat cleared. Ready for new conversation.',
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  return (
    <div className="ai-chat-container">
      <div className="ai-chat-header">
        <div className="header-content">
          <h1>AI Chat</h1>
          <p>Intelligent assistant for OmniCore Ontology Platform</p>
        </div>
        <div className="chat-controls">
          <button
            onClick={() => setShowContext(!showContext)}
            className="btn-outline"
            title="View AI Context"
          >
            {showContext ? 'Hide Context' : 'View Context'}
          </button>
          <button onClick={clearChat} className="btn-secondary">
            Clear Chat
          </button>
        </div>
      </div>

      {showContext && (
        <div className="context-panel">
          <h3>AI Knowledge Context</h3>
          <pre>{OMNICORE_CONTEXT}</pre>
        </div>
      )}

      <div className="quick-actions">
        <span className="quick-label">Quick prompts:</span>
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
                {message.role === 'user' ? 'You' : message.role === 'assistant' ? 'OmniCore AI' : 'System'}
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
                <span>Confidence: {((message.metadata.confidence as number) * 100).toFixed(0)}%</span>
                <span>Tokens: {message.metadata.tokens as number}</span>
                <span>Latency: {message.metadata.latency as number}ms</span>
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
          placeholder="Ask about OmniCore, ontologies, or knowledge engineering..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      <style>{`
        .ai-chat-container {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 100px);
          max-width: 1000px;
          margin: 0 auto;
        }

        .ai-chat-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .header-content h1 {
          margin: 0 0 0.25rem 0;
          color: var(--primary-color, #6366f1);
        }

        .header-content p {
          margin: 0;
          color: var(--text-secondary, #666);
          font-size: 0.9rem;
        }

        .chat-controls {
          display: flex;
          gap: 0.5rem;
        }

        .context-panel {
          max-height: 300px;
          overflow-y: auto;
          padding: 1rem;
          background: #1e293b;
          color: #e2e8f0;
          font-size: 0.8rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .context-panel h3 {
          margin: 0 0 0.5rem 0;
          color: #94a3b8;
        }

        .context-panel pre {
          margin: 0;
          white-space: pre-wrap;
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 0.75rem;
          line-height: 1.4;
        }

        .quick-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: var(--bg-secondary, #f8fafc);
          align-items: center;
        }

        .quick-label {
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
          margin-right: 0.5rem;
        }

        .quick-action-btn {
          padding: 0.4rem 0.8rem;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 16px;
          cursor: pointer;
          font-size: 0.8rem;
          transition: all 0.2s;
        }

        .quick-action-btn:hover {
          background: var(--primary-color, #6366f1);
          color: white;
          border-color: var(--primary-color, #6366f1);
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
          max-width: 85%;
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
          background: var(--primary-color, #6366f1);
          color: white;
        }

        .message.assistant {
          align-self: flex-start;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
        }

        .message.system {
          align-self: center;
          background: #fef3c7;
          color: #92400e;
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

        .message-role {
          font-weight: 600;
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
          opacity: 0.6;
          flex-wrap: wrap;
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 0.5rem;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: var(--primary-color, #6366f1);
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
          border-color: var(--primary-color, #6366f1);
        }

        .send-btn {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #6366f1);
          color: white;
          border: none;
          border-radius: 24px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.2s;
        }

        .send-btn:hover:not(:disabled) {
          background: var(--primary-dark, #4f46e5);
        }

        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          padding: 0.5rem 1rem;
          background: transparent;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .btn-secondary:hover {
          background: var(--bg-secondary, #f5f5f5);
        }

        .btn-outline {
          padding: 0.5rem 1rem;
          background: transparent;
          border: 1px solid var(--primary-color, #6366f1);
          color: var(--primary-color, #6366f1);
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .btn-outline:hover {
          background: var(--primary-color, #6366f1);
          color: white;
        }
      `}</style>
    </div>
  );
}

export default AIChat;
