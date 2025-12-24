import { useState } from 'react';
import { aiApi } from '../api/client';
import EntitySelect from '../components/common/EntitySelect';
import type { RootType, EpistemicBasis, ConflictType } from '../types';

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
      setError('Failed to infer root type. Ensure Ollama is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCausalityExtraction = async () => {
    const entities = causalityEntities.split('\n').filter(e => e.trim());
    const descriptions = causalityDescriptions.split('\n').filter(d => d.trim());
    if (entities.length < 2) {
      setError('At least 2 entities required');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const result = await aiApi.extractCausality(entities, descriptions);
      setCausalityResults(result.relationships);
    } catch (err) {
      setError('Failed to extract causality relationships');
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
      setError('Failed to generate epistemic annotation');
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
      setError('Failed to resolve conflict');
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
      setError('Failed to enhance entity');
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
      setError('Failed to assess quality');
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'root-inference' as TabType, label: 'Root Type', icon: '🌳', desc: 'Classify entities' },
    { id: 'causality' as TabType, label: 'Causality', icon: '🔗', desc: 'Extract relationships' },
    { id: 'epistemic' as TabType, label: 'Epistemic', icon: '📚', desc: 'Annotate knowledge' },
    { id: 'conflict' as TabType, label: 'Conflict', icon: '⚖️', desc: 'Resolve disputes' },
    { id: 'enhancement' as TabType, label: 'Enhance', icon: '✨', desc: 'Enrich entities' },
    { id: 'quality' as TabType, label: 'Quality', icon: '📊', desc: 'Assess ontologies' },
  ];

  const rootTypeColors: Record<string, string> = {
    EXTANT: '#22c55e',
    ABSTRACT: '#3b82f6',
    MENTAL: '#a855f7',
    FICTIVE: '#f97316',
  };

  const rootTypeDescriptions: Record<string, string> = {
    EXTANT: 'Physical, observable entities that exist in space-time',
    ABSTRACT: 'Non-physical concepts, ideas, and universals',
    MENTAL: 'Mind-dependent entities like beliefs and emotions',
    FICTIVE: 'Fictional or imaginary entities',
  };

  return (
    <div className="ai-assistant">
      <header className="assistant-header">
        <h1>AI Assistant</h1>
        <p>Ontology operations powered by Ollama SLM</p>
      </header>

      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            title={tab.desc}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="tab-content">
        {/* Root Type Inference */}
        {activeTab === 'root-inference' && (
          <div className="panel">
            <h2>Root Type Inference</h2>
            <p>Classify an entity into one of four fundamental ontological categories using AI analysis.</p>

            <div className="type-legend">
              {Object.entries(rootTypeColors).map(([type, color]) => (
                <div key={type} className="legend-item">
                  <span className="legend-color" style={{ background: color }} />
                  <span className="legend-label">{type}</span>
                  <span className="legend-desc">{rootTypeDescriptions[type]}</span>
                </div>
              ))}
            </div>

            <div className="form-group">
              <label>Entity Name *</label>
              <input
                type="text"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
                placeholder="e.g., Electron, Democracy, Happiness, Unicorn"
              />
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={entityDescription}
                onChange={(e) => setEntityDescription(e.target.value)}
                placeholder="Additional context about the entity..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleRootInference}
              disabled={isLoading || !entityName.trim()}
            >
              {isLoading ? 'Analyzing...' : 'Infer Root Type'}
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
                  <span>{(inferenceResult.confidence * 100).toFixed(0)}% confidence</span>
                </div>
                <div className="reasoning-box">
                  <h4>AI Reasoning</h4>
                  <p>{inferenceResult.reasoning}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Causality Extraction */}
        {activeTab === 'causality' && (
          <div className="panel">
            <h2>Causality Extraction</h2>
            <p>Discover causal relationships between entities using AI analysis (Efficient, Final, Material, Formal, Emergent).</p>

            <div className="form-group">
              <label>Entities (one per line) *</label>
              <textarea
                value={causalityEntities}
                onChange={(e) => setCausalityEntities(e.target.value)}
                placeholder="Climate Change&#10;Sea Level Rise&#10;Coastal Flooding&#10;Economic Damage"
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Descriptions (one per entity)</label>
              <textarea
                value={causalityDescriptions}
                onChange={(e) => setCausalityDescriptions(e.target.value)}
                placeholder="Global temperature increase from greenhouse gases&#10;Ocean water expansion and ice melt&#10;Coastal area inundation&#10;Property and infrastructure losses"
                rows={4}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleCausalityExtraction}
              disabled={isLoading}
            >
              {isLoading ? 'Extracting...' : 'Extract Relationships'}
            </button>

            {causalityResults.length > 0 && (
              <div className="results-list">
                <h3>Discovered Relationships ({causalityResults.length})</h3>
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
            <h2>Epistemic Annotation</h2>
            <p>Generate knowledge certainty annotations for claims (Axiomatic, Empirical, Consensus, Speculative).</p>

            <div className="form-group">
              <label>Entity Name *</label>
              <input
                type="text"
                value={epistemicEntity}
                onChange={(e) => setEpistemicEntity(e.target.value)}
                placeholder="e.g., Quantum Entanglement"
              />
            </div>

            <div className="form-group">
              <label>Claim/Statement *</label>
              <textarea
                value={epistemicClaim}
                onChange={(e) => setEpistemicClaim(e.target.value)}
                placeholder="e.g., Entangled particles maintain correlation regardless of distance"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Source (optional)</label>
              <input
                type="text"
                value={epistemicSource}
                onChange={(e) => setEpistemicSource(e.target.value)}
                placeholder="e.g., Physical Review Letters, 2023"
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleEpistemicAnnotation}
              disabled={isLoading || !epistemicEntity.trim() || !epistemicClaim.trim()}
            >
              {isLoading ? 'Analyzing...' : 'Generate Annotation'}
            </button>

            {epistemicResult && (
              <div className="result-card">
                <div className="epistemic-metrics">
                  <div className="metric">
                    <span className="metric-value">{(epistemicResult.certainty * 100).toFixed(0)}%</span>
                    <span className="metric-label">Certainty</span>
                  </div>
                  <div className="metric">
                    <span className={`basis-badge ${epistemicResult.basis}`}>
                      {epistemicResult.basis}
                    </span>
                    <span className="metric-label">Epistemic Basis</span>
                  </div>
                </div>
                <div className="reasoning-box">
                  <h4>Analysis</h4>
                  <p>{epistemicResult.reasoning}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Conflict Resolution */}
        {activeTab === 'conflict' && (
          <div className="panel">
            <h2>Conflict Resolution</h2>
            <p>Resolve ontological conflicts through multi-agent AI debate (Platonist, Nominalist, Pragmatist perspectives).</p>

            <div className="form-row">
              <div className="form-group">
                <label>Entity A *</label>
                <input
                  type="text"
                  value={conflictEntityA}
                  onChange={(e) => setConflictEntityA(e.target.value)}
                  placeholder="First entity"
                />
              </div>
              <div className="form-group">
                <label>Entity B *</label>
                <input
                  type="text"
                  value={conflictEntityB}
                  onChange={(e) => setConflictEntityB(e.target.value)}
                  placeholder="Second entity"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Conflict Type</label>
              <select
                value={conflictType}
                onChange={(e) => setConflictType(e.target.value as ConflictType)}
              >
                <option value="classification">Classification - Disagreement on entity type</option>
                <option value="relationship">Relationship - Conflicting connections</option>
                <option value="property">Property - Attribute conflicts</option>
                <option value="definition">Definition - Semantic disagreements</option>
              </select>
            </div>

            <div className="form-group">
              <label>Conflict Description</label>
              <textarea
                value={conflictDescription}
                onChange={(e) => setConflictDescription(e.target.value)}
                placeholder="Describe the nature of the conflict in detail..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleConflictResolution}
              disabled={isLoading || !conflictEntityA.trim() || !conflictEntityB.trim()}
            >
              {isLoading ? 'Debate in progress...' : 'Resolve Conflict'}
            </button>

            {conflictResult && (
              <div className="result-card">
                <div className="conflict-status">
                  <span className={`status-badge ${conflictResult.consensus_reached ? 'success' : 'warning'}`}>
                    {conflictResult.consensus_reached ? '✓ Consensus Reached' : '⚠ No Consensus'}
                  </span>
                  <span className="rounds">{conflictResult.rounds} debate rounds</span>
                </div>
                <div className="resolution-box">
                  <h4>Final Resolution</h4>
                  <p>{conflictResult.final_resolution}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Entity Enhancement */}
        {activeTab === 'enhancement' && (
          <div className="panel">
            <h2>Entity Enhancement</h2>
            <p>Enrich existing entities with AI-derived insights and metadata.</p>

            <div className="form-group">
              <label>Select Existing Entity (optional)</label>
              <EntitySelect
                value={enhanceEntityId}
                onChange={(entityId, entity) => {
                  setEnhanceEntityId(entityId);
                  if (entity) {
                    setEnhanceEntityName(entity.name);
                    setEnhanceDescription(entity.description ?? '');
                  }
                }}
                placeholder="Pick an entity from Roots…"
                searchPlaceholder="Search roots…"
              />
            </div>

            <div className="form-group">
              <label>Entity Name *</label>
              <input
                type="text"
                value={enhanceEntityName}
                onChange={(e) => setEnhanceEntityName(e.target.value)}
                placeholder="e.g., Machine Learning"
              />
            </div>

            <div className="form-group">
              <label>Current Description</label>
              <textarea
                value={enhanceDescription}
                onChange={(e) => setEnhanceDescription(e.target.value)}
                placeholder="Existing information about the entity..."
                rows={3}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleEnhancement}
              disabled={isLoading || !enhanceEntityName.trim()}
            >
              {isLoading ? 'Enhancing...' : 'Enhance Entity'}
            </button>

            {enhancementResults.length > 0 && (
              <div className="results-list">
                <h3>Enhancements ({enhancementResults.length})</h3>
                {enhancementResults.map((enh, idx) => (
                  <div key={idx} className="enhancement-card">
                    <div className="enhancement-header">
                      <span className="type-badge">{enh.enhancement_type}</span>
                      <span className="confidence">{(enh.confidence * 100).toFixed(0)}% confidence</span>
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
            <h2>Ontology Quality Assessment</h2>
            <p>Evaluate ontology quality using AI analysis and get integration recommendations.</p>

            <div className="form-row">
              <div className="form-group">
                <label>Ontology Name *</label>
                <input
                  type="text"
                  value={qualityName}
                  onChange={(e) => setQualityName(e.target.value)}
                  placeholder="e.g., FOAF Ontology"
                />
              </div>
              <div className="form-group">
                <label>Source</label>
                <input
                  type="text"
                  value={qualitySource}
                  onChange={(e) => setQualitySource(e.target.value)}
                  placeholder="e.g., W3C"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Domain</label>
                <input
                  type="text"
                  value={qualityDomain}
                  onChange={(e) => setQualityDomain(e.target.value)}
                  placeholder="e.g., Social Networks"
                />
              </div>
              <div className="form-group">
                <label>Triple Count</label>
                <input
                  type="number"
                  value={qualityTripleCount}
                  onChange={(e) => setQualityTripleCount(parseInt(e.target.value) || 0)}
                  placeholder="1000"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Sample Classes (comma-separated)</label>
              <input
                type="text"
                value={qualityClasses}
                onChange={(e) => setQualityClasses(e.target.value)}
                placeholder="Person, Organization, Document"
              />
            </div>

            <div className="form-group">
              <label>Sample Properties (comma-separated)</label>
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
              {isLoading ? 'Assessing...' : 'Assess Quality'}
            </button>

            {qualityResult && (
              <div className="result-card">
                <div className="quality-score">
                  <div className="score-circle">
                    <span className="score">{(qualityResult.overall_score * 100).toFixed(0)}</span>
                    <span className="label">/100</span>
                  </div>
                  <span className={`recommendation-badge ${qualityResult.recommendation}`}>
                    {qualityResult.recommendation === 'integrate' ? '✓ Integrate' :
                     qualityResult.recommendation === 'review' ? '⚠ Review Required' : '✗ Reject'}
                  </span>
                </div>

                {qualityResult.issues.length > 0 && (
                  <div className="issues-box">
                    <h4>Issues Found</h4>
                    <ul>
                      {qualityResult.issues.map((issue, idx) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {qualityResult.suggestions.length > 0 && (
                  <div className="suggestions-box">
                    <h4>Recommendations</h4>
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
          margin: 0 0 0.25rem 0;
          color: var(--primary-color, #6366f1);
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
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .tab {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.25rem;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .tab:hover {
          border-color: var(--primary-color, #6366f1);
        }

        .tab.active {
          background: var(--primary-color, #6366f1);
          color: white;
          border-color: var(--primary-color, #6366f1);
        }

        .tab-icon {
          font-size: 1.1rem;
        }

        .tab-label {
          font-weight: 500;
        }

        .error-banner {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #dc2626;
          margin-bottom: 1.5rem;
        }

        .error-icon {
          font-size: 1.25rem;
        }

        .error-banner button {
          margin-left: auto;
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
          color: var(--text-primary, #1e293b);
        }

        .panel > p {
          margin: 0 0 1.5rem 0;
          color: var(--text-secondary, #666);
        }

        .type-legend {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 0.75rem;
          margin-bottom: 1.5rem;
          padding: 1rem;
          background: var(--bg-secondary, #f8fafc);
          border-radius: 8px;
        }

        .legend-item {
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
        }

        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 3px;
          margin-top: 4px;
          flex-shrink: 0;
        }

        .legend-label {
          font-weight: 600;
          font-size: 0.85rem;
          min-width: 70px;
        }

        .legend-desc {
          font-size: 0.8rem;
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
          font-size: 0.9rem;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          font-size: 0.95rem;
          transition: border-color 0.2s;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
          outline: none;
          border-color: var(--primary-color, #6366f1);
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .btn-primary {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #6366f1);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
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
          font-size: 1.1rem;
        }

        .root-badge {
          padding: 0.35rem 0.85rem;
          border-radius: 16px;
          color: white;
          font-weight: 600;
          font-size: 0.85rem;
        }

        .confidence-bar {
          position: relative;
          height: 28px;
          background: #e0e0e0;
          border-radius: 14px;
          overflow: hidden;
          margin-bottom: 1rem;
        }

        .confidence-bar.small {
          height: 20px;
          margin: 0.75rem 0;
          border-radius: 10px;
        }

        .confidence-fill {
          position: absolute;
          left: 0;
          top: 0;
          height: 100%;
          background: linear-gradient(90deg, #22c55e, #16a34a);
          border-radius: inherit;
          transition: width 0.5s ease;
        }

        .confidence-bar span {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 0.8rem;
          font-weight: 600;
          color: #333;
        }

        .reasoning-box,
        .resolution-box,
        .issues-box,
        .suggestions-box {
          margin-top: 1rem;
          padding: 1rem;
          background: white;
          border-radius: 6px;
          border: 1px solid var(--border-color, #e0e0e0);
        }

        .reasoning-box h4,
        .resolution-box h4,
        .issues-box h4,
        .suggestions-box h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
        }

        .reasoning-box p,
        .resolution-box p {
          margin: 0;
          line-height: 1.5;
        }

        .issues-box ul,
        .suggestions-box ul {
          margin: 0;
          padding-left: 1.25rem;
        }

        .issues-box li,
        .suggestions-box li {
          margin-bottom: 0.25rem;
        }

        .results-list {
          margin-top: 1.5rem;
        }

        .results-list h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
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
          padding: 0.3rem 0.6rem;
          background: #dbeafe;
          border-radius: 4px;
          font-weight: 500;
          font-size: 0.9rem;
        }

        .arrow {
          color: var(--text-secondary, #666);
          font-size: 1.2rem;
        }

        .causality-type {
          padding: 0.3rem 0.6rem;
          background: #fef3c7;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .reasoning {
          margin: 0.75rem 0 0 0;
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
          line-height: 1.4;
        }

        .epistemic-metrics {
          display: flex;
          gap: 2rem;
          margin-bottom: 1rem;
        }

        .metric {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
        }

        .metric-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--primary-color, #6366f1);
        }

        .metric-label {
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
        }

        .basis-badge {
          padding: 0.35rem 0.85rem;
          border-radius: 16px;
          font-weight: 600;
          text-transform: capitalize;
          font-size: 0.9rem;
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
          font-weight: 600;
          font-size: 0.9rem;
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
          font-size: 0.9rem;
        }

        .enhancement-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .type-badge {
          padding: 0.25rem 0.6rem;
          background: #dbeafe;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .confidence {
          font-size: 0.85rem;
          color: var(--primary-color, #6366f1);
          font-weight: 500;
        }

        .enhanced-value {
          font-weight: 500;
          margin-bottom: 0.5rem;
          font-size: 1rem;
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
          align-items: baseline;
          justify-content: center;
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: linear-gradient(135deg, #22c55e, #16a34a);
          color: white;
        }

        .score-circle .score {
          font-size: 2.25rem;
          font-weight: 700;
        }

        .score-circle .label {
          font-size: 1rem;
          opacity: 0.8;
        }

        .recommendation-badge {
          padding: 0.5rem 1.25rem;
          border-radius: 8px;
          font-weight: 600;
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

        @media (max-width: 640px) {
          .form-row {
            grid-template-columns: 1fr;
          }

          .tabs {
            justify-content: center;
          }

          .tab .tab-label {
            display: none;
          }

          .epistemic-metrics {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
}

export default AIAssistant;
