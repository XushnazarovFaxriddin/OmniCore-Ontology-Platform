import { useState } from 'react';
import { aiApi } from '../api/client';
import type { RootType, CausalityType, EpistemicBasis, ConflictType } from '../types';

type TabType = 'root-inference' | 'causality' | 'epistemic' | 'conflict' | 'enhancement' | 'quality';

interface InferenceResult {
  entity_name: string;
  root_type: RootType;
  confidence: number;
  reasoning: string;
}

interface CausalityResult {
  source: string;
  target: string;
  causality_type: string;
  confidence: number;
  reasoning: string;
}

function AIAssistant() {
  const [activeTab, setActiveTab] = useState<TabType>('root-inference');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Root Inference State
  const [entityName, setEntityName] = useState('');
  const [entityDescription, setEntityDescription] = useState('');
  const [inferenceResult, setInferenceResult] = useState<InferenceResult | null>(null);

  // Causality State
  const [causalityEntities, setCausalityEntities] = useState('');
  const [causalityDescriptions, setCausalityDescriptions] = useState('');
  const [causalityResults, setCausalityResults] = useState<CausalityResult[]>([]);

  // Epistemic State
  const [epistemicEntity, setEpistemicEntity] = useState('');
  const [epistemicClaim, setEpistemicClaim] = useState('');
  const [epistemicSource, setEpistemicSource] = useState('');
  const [epistemicResult, setEpistemicResult] = useState<{
    certainty: number;
    basis: EpistemicBasis;
    reasoning: string;
  } | null>(null);

  // Conflict State
  const [conflictEntityA, setConflictEntityA] = useState('');
  const [conflictEntityB, setConflictEntityB] = useState('');
  const [conflictDescription, setConflictDescription] = useState('');
  const [conflictType, setConflictType] = useState<ConflictType>('classification');
  const [conflictResult, setConflictResult] = useState<{
    consensus_reached: boolean;
    final_resolution: string;
    rounds: number;
  } | null>(null);

  // Enhancement State
  const [enhanceEntityId, setEnhanceEntityId] = useState('');
  const [enhanceEntityName, setEnhanceEntityName] = useState('');
  const [enhanceDescription, setEnhanceDescription] = useState('');
  const [enhancementResults, setEnhancementResults] = useState<Array<{
    enhancement_type: string;
    enhanced_value: string;
    confidence: number;
    rationale: string;
  }>>([]);

  // Quality State
  const [qualityName, setQualityName] = useState('');
  const [qualitySource, setQualitySource] = useState('');
  const [qualityDomain, setQualityDomain] = useState('');
  const [qualityTripleCount, setQualityTripleCount] = useState(0);
  const [qualityClasses, setQualityClasses] = useState('');
  const [qualityProperties, setQualityProperties] = useState('');
  const [qualityResult, setQualityResult] = useState<{
    overall_score: number;
    recommendation: string;
    issues: string[];
    suggestions: string[];
  } | null>(null);

  const handleRootInference = async () => {
    if (!entityName.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.inferRootType(entityName, entityDescription);
      setInferenceResult(result);
    } catch (err) {
      setError('Root turini aniqlashda xatolik yuz berdi');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCausalityExtraction = async () => {
    const entities = causalityEntities.split('\n').filter(e => e.trim());
    const descriptions = causalityDescriptions.split('\n').filter(d => d.trim());
    if (entities.length < 2) {
      setError('Kamida 2 ta entity kerak');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.extractCausality(entities, descriptions);
      setCausalityResults(result.relationships);
    } catch (err) {
      setError('Kauzal aloqalarni aniqlashda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEpistemicAnnotation = async () => {
    if (!epistemicEntity.trim() || !epistemicClaim.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.annotateEpistemic(epistemicEntity, epistemicClaim, epistemicSource);
      setEpistemicResult(result);
    } catch (err) {
      setError('Epistemik annotatsiyada xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConflictResolution = async () => {
    if (!conflictEntityA.trim() || !conflictEntityB.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.resolveConflict(
        `conflict-${Date.now()}`,
        conflictType,
        conflictEntityA,
        conflictEntityB,
        conflictDescription
      );
      setConflictResult({
        consensus_reached: result.consensus_reached,
        final_resolution: result.final_resolution,
        rounds: result.rounds.length,
      });
    } catch (err) {
      setError('Konfliktni hal qilishda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnhancement = async () => {
    if (!enhanceEntityName.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.enhanceEntity(
        enhanceEntityId || `entity-${Date.now()}`,
        enhanceEntityName,
        enhanceDescription
      );
      setEnhancementResults(result.enhancements);
    } catch (err) {
      setError('Entity-ni boyitishda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQualityAssessment = async () => {
    if (!qualityName.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.assessQuality(
        qualityName,
        qualitySource,
        qualityDomain,
        qualityTripleCount,
        qualityClasses.split(',').map(c => c.trim()).filter(Boolean),
        qualityProperties.split(',').map(p => p.trim()).filter(Boolean)
      );
      setQualityResult(result);
    } catch (err) {
      setError('Sifatni baholashda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'root-inference' as TabType, label: 'Root Turi', icon: '🌳' },
    { id: 'causality' as TabType, label: 'Kauzallik', icon: '🔗' },
    { id: 'epistemic' as TabType, label: 'Epistemik', icon: '📚' },
    { id: 'conflict' as TabType, label: 'Konflikt', icon: '⚖️' },
    { id: 'enhancement' as TabType, label: 'Boyitish', icon: '✨' },
    { id: 'quality' as TabType, label: 'Sifat', icon: '📊' },
  ];

  const rootTypeColors: Record<string, string> = {
    EXTANT: '#22c55e',
    ABSTRACT: '#3b82f6',
    MENTAL: '#a855f7',
    FICTIVE: '#f97316',
  };

  return (
    <div className="ai-assistant">
      <header className="assistant-header">
        <h1>AI Assistant</h1>
        <p>Ontologiya operatsiyalari uchun AI yordamchisi</p>
      </header>

      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="tab-content">
        {/* Root Type Inference */}
        {activeTab === 'root-inference' && (
          <div className="panel">
            <h2>Root Turini Aniqlash</h2>
            <p>Entity nomini kiriting va AI root turini (EXTANT, ABSTRACT, MENTAL, FICTIVE) aniqlaydi</p>

            <div className="form-group">
              <label>Entity nomi</label>
              <input
                type="text"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
                placeholder="masalan: Electron, Democracy, Happiness, Unicorn"
              />
            </div>

            <div className="form-group">
              <label>Tavsif (ixtiyoriy)</label>
              <textarea
                value={entityDescription}
                onChange={(e) => setEntityDescription(e.target.value)}
                placeholder="Entity haqida qo'shimcha ma'lumot..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleRootInference}
              disabled={isLoading || !entityName.trim()}
            >
              {isLoading ? 'Aniqlanmoqda...' : 'Aniqlash'}
            </button>

            {inferenceResult && (
              <div className="result-card">
                <div className="result-header">
                  <h3>{inferenceResult.entity_name}</h3>
                  <span
                    className="root-badge"
                    style={{ background: rootTypeColors[inferenceResult.root_type] }}
                  >
                    {inferenceResult.root_type}
                  </span>
                </div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${inferenceResult.confidence * 100}%` }}
                  />
                  <span>{(inferenceResult.confidence * 100).toFixed(0)}% ishonch</span>
                </div>
                <p className="reasoning">{inferenceResult.reasoning}</p>
              </div>
            )}
          </div>
        )}

        {/* Causality Extraction */}
        {activeTab === 'causality' && (
          <div className="panel">
            <h2>Kauzal Aloqalarni Aniqlash</h2>
            <p>Entity'lar ro'yxatini kiriting va AI ular orasidagi kauzal aloqalarni topadi</p>

            <div className="form-group">
              <label>Entity'lar (har bir qatorda bittadan)</label>
              <textarea
                value={causalityEntities}
                onChange={(e) => setCausalityEntities(e.target.value)}
                placeholder="Climate Change&#10;Sea Level Rise&#10;Coastal Flooding"
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Tavsiflar (har bir entity uchun)</label>
              <textarea
                value={causalityDescriptions}
                onChange={(e) => setCausalityDescriptions(e.target.value)}
                placeholder="Global temperature increase&#10;Ocean water expansion&#10;Coastal area inundation"
                rows={4}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleCausalityExtraction}
              disabled={isLoading}
            >
              {isLoading ? 'Aniqlanmoqda...' : 'Aloqalarni Topish'}
            </button>

            {causalityResults.length > 0 && (
              <div className="results-list">
                <h3>Topilgan aloqalar:</h3>
                {causalityResults.map((rel, idx) => (
                  <div key={idx} className="causality-card">
                    <div className="causality-flow">
                      <span className="entity">{rel.source}</span>
                      <span className="arrow">→</span>
                      <span className="causality-type">{rel.causality_type}</span>
                      <span className="arrow">→</span>
                      <span className="entity">{rel.target}</span>
                    </div>
                    <div className="confidence-bar small">
                      <div
                        className="confidence-fill"
                        style={{ width: `${rel.confidence * 100}%` }}
                      />
                      <span>{(rel.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p className="reasoning">{rel.reasoning}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Epistemic Annotation */}
        {activeTab === 'epistemic' && (
          <div className="panel">
            <h2>Epistemik Annotatsiya</h2>
            <p>Da'vo yoki bayonot uchun epistemik (bilim asosi) annotatsiya yarating</p>

            <div className="form-group">
              <label>Entity nomi</label>
              <input
                type="text"
                value={epistemicEntity}
                onChange={(e) => setEpistemicEntity(e.target.value)}
                placeholder="masalan: Quantum Entanglement"
              />
            </div>

            <div className="form-group">
              <label>Da'vo/Bayonot</label>
              <textarea
                value={epistemicClaim}
                onChange={(e) => setEpistemicClaim(e.target.value)}
                placeholder="masalan: Entangled particles maintain correlation regardless of distance"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Manba (ixtiyoriy)</label>
              <input
                type="text"
                value={epistemicSource}
                onChange={(e) => setEpistemicSource(e.target.value)}
                placeholder="masalan: Physical Review Letters, 2023"
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleEpistemicAnnotation}
              disabled={isLoading || !epistemicEntity.trim() || !epistemicClaim.trim()}
            >
              {isLoading ? 'Aniqlanmoqda...' : 'Annotatsiya Yaratish'}
            </button>

            {epistemicResult && (
              <div className="result-card">
                <div className="epistemic-metrics">
                  <div className="metric">
                    <span className="label">Aniqlik</span>
                    <span className="value">{(epistemicResult.certainty * 100).toFixed(0)}%</span>
                  </div>
                  <div className="metric">
                    <span className="label">Asos</span>
                    <span className={`basis-badge ${epistemicResult.basis}`}>
                      {epistemicResult.basis}
                    </span>
                  </div>
                </div>
                <p className="reasoning">{epistemicResult.reasoning}</p>
              </div>
            )}
          </div>
        )}

        {/* Conflict Resolution */}
        {activeTab === 'conflict' && (
          <div className="panel">
            <h2>Konfliktni Hal Qilish</h2>
            <p>AI agentlari munozarasi orqali ontologik konfliktlarni hal qiling</p>

            <div className="form-row">
              <div className="form-group">
                <label>Entity A</label>
                <input
                  type="text"
                  value={conflictEntityA}
                  onChange={(e) => setConflictEntityA(e.target.value)}
                  placeholder="Birinchi entity"
                />
              </div>
              <div className="form-group">
                <label>Entity B</label>
                <input
                  type="text"
                  value={conflictEntityB}
                  onChange={(e) => setConflictEntityB(e.target.value)}
                  placeholder="Ikkinchi entity"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Konflikt turi</label>
              <select
                value={conflictType}
                onChange={(e) => setConflictType(e.target.value as ConflictType)}
              >
                <option value="classification">Klassifikatsiya</option>
                <option value="relationship">Munosabat</option>
                <option value="property">Xususiyat</option>
                <option value="definition">Ta'rif</option>
              </select>
            </div>

            <div className="form-group">
              <label>Konflikt tavsifi</label>
              <textarea
                value={conflictDescription}
                onChange={(e) => setConflictDescription(e.target.value)}
                placeholder="Konfliktni batafsil tasvirlab bering..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleConflictResolution}
              disabled={isLoading || !conflictEntityA.trim() || !conflictEntityB.trim()}
            >
              {isLoading ? 'Munozara davom etmoqda...' : 'Hal Qilish'}
            </button>

            {conflictResult && (
              <div className="result-card">
                <div className="conflict-status">
                  <span className={`status-badge ${conflictResult.consensus_reached ? 'success' : 'warning'}`}>
                    {conflictResult.consensus_reached ? 'Konsensusga erishildi' : 'Konsensus yo\'q'}
                  </span>
                  <span className="rounds">{conflictResult.rounds} raund</span>
                </div>
                <div className="resolution">
                  <h4>Yakuniy qaror:</h4>
                  <p>{conflictResult.final_resolution}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Entity Enhancement */}
        {activeTab === 'enhancement' && (
          <div className="panel">
            <h2>Entity Boyitish</h2>
            <p>Mavjud entity'ni AI yordamida qo'shimcha ma'lumotlar bilan boyiting</p>

            <div className="form-group">
              <label>Entity ID (ixtiyoriy)</label>
              <input
                type="text"
                value={enhanceEntityId}
                onChange={(e) => setEnhanceEntityId(e.target.value)}
                placeholder="entity-123"
              />
            </div>

            <div className="form-group">
              <label>Entity nomi</label>
              <input
                type="text"
                value={enhanceEntityName}
                onChange={(e) => setEnhanceEntityName(e.target.value)}
                placeholder="masalan: Machine Learning"
              />
            </div>

            <div className="form-group">
              <label>Tavsif</label>
              <textarea
                value={enhanceDescription}
                onChange={(e) => setEnhanceDescription(e.target.value)}
                placeholder="Entity haqida mavjud ma'lumot..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleEnhancement}
              disabled={isLoading || !enhanceEntityName.trim()}
            >
              {isLoading ? 'Boyitilmoqda...' : 'Boyitish'}
            </button>

            {enhancementResults.length > 0 && (
              <div className="results-list">
                <h3>Boyitishlar:</h3>
                {enhancementResults.map((enh, idx) => (
                  <div key={idx} className="enhancement-card">
                    <div className="enhancement-header">
                      <span className="type-badge">{enh.enhancement_type}</span>
                      <span className="confidence">{(enh.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="enhanced-value">{enh.enhanced_value}</div>
                    <p className="rationale">{enh.rationale}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quality Assessment */}
        {activeTab === 'quality' && (
          <div className="panel">
            <h2>Ontologiya Sifatini Baholash</h2>
            <p>Ontologiya sifatini AI yordamida baholang va tavsiyalar oling</p>

            <div className="form-row">
              <div className="form-group">
                <label>Ontologiya nomi</label>
                <input
                  type="text"
                  value={qualityName}
                  onChange={(e) => setQualityName(e.target.value)}
                  placeholder="masalan: FOAF Ontology"
                />
              </div>
              <div className="form-group">
                <label>Manba</label>
                <input
                  type="text"
                  value={qualitySource}
                  onChange={(e) => setQualitySource(e.target.value)}
                  placeholder="masalan: W3C"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Domen</label>
                <input
                  type="text"
                  value={qualityDomain}
                  onChange={(e) => setQualityDomain(e.target.value)}
                  placeholder="masalan: Social Networks"
                />
              </div>
              <div className="form-group">
                <label>Triple soni</label>
                <input
                  type="number"
                  value={qualityTripleCount}
                  onChange={(e) => setQualityTripleCount(parseInt(e.target.value) || 0)}
                  placeholder="1000"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Namuna klasslar (vergul bilan)</label>
              <input
                type="text"
                value={qualityClasses}
                onChange={(e) => setQualityClasses(e.target.value)}
                placeholder="Person, Organization, Document"
              />
            </div>

            <div className="form-group">
              <label>Namuna xususiyatlar (vergul bilan)</label>
              <input
                type="text"
                value={qualityProperties}
                onChange={(e) => setQualityProperties(e.target.value)}
                placeholder="name, knows, memberOf"
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleQualityAssessment}
              disabled={isLoading || !qualityName.trim()}
            >
              {isLoading ? 'Baholanmoqda...' : 'Baholash'}
            </button>

            {qualityResult && (
              <div className="result-card">
                <div className="quality-score">
                  <div className="score-circle">
                    <span className="score">{(qualityResult.overall_score * 100).toFixed(0)}</span>
                    <span className="label">ball</span>
                  </div>
                  <span className={`recommendation-badge ${qualityResult.recommendation}`}>
                    {qualityResult.recommendation === 'integrate' ? 'Integratsiya qiling' :
                     qualityResult.recommendation === 'review' ? 'Ko\'rib chiqing' : 'Rad eting'}
                  </span>
                </div>

                {qualityResult.issues.length > 0 && (
                  <div className="issues">
                    <h4>Muammolar:</h4>
                    <ul>
                      {qualityResult.issues.map((issue, idx) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {qualityResult.suggestions.length > 0 && (
                  <div className="suggestions">
                    <h4>Tavsiyalar:</h4>
                    <ul>
                      {qualityResult.suggestions.map((sug, idx) => (
                        <li key={idx}>{sug}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        .ai-assistant {
          padding: 1.5rem;
          max-width: 1000px;
          margin: 0 auto;
        }

        .assistant-header {
          margin-bottom: 1.5rem;
        }

        .assistant-header h1 {
          margin: 0 0 0.5rem 0;
          color: var(--primary-color, #2563eb);
        }

        .assistant-header p {
          margin: 0;
          color: var(--text-secondary, #666);
        }

        .tabs {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
          padding-bottom: 0.5rem;
        }

        .tab {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: transparent;
          border: none;
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.2s;
          color: var(--text-secondary, #666);
        }

        .tab:hover {
          background: var(--bg-secondary, #f5f5f5);
        }

        .tab.active {
          background: var(--primary-color, #2563eb);
          color: white;
        }

        .tab-icon {
          font-size: 1.2rem;
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
          margin-bottom: 1rem;
        }

        .error-banner button {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          color: inherit;
        }

        .panel {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .panel h2 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
        }

        .panel > p {
          margin: 0 0 1.5rem 0;
          color: var(--text-secondary, #666);
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: var(--text-primary, #333);
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
          outline: none;
          border-color: var(--primary-color, #2563eb);
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
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

        .result-card {
          margin-top: 1.5rem;
          padding: 1.25rem;
          background: var(--bg-secondary, #f8f9fa);
          border-radius: 8px;
          border: 1px solid var(--border-color, #e0e0e0);
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .result-header h3 {
          margin: 0;
        }

        .root-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 16px;
          color: white;
          font-weight: 600;
          font-size: 0.85rem;
        }

        .confidence-bar {
          position: relative;
          height: 24px;
          background: #e0e0e0;
          border-radius: 12px;
          overflow: hidden;
          margin-bottom: 1rem;
        }

        .confidence-bar.small {
          height: 16px;
          margin: 0.5rem 0;
        }

        .confidence-fill {
          position: absolute;
          left: 0;
          top: 0;
          height: 100%;
          background: linear-gradient(90deg, #22c55e, #16a34a);
          border-radius: 12px;
          transition: width 0.5s ease;
        }

        .confidence-bar span {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 0.75rem;
          font-weight: 600;
          color: #333;
        }

        .reasoning {
          margin: 0;
          color: var(--text-secondary, #666);
          line-height: 1.5;
        }

        .results-list {
          margin-top: 1.5rem;
        }

        .results-list h3 {
          margin: 0 0 1rem 0;
        }

        .causality-card,
        .enhancement-card {
          padding: 1rem;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          margin-bottom: 0.75rem;
        }

        .causality-flow {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .entity {
          padding: 0.25rem 0.5rem;
          background: var(--primary-light, #dbeafe);
          border-radius: 4px;
          font-weight: 500;
        }

        .arrow {
          color: var(--text-secondary, #666);
        }

        .causality-type {
          padding: 0.25rem 0.5rem;
          background: #fef3c7;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 500;
        }

        .epistemic-metrics {
          display: flex;
          gap: 2rem;
          margin-bottom: 1rem;
        }

        .metric {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .metric .label {
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
        }

        .metric .value {
          font-size: 1.5rem;
          font-weight: 600;
        }

        .basis-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 16px;
          font-weight: 500;
          text-transform: capitalize;
        }

        .basis-badge.axiomatic { background: #dbeafe; color: #1e40af; }
        .basis-badge.empirical { background: #dcfce7; color: #166534; }
        .basis-badge.consensus { background: #fef3c7; color: #92400e; }
        .basis-badge.speculative { background: #fae8ff; color: #86198f; }

        .conflict-status {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .status-badge {
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-weight: 500;
        }

        .status-badge.success {
          background: #dcfce7;
          color: #166534;
        }

        .status-badge.warning {
          background: #fef3c7;
          color: #92400e;
        }

        .rounds {
          color: var(--text-secondary, #666);
        }

        .resolution h4 {
          margin: 0 0 0.5rem 0;
        }

        .enhancement-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .type-badge {
          padding: 0.25rem 0.5rem;
          background: var(--primary-light, #dbeafe);
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 500;
        }

        .confidence {
          font-weight: 600;
          color: var(--primary-color, #2563eb);
        }

        .enhanced-value {
          font-weight: 500;
          margin-bottom: 0.5rem;
        }

        .rationale {
          margin: 0;
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
        }

        .quality-score {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .score-circle {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: linear-gradient(135deg, #22c55e, #16a34a);
          color: white;
        }

        .score-circle .score {
          font-size: 1.75rem;
          font-weight: 700;
        }

        .score-circle .label {
          font-size: 0.75rem;
        }

        .recommendation-badge {
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-weight: 500;
        }

        .recommendation-badge.integrate {
          background: #dcfce7;
          color: #166534;
        }

        .recommendation-badge.review {
          background: #fef3c7;
          color: #92400e;
        }

        .recommendation-badge.reject {
          background: #fef2f2;
          color: #dc2626;
        }

        .issues, .suggestions {
          margin-top: 1rem;
        }

        .issues h4, .suggestions h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.9rem;
        }

        .issues ul, .suggestions ul {
          margin: 0;
          padding-left: 1.25rem;
        }

        .issues li, .suggestions li {
          margin-bottom: 0.25rem;
          color: var(--text-secondary, #666);
        }

        @media (max-width: 640px) {
          .form-row {
            grid-template-columns: 1fr;
          }

          .tabs {
            justify-content: center;
          }

          .tab span:not(.tab-icon) {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}

export default AIAssistant;
