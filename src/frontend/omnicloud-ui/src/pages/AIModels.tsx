import { useState, useEffect } from 'react';
import { aiApi, globalApi } from '../api/client';
import type { AIModel } from '../types';

interface ModelStats {
  total_requests: number;
  avg_latency_ms: number;
  success_rate: number;
  tokens_used: number;
}

function AIModels() {
  const [models, setModels] = useState<AIModel[]>([]);
  const [health, setHealth] = useState<{ status: string; providers: Record<string, boolean> } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [testPrompt, setTestPrompt] = useState('');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  // Strategic Plan State
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [planResult, setPlanResult] = useState<{
    objectives: string[];
    actions: string[];
    requires_human_approval: boolean;
  } | null>(null);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);

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
      setError('Ma\'lumotlarni yuklashda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestModel = async () => {
    if (!testPrompt.trim()) return;
    setIsTesting(true);
    setTestResult(null);
    try {
      const response = await aiApi.generate({
        prompt: testPrompt,
        task_type: 'general',
        max_tokens: 512,
        temperature: 0.7,
        model: selectedModel || undefined,
      });
      setTestResult(response.response);
    } catch (err) {
      setTestResult('Xatolik yuz berdi. Model mavjud emas yoki xatolik bor.');
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
        stats.total_roots < 100 ? 'Kam root entity\'lar' : '',
        stats.avg_causality_confidence < 0.7 ? 'Past kauzal ishonch darajasi' : '',
        stats.avg_epistemic_certainty < 0.6 ? 'Past epistemik aniqlik' : '',
      ].filter(Boolean);

      const plan = await aiApi.generateStrategicPlan(metrics, gaps);
      setPlanResult(plan);
      setShowPlanModal(true);
    } catch (err) {
      setError('Strategik rejani yaratishda xatolik');
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  const defaultModels: AIModel[] = [
    {
      id: 'ollama-llama3',
      name: 'Llama 3.2',
      provider: 'Ollama',
      status: health?.providers?.ollama ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'analysis', 'reasoning'],
    },
    {
      id: 'openai-gpt4',
      name: 'GPT-4',
      provider: 'OpenAI',
      status: health?.providers?.openai ? 'available' : 'unavailable',
      capabilities: ['text-generation', 'code', 'analysis', 'reasoning'],
    },
    {
      id: 'anthropic-claude',
      name: 'Claude 3',
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
        <p>Yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="ai-models">
      <header className="models-header">
        <div>
          <h1>AI Modellar</h1>
          <p>SLM va AI modellarni boshqarish va monitoring</p>
        </div>
        <div className="header-actions">
          <button
            className="btn-secondary"
            onClick={handleGenerateStrategicPlan}
            disabled={isGeneratingPlan}
          >
            {isGeneratingPlan ? 'Yaratilmoqda...' : 'Strategik Reja'}
          </button>
          <button className="btn-primary" onClick={loadData}>
            Yangilash
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Health Status */}
      <div className="health-section">
        <h2>Xizmat Holati</h2>
        <div className="health-grid">
          <div className={`health-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
            <span className="status-icon">{health?.status === 'healthy' ? '✓' : '!'}</span>
            <span className="status-label">Umumiy holat</span>
            <span className="status-value">{health?.status || 'Noma\'lum'}</span>
          </div>
          {Object.entries(health?.providers || {}).map(([provider, isHealthy]) => (
            <div key={provider} className={`health-card ${isHealthy ? 'healthy' : 'unhealthy'}`}>
              <span className="status-icon">{isHealthy ? '✓' : '×'}</span>
              <span className="status-label">{provider}</span>
              <span className="status-value">{isHealthy ? 'Faol' : 'Faol emas'}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Models Grid */}
      <div className="models-section">
        <h2>Mavjud Modellar</h2>
        <div className="models-grid">
          {displayModels.map((model) => (
            <div
              key={model.id}
              className={`model-card ${selectedModel === model.id ? 'selected' : ''}`}
              onClick={() => setSelectedModel(model.id === selectedModel ? null : model.id)}
            >
              <div className="model-header">
                <h3>{model.name}</h3>
                <span className={`status-badge ${model.status}`}>
                  {model.status === 'available' ? 'Mavjud' :
                   model.status === 'loading' ? 'Yuklanmoqda' : 'Mavjud emas'}
                </span>
              </div>
              <div className="model-provider">{model.provider}</div>
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
      <div className="test-section">
        <h2>Model Test</h2>
        <p>Tanlangan modelni test qiling: {selectedModel || 'default'}</p>

        <div className="test-form">
          <textarea
            value={testPrompt}
            onChange={(e) => setTestPrompt(e.target.value)}
            placeholder="Test so'rovini kiriting..."
            rows={4}
          />
          <button
            className="btn-primary"
            onClick={handleTestModel}
            disabled={isTesting || !testPrompt.trim()}
          >
            {isTesting ? 'Tekshirilmoqda...' : 'Test Qilish'}
          </button>
        </div>

        {testResult && (
          <div className="test-result">
            <h4>Natija:</h4>
            <pre>{testResult}</pre>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="actions-section">
        <h2>Tezkor Amallar</h2>
        <div className="actions-grid">
          <div className="action-card">
            <span className="action-icon">🔄</span>
            <h4>Modellarni Yangilash</h4>
            <p>Barcha modellar holatini tekshirish</p>
            <button className="btn-secondary" onClick={loadData}>Yangilash</button>
          </div>
          <div className="action-card">
            <span className="action-icon">📊</span>
            <h4>Statistikalar</h4>
            <p>Model ishlatilish statistikasi</p>
            <button className="btn-secondary" disabled>Tez kunda</button>
          </div>
          <div className="action-card">
            <span className="action-icon">⚙️</span>
            <h4>Konfiguratsiya</h4>
            <p>Model sozlamalarini o'zgartirish</p>
            <button className="btn-secondary" disabled>Tez kunda</button>
          </div>
          <div className="action-card">
            <span className="action-icon">📈</span>
            <h4>Strategik Reja</h4>
            <p>AI yordamida reja tuzish</p>
            <button
              className="btn-secondary"
              onClick={handleGenerateStrategicPlan}
              disabled={isGeneratingPlan}
            >
              {isGeneratingPlan ? '...' : 'Yaratish'}
            </button>
          </div>
        </div>
      </div>

      {/* Strategic Plan Modal */}
      {showPlanModal && planResult && (
        <div className="modal-overlay" onClick={() => setShowPlanModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Strategik Reja</h2>
              <button className="close-btn" onClick={() => setShowPlanModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {planResult.requires_human_approval && (
                <div className="approval-warning">
                  ⚠️ Bu reja inson tasdig'ini talab qiladi
                </div>
              )}

              <div className="plan-section">
                <h3>Maqsadlar</h3>
                <ul>
                  {planResult.objectives.map((obj, idx) => (
                    <li key={idx}>{obj}</li>
                  ))}
                </ul>
              </div>

              <div className="plan-section">
                <h3>Harakatlar</h3>
                <ul>
                  {planResult.actions.map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowPlanModal(false)}>
                Yopish
              </button>
              <button className="btn-primary" disabled>
                Rejani Qo'llash
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
          margin-bottom: 2rem;
        }

        .models-header h1 {
          margin: 0 0 0.5rem 0;
          color: var(--primary-color, #2563eb);
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
          border-top-color: var(--primary-color, #2563eb);
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

        .health-section,
        .models-section,
        .test-section,
        .actions-section {
          margin-bottom: 2rem;
        }

        .health-section h2,
        .models-section h2,
        .test-section h2,
        .actions-section h2 {
          margin: 0 0 1rem 0;
          font-size: 1.25rem;
        }

        .health-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 1rem;
        }

        .health-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 1rem;
          background: white;
          border-radius: 12px;
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
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
          text-transform: capitalize;
        }

        .status-value {
          font-weight: 600;
          margin-top: 0.25rem;
        }

        .models-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1rem;
        }

        .model-card {
          padding: 1.25rem;
          background: white;
          border-radius: 12px;
          border: 2px solid var(--border-color, #e0e0e0);
          cursor: pointer;
          transition: all 0.2s;
        }

        .model-card:hover {
          border-color: var(--primary-color, #2563eb);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .model-card.selected {
          border-color: var(--primary-color, #2563eb);
          background: #eff6ff;
        }

        .model-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .model-header h3 {
          margin: 0;
          font-size: 1.1rem;
        }

        .status-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
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
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
          margin-bottom: 0.75rem;
        }

        .model-capabilities {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .capability-tag {
          padding: 0.2rem 0.5rem;
          background: var(--bg-secondary, #f5f5f5);
          border-radius: 4px;
          font-size: 0.75rem;
          color: var(--text-secondary, #666);
        }

        .test-section p {
          margin: 0 0 1rem 0;
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
          font-size: 1rem;
          resize: vertical;
        }

        .test-form textarea:focus {
          outline: none;
          border-color: var(--primary-color, #2563eb);
        }

        .test-result {
          margin-top: 1rem;
          padding: 1rem;
          background: var(--bg-secondary, #f8f9fa);
          border-radius: 8px;
          border: 1px solid var(--border-color, #e0e0e0);
        }

        .test-result h4 {
          margin: 0 0 0.5rem 0;
        }

        .test-result pre {
          margin: 0;
          white-space: pre-wrap;
          font-family: inherit;
          line-height: 1.5;
        }

        .actions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 1rem;
        }

        .action-card {
          padding: 1.25rem;
          background: white;
          border-radius: 12px;
          border: 1px solid var(--border-color, #e0e0e0);
          text-align: center;
        }

        .action-icon {
          font-size: 2rem;
          display: block;
          margin-bottom: 0.75rem;
        }

        .action-card h4 {
          margin: 0 0 0.5rem 0;
        }

        .action-card p {
          margin: 0 0 1rem 0;
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
        }

        .btn-primary {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #2563eb);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-primary:hover:not(:disabled) {
          background: var(--primary-dark, #1d4ed8);
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
          font-size: 1rem;
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
        }
      `}</style>
    </div>
  );
}

export default AIModels;
