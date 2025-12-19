import { useState, useEffect } from 'react';
import { aiApi, globalApi } from '../api/client';
import type { AIModel } from '../types';

interface ModelUsageStats {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_latency_ms: number;
  total_tokens: number;
  requests_today: number;
}

function AIModels() {
  const [models, setModels] = useState<AIModel[]>([]);
  const [health, setHealth] = useState<{ status: string; providers: Record<string, boolean> } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [testPrompt, setTestPrompt] = useState('');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testMetrics, setTestMetrics] = useState<{ latency: number; tokens: number } | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  // Strategic Plan State
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [planResult, setPlanResult] = useState<{
    objectives: string[];
    actions: string[];
    requires_human_approval: boolean;
  } | null>(null);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);

  // Usage Stats (simulated for now)
  const [usageStats] = useState<ModelUsageStats>({
    total_requests: 1247,
    successful_requests: 1198,
    failed_requests: 49,
    avg_latency_ms: 342,
    total_tokens: 156420,
    requests_today: 87,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [healthData, modelsData] = await Promise.all([
        aiApi.getHealth().catch(() => ({ status: 'unknown', providers: {} })),
        aiApi.listModels().catch(() => []),
      ]);
      setHealth(healthData);
      setModels(Array.isArray(modelsData) ? modelsData : []);
    } catch (err) {
      setError('Failed to load AI service data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestModel = async () => {
    if (!testPrompt.trim()) return;
    setIsTesting(true);
    setTestResult(null);
    setTestMetrics(null);
    try {
      const startTime = Date.now();
      const response = await aiApi.generate({
        prompt: testPrompt,
        task_type: 'general',
        max_tokens: 512,
        temperature: 0.7,
        model: selectedModel || undefined,
      });
      const latency = Date.now() - startTime;
      setTestResult(response.response);
      setTestMetrics({ latency, tokens: response.tokens_used });
    } catch (err) {
      setTestResult('Error: Model unavailable. Please ensure Ollama is running with: ollama serve');
    } finally {
      setIsTesting(false);
    }
  };

  const handleGenerateStrategicPlan = async () => {
    setIsGeneratingPlan(true);
    try {
      const stats = await globalApi.getStats();
      const metrics = {
        total_roots: stats.total_roots,
        total_causality_links: stats.total_causality_links,
        total_epistemic_annotations: stats.total_epistemic_annotations,
        avg_causality_confidence: stats.avg_causality_confidence,
        avg_epistemic_certainty: stats.avg_epistemic_certainty,
      };
      const gaps = [
        stats.total_roots < 100 ? 'Low root entity count' : '',
        stats.avg_causality_confidence < 0.7 ? 'Low causality confidence' : '',
        stats.avg_epistemic_certainty < 0.6 ? 'Low epistemic certainty' : '',
      ].filter(Boolean);

      const plan = await aiApi.generateStrategicPlan(metrics, gaps);
      setPlanResult(plan);
      setShowPlanModal(true);
    } catch (err) {
      setError('Failed to generate strategic plan');
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  const defaultModels: AIModel[] = [
    {
      id: 'ollama-llama3.2',
      name: 'Llama 3.2 (3B)',
      provider: 'Ollama',
      status: health?.providers?.ollama ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'analysis', 'reasoning', 'classification'],
    },
    {
      id: 'ollama-mistral',
      name: 'Mistral 7B',
      provider: 'Ollama',
      status: health?.providers?.ollama ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'code', 'analysis'],
    },
    {
      id: 'ollama-phi3',
      name: 'Phi-3 Mini',
      provider: 'Ollama',
      status: health?.providers?.ollama ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'reasoning', 'math'],
    },
    {
      id: 'openai-gpt4',
      name: 'GPT-4 Turbo',
      provider: 'OpenAI',
      status: health?.providers?.openai ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'code', 'analysis', 'reasoning', 'vision'],
    },
    {
      id: 'anthropic-claude',
      name: 'Claude 3 Sonnet',
      provider: 'Anthropic',
      status: health?.providers?.anthropic ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'analysis', 'reasoning', 'long-context'],
    },
  ];

  const displayModels = models.length > 0 ? models : defaultModels;

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading AI services...</p>
      </div>
    );
  }

  return (
    <div className="ai-models">
      <header className="models-header">
        <div>
          <h1>AI Models</h1>
          <p>Manage and monitor SLM providers (Ollama recommended)</p>
        </div>
        <div className="header-actions">
          <button
            className="btn-secondary"
            onClick={handleGenerateStrategicPlan}
            disabled={isGeneratingPlan}
          >
            {isGeneratingPlan ? 'Generating...' : 'Strategic Plan'}
          </button>
          <button className="btn-primary" onClick={loadData}>
            Refresh
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Setup Instructions */}
      {health?.status !== 'healthy' && (
        <div className="setup-banner">
          <h3>Quick Setup</h3>
          <p>To use AI features, start Ollama locally:</p>
          <code>ollama serve</code>
          <p>Then pull a model:</p>
          <code>ollama pull llama3.2</code>
        </div>
      )}

      {/* Health Status */}
      <div className="section">
        <h2>Service Status</h2>
        <div className="health-grid">
          <div className={`health-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
            <span className="status-icon">{health?.status === 'healthy' ? '✓' : '!'}</span>
            <span className="status-label">Overall Status</span>
            <span className="status-value">{health?.status || 'Unknown'}</span>
          </div>
          {Object.entries(health?.providers || { ollama: false, openai: false, anthropic: false }).map(([provider, isHealthy]) => (
            <div key={provider} className={`health-card ${isHealthy ? 'healthy' : 'unhealthy'}`}>
              <span className="status-icon">{isHealthy ? '✓' : '×'}</span>
              <span className="status-label">{provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
              <span className="status-value">{isHealthy ? 'Connected' : 'Offline'}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Statistics */}
      <div className="section">
        <h2>Usage Statistics</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-value">{usageStats.total_requests.toLocaleString()}</span>
            <span className="stat-label">Total Requests</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{((usageStats.successful_requests / usageStats.total_requests) * 100).toFixed(1)}%</span>
            <span className="stat-label">Success Rate</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{usageStats.avg_latency_ms}ms</span>
            <span className="stat-label">Avg Latency</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{(usageStats.total_tokens / 1000).toFixed(1)}K</span>
            <span className="stat-label">Total Tokens</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{usageStats.requests_today}</span>
            <span className="stat-label">Today's Requests</span>
          </div>
        </div>
      </div>

      {/* Models Grid */}
      <div className="section">
        <h2>Available Models</h2>
        <div className="models-grid">
          {displayModels.map((model) => (
            <div
              key={model.id}
              className={`model-card ${selectedModel === model.id ? 'selected' : ''} ${model.status}`}
              onClick={() => setSelectedModel(model.id === selectedModel ? null : model.id)}
            >
              <div className="model-header">
                <h3>{model.name}</h3>
                <span className={`status-badge ${model.status}`}>
                  {model.status === 'available' ? 'Available' :
                   model.status === 'loading' ? 'Loading' : 'Offline'}
                </span>
              </div>
              <div className="model-provider">
                <span className={`provider-badge ${model.provider.toLowerCase()}`}>
                  {model.provider}
                </span>
                {model.provider === 'Ollama' && <span className="recommended">Recommended</span>}
              </div>
              <div className="model-capabilities">
                {model.capabilities.map((cap) => (
                  <span key={cap} className="capability-tag">{cap}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Panel */}
      <div className="section">
        <h2>Model Playground</h2>
        <p className="section-desc">
          Test the selected model: <strong>{selectedModel || 'default (Ollama)'}</strong>
        </p>

        <div className="test-form">
          <textarea
            value={testPrompt}
            onChange={(e) => setTestPrompt(e.target.value)}
            placeholder="Enter a prompt to test the model..."
            rows={4}
          />
          <div className="test-actions">
            <button
              className="btn-primary"
              onClick={handleTestModel}
              disabled={isTesting || !testPrompt.trim()}
            >
              {isTesting ? 'Processing...' : 'Test Model'}
            </button>
            {testMetrics && (
              <div className="test-metrics">
                <span>Latency: {testMetrics.latency}ms</span>
                <span>Tokens: {testMetrics.tokens}</span>
              </div>
            )}
          </div>
        </div>

        {testResult && (
          <div className="test-result">
            <h4>Response</h4>
            <pre>{testResult}</pre>
          </div>
        )}
      </div>

      {/* Configuration Panel */}
      <div className="section">
        <h2>Configuration</h2>
        <div className="config-grid">
          <div className="config-card">
            <h4>Default Provider</h4>
            <select defaultValue="ollama" disabled>
              <option value="ollama">Ollama (Local)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
            <p className="config-desc">Primary AI provider for all operations</p>
          </div>
          <div className="config-card">
            <h4>Default Model</h4>
            <select defaultValue="llama3.2" disabled>
              <option value="llama3.2">Llama 3.2 (3B)</option>
              <option value="mistral">Mistral 7B</option>
              <option value="phi3">Phi-3 Mini</option>
            </select>
            <p className="config-desc">Model used when none specified</p>
          </div>
          <div className="config-card">
            <h4>Max Tokens</h4>
            <input type="number" defaultValue={1024} disabled />
            <p className="config-desc">Maximum response length</p>
          </div>
          <div className="config-card">
            <h4>Temperature</h4>
            <input type="number" defaultValue={0.7} step={0.1} min={0} max={2} disabled />
            <p className="config-desc">Response creativity (0-2)</p>
          </div>
        </div>
        <p className="coming-soon-note">Configuration editing coming in v10.1</p>
      </div>

      {/* Future Features */}
      <div className="section">
        <h2>Coming Soon</h2>
        <div className="future-grid">
          <div className="future-card">
            <span className="future-icon">📊</span>
            <h4>Advanced Analytics</h4>
            <p>Detailed usage charts, cost tracking, and performance insights</p>
            <span className="version-badge">v10.1</span>
          </div>
          <div className="future-card">
            <span className="future-icon">🔧</span>
            <h4>Fine-tuning</h4>
            <p>Custom model training on your ontology data</p>
            <span className="version-badge">v10.2</span>
          </div>
          <div className="future-card">
            <span className="future-icon">🔄</span>
            <h4>Model Chaining</h4>
            <p>Create pipelines combining multiple models</p>
            <span className="version-badge">v10.2</span>
          </div>
          <div className="future-card">
            <span className="future-icon">🌐</span>
            <h4>Multi-Modal</h4>
            <p>Support for image and document analysis</p>
            <span className="version-badge">v11.0</span>
          </div>
          <div className="future-card">
            <span className="future-icon">🔒</span>
            <h4>Enterprise Security</h4>
            <p>SSO, audit logs, and compliance features</p>
            <span className="version-badge">v11.0</span>
          </div>
          <div className="future-card">
            <span className="future-icon">🤝</span>
            <h4>Agent Collaboration</h4>
            <p>Multi-agent workflows for complex tasks</p>
            <span className="version-badge">v11.0</span>
          </div>
        </div>
      </div>

      {/* Strategic Plan Modal */}
      {showPlanModal && planResult && (
        <div className="modal-overlay" onClick={() => setShowPlanModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Strategic Plan</h2>
              <button className="close-btn" onClick={() => setShowPlanModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {planResult.requires_human_approval && (
                <div className="approval-warning">
                  ⚠️ This plan requires human approval before execution
                </div>
              )}

              <div className="plan-section">
                <h3>Objectives</h3>
                <ul>
                  {planResult.objectives.map((obj, idx) => (
                    <li key={idx}>{obj}</li>
                  ))}
                </ul>
              </div>

              <div className="plan-section">
                <h3>Recommended Actions</h3>
                <ul>
                  {planResult.actions.map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowPlanModal(false)}>
                Close
              </button>
              <button className="btn-primary" disabled title="Coming in v10.1">
                Apply Plan
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .ai-models {
          padding: 1.5rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .models-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
        }

        .models-header h1 {
          margin: 0 0 0.25rem 0;
          color: var(--primary-color, #6366f1);
        }

        .models-header p {
          margin: 0;
          color: var(--text-secondary, #666);
        }

        .header-actions {
          display: flex;
          gap: 0.75rem;
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 400px;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid var(--border-color, #e0e0e0);
          border-top-color: var(--primary-color, #6366f1);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .error-banner {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 1rem;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #dc2626;
          margin-bottom: 1.5rem;
        }

        .error-banner button {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          color: inherit;
        }

        .setup-banner {
          padding: 1.25rem;
          background: linear-gradient(135deg, #1e293b, #334155);
          color: white;
          border-radius: 12px;
          margin-bottom: 1.5rem;
        }

        .setup-banner h3 {
          margin: 0 0 0.5rem 0;
        }

        .setup-banner p {
          margin: 0.5rem 0;
          opacity: 0.9;
        }

        .setup-banner code {
          display: inline-block;
          padding: 0.5rem 1rem;
          background: rgba(255,255,255,0.1);
          border-radius: 6px;
          font-family: 'Monaco', monospace;
          margin: 0.25rem 0;
        }

        .section {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .section h2 {
          margin: 0 0 1rem 0;
          font-size: 1.15rem;
          color: var(--text-primary, #1e293b);
        }

        .section-desc {
          margin: 0 0 1rem 0;
          color: var(--text-secondary, #666);
        }

        .health-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
          gap: 1rem;
        }

        .health-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 1rem;
          border-radius: 10px;
          border: 2px solid var(--border-color, #e0e0e0);
          transition: all 0.2s;
        }

        .health-card.healthy {
          border-color: #22c55e;
          background: #f0fdf4;
        }

        .health-card.unhealthy {
          border-color: #ef4444;
          background: #fef2f2;
        }

        .status-icon {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }

        .health-card.healthy .status-icon { color: #22c55e; }
        .health-card.unhealthy .status-icon { color: #ef4444; }

        .status-label {
          font-size: 0.8rem;
          color: var(--text-secondary, #666);
          text-transform: capitalize;
        }

        .status-value {
          font-weight: 600;
          margin-top: 0.25rem;
          font-size: 0.9rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 1rem;
        }

        .stat-card {
          text-align: center;
          padding: 1rem;
          background: var(--bg-secondary, #f8fafc);
          border-radius: 8px;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--primary-color, #6366f1);
          display: block;
        }

        .stat-label {
          font-size: 0.8rem;
          color: var(--text-secondary, #666);
        }

        .models-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1rem;
        }

        .model-card {
          padding: 1.25rem;
          background: white;
          border-radius: 10px;
          border: 2px solid var(--border-color, #e0e0e0);
          cursor: pointer;
          transition: all 0.2s;
        }

        .model-card:hover {
          border-color: var(--primary-color, #6366f1);
        }

        .model-card.selected {
          border-color: var(--primary-color, #6366f1);
          background: #f5f3ff;
        }

        .model-card.unavailable {
          opacity: 0.6;
        }

        .model-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
        }

        .model-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .status-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.7rem;
          font-weight: 600;
        }

        .status-badge.available {
          background: #dcfce7;
          color: #166534;
        }

        .status-badge.unavailable {
          background: #fef2f2;
          color: #dc2626;
        }

        .status-badge.loading {
          background: #fef3c7;
          color: #92400e;
        }

        .model-provider {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
        }

        .provider-badge {
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .provider-badge.ollama { background: #dbeafe; color: #1e40af; }
        .provider-badge.openai { background: #dcfce7; color: #166534; }
        .provider-badge.anthropic { background: #fae8ff; color: #86198f; }

        .recommended {
          font-size: 0.7rem;
          color: #22c55e;
          font-weight: 500;
        }

        .model-capabilities {
          display: flex;
          flex-wrap: wrap;
          gap: 0.4rem;
        }

        .capability-tag {
          padding: 0.15rem 0.4rem;
          background: var(--bg-secondary, #f5f5f5);
          border-radius: 4px;
          font-size: 0.7rem;
          color: var(--text-secondary, #666);
        }

        .test-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .test-form textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          font-size: 0.95rem;
          resize: vertical;
          font-family: inherit;
        }

        .test-form textarea:focus {
          outline: none;
          border-color: var(--primary-color, #6366f1);
        }

        .test-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .test-metrics {
          display: flex;
          gap: 1rem;
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
        }

        .test-result {
          margin-top: 1rem;
          padding: 1rem;
          background: #1e293b;
          border-radius: 8px;
          color: #e2e8f0;
        }

        .test-result h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.85rem;
          color: #94a3b8;
        }

        .test-result pre {
          margin: 0;
          white-space: pre-wrap;
          font-family: 'Monaco', monospace;
          font-size: 0.85rem;
          line-height: 1.5;
        }

        .config-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .config-card {
          padding: 1rem;
          background: var(--bg-secondary, #f8fafc);
          border-radius: 8px;
        }

        .config-card h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.9rem;
        }

        .config-card select,
        .config-card input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 6px;
          margin-bottom: 0.5rem;
        }

        .config-desc {
          margin: 0;
          font-size: 0.75rem;
          color: var(--text-secondary, #666);
        }

        .coming-soon-note {
          margin: 0;
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
          font-style: italic;
        }

        .future-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .future-card {
          padding: 1.25rem;
          background: var(--bg-secondary, #f8fafc);
          border-radius: 10px;
          border: 1px dashed var(--border-color, #e0e0e0);
          text-align: center;
          opacity: 0.8;
        }

        .future-icon {
          font-size: 2rem;
          display: block;
          margin-bottom: 0.75rem;
        }

        .future-card h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.95rem;
        }

        .future-card p {
          margin: 0 0 0.75rem 0;
          font-size: 0.8rem;
          color: var(--text-secondary, #666);
        }

        .version-badge {
          display: inline-block;
          padding: 0.2rem 0.5rem;
          background: var(--primary-color, #6366f1);
          color: white;
          border-radius: 12px;
          font-size: 0.7rem;
          font-weight: 600;
        }

        .btn-primary {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #6366f1);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-primary:hover:not(:disabled) {
          background: var(--primary-dark, #4f46e5);
        }

        .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          padding: 0.75rem 1.5rem;
          background: white;
          color: var(--text-primary, #333);
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary:hover:not(:disabled) {
          background: var(--bg-secondary, #f5f5f5);
        }

        .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.25rem 1.5rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .modal-header h2 {
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: var(--text-secondary, #666);
        }

        .modal-body {
          padding: 1.5rem;
          overflow-y: auto;
        }

        .approval-warning {
          padding: 0.75rem 1rem;
          background: #fef3c7;
          border-radius: 8px;
          color: #92400e;
          margin-bottom: 1rem;
        }

        .plan-section {
          margin-bottom: 1.5rem;
        }

        .plan-section h3 {
          margin: 0 0 0.75rem 0;
          font-size: 1rem;
        }

        .plan-section ul {
          margin: 0;
          padding-left: 1.25rem;
        }

        .plan-section li {
          margin-bottom: 0.5rem;
          line-height: 1.4;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          padding: 1rem 1.5rem;
          border-top: 1px solid var(--border-color, #e0e0e0);
        }

        @media (max-width: 640px) {
          .models-header {
            flex-direction: column;
            gap: 1rem;
          }

          .header-actions {
            width: 100%;
          }

          .header-actions button {
            flex: 1;
          }

          .config-grid,
          .future-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default AIModels;
