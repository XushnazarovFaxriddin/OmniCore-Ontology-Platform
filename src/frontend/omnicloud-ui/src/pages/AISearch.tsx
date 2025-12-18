import { useState } from 'react';
import { aiApi, rootsApi, causalityApi, epistemicApi } from '../api/client';
import type { Root, CausalityLink, EpistemicAnnotation } from '../types';

interface SearchResult {
  interpreted_query: string;
  suggested_entities: string[];
  related_concepts: string[];
  search_tips: string[];
}

interface CombinedResults {
  roots: Root[];
  causality: CausalityLink[];
  epistemic: EpistemicAnnotation[];
}

function AISearch() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [aiResult, setAiResult] = useState<SearchResult | null>(null);
  const [combinedResults, setCombinedResults] = useState<CombinedResults | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'roots' | 'causality' | 'epistemic'>('all');
  const [entityTypes, setEntityTypes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const entityTypeOptions = ['EXTANT', 'ABSTRACT', 'MENTAL', 'FICTIVE'];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setAiResult(null);
    setCombinedResults(null);

    try {
      // First, get AI interpretation
      const aiResponse = await aiApi.smartSearch(
        query,
        entityTypes.length > 0 ? entityTypes : undefined
      );

      // Parse AI response
      let parsed: SearchResult;
      try {
        const jsonMatch = aiResponse.response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          parsed = JSON.parse(jsonMatch[0]);
        } else {
          parsed = {
            interpreted_query: query,
            suggested_entities: [],
            related_concepts: [],
            search_tips: [],
          };
        }
      } catch {
        parsed = {
          interpreted_query: query,
          suggested_entities: [],
          related_concepts: [],
          search_tips: [],
        };
      }
      setAiResult(parsed);

      // Then, search actual data
      const [rootsData, causalityData, epistemicData] = await Promise.all([
        rootsApi.list(0, 20).catch(() => ({ items: [] })),
        causalityApi.list(0, 20).catch(() => ({ items: [] })),
        epistemicApi.list(0, 20).catch(() => ({ items: [] })),
      ]);

      // Filter results based on query
      const queryLower = query.toLowerCase();
      const filteredRoots = rootsData.items.filter(
        (r) =>
          r.name.toLowerCase().includes(queryLower) ||
          r.description?.toLowerCase().includes(queryLower) ||
          (entityTypes.length === 0 || entityTypes.includes(r.root_type))
      );

      const filteredCausality = causalityData.items.filter(
        (c) =>
          c.description?.toLowerCase().includes(queryLower) ||
          c.source_entity_id.toLowerCase().includes(queryLower) ||
          c.target_entity_id.toLowerCase().includes(queryLower)
      );

      const filteredEpistemic = epistemicData.items.filter(
        (e) =>
          e.note?.toLowerCase().includes(queryLower) ||
          e.source?.toLowerCase().includes(queryLower)
      );

      setCombinedResults({
        roots: filteredRoots,
        causality: filteredCausality,
        epistemic: filteredEpistemic,
      });
    } catch (err) {
      setError('Qidirishda xatolik yuz berdi');
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const toggleEntityType = (type: string) => {
    setEntityTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const totalResults = combinedResults
    ? combinedResults.roots.length +
      combinedResults.causality.length +
      combinedResults.epistemic.length
    : 0;

  const rootTypeColors: Record<string, string> = {
    EXTANT: '#22c55e',
    ABSTRACT: '#3b82f6',
    MENTAL: '#a855f7',
    FICTIVE: '#f97316',
  };

  return (
    <div className="ai-search">
      <header className="search-header">
        <h1>AI Qidiruv</h1>
        <p>Ontologiya ma'lumotlarini AI yordamida qidiring</p>
      </header>

      {/* Search Box */}
      <div className="search-box">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Qidiruv so'rovini kiriting..."
            className="search-input"
          />
          <button
            className="search-btn"
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? 'Qidirilmoqda...' : 'Qidirish'}
          </button>
        </div>

        {/* Entity Type Filters */}
        <div className="filters">
          <span className="filter-label">Filtr:</span>
          {entityTypeOptions.map((type) => (
            <button
              key={type}
              className={`filter-btn ${entityTypes.includes(type) ? 'active' : ''}`}
              onClick={() => toggleEntityType(type)}
              style={{
                borderColor: entityTypes.includes(type) ? rootTypeColors[type] : undefined,
                background: entityTypes.includes(type) ? `${rootTypeColors[type]}20` : undefined,
              }}
            >
              {type}
            </button>
          ))}
          {entityTypes.length > 0 && (
            <button className="clear-btn" onClick={() => setEntityTypes([])}>
              Tozalash
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* AI Interpretation */}
      {aiResult && (
        <div className="ai-interpretation">
          <h3>AI Tahlili</h3>
          <div className="interpretation-content">
            <div className="interpretation-item">
              <span className="label">Tushunilgan so'rov:</span>
              <span className="value">{aiResult.interpreted_query}</span>
            </div>

            {aiResult.suggested_entities.length > 0 && (
              <div className="interpretation-item">
                <span className="label">Tavsiya etilgan entity'lar:</span>
                <div className="tags">
                  {aiResult.suggested_entities.map((entity, idx) => (
                    <span key={idx} className="tag suggested">{entity}</span>
                  ))}
                </div>
              </div>
            )}

            {aiResult.related_concepts.length > 0 && (
              <div className="interpretation-item">
                <span className="label">Bog'liq tushunchalar:</span>
                <div className="tags">
                  {aiResult.related_concepts.map((concept, idx) => (
                    <span key={idx} className="tag related">{concept}</span>
                  ))}
                </div>
              </div>
            )}

            {aiResult.search_tips.length > 0 && (
              <div className="interpretation-item">
                <span className="label">Qidiruv bo'yicha maslahatlar:</span>
                <ul className="tips">
                  {aiResult.search_tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Results */}
      {combinedResults && (
        <div className="results-section">
          <div className="results-header">
            <h3>Natijalar ({totalResults})</h3>
            <div className="results-tabs">
              <button
                className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                Hammasi ({totalResults})
              </button>
              <button
                className={`tab ${activeTab === 'roots' ? 'active' : ''}`}
                onClick={() => setActiveTab('roots')}
              >
                Root'lar ({combinedResults.roots.length})
              </button>
              <button
                className={`tab ${activeTab === 'causality' ? 'active' : ''}`}
                onClick={() => setActiveTab('causality')}
              >
                Kauzallik ({combinedResults.causality.length})
              </button>
              <button
                className={`tab ${activeTab === 'epistemic' ? 'active' : ''}`}
                onClick={() => setActiveTab('epistemic')}
              >
                Epistemik ({combinedResults.epistemic.length})
              </button>
            </div>
          </div>

          <div className="results-list">
            {/* Roots */}
            {(activeTab === 'all' || activeTab === 'roots') &&
              combinedResults.roots.map((root) => (
                <div key={root.id} className="result-card root-card">
                  <div className="card-type">Root</div>
                  <div className="card-header">
                    <h4>{root.name}</h4>
                    <span
                      className="root-badge"
                      style={{ background: rootTypeColors[root.root_type] }}
                    >
                      {root.root_type}
                    </span>
                  </div>
                  {root.description && (
                    <p className="card-description">{root.description}</p>
                  )}
                  <div className="card-meta">
                    <span>ID: {root.id.slice(0, 8)}...</span>
                    <span>{new Date(root.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}

            {/* Causality */}
            {(activeTab === 'all' || activeTab === 'causality') &&
              combinedResults.causality.map((link) => (
                <div key={link.id} className="result-card causality-card">
                  <div className="card-type">Kauzal Aloqa</div>
                  <div className="causality-flow">
                    <span className="entity">{link.source_entity_id.slice(0, 12)}...</span>
                    <span className="arrow">→</span>
                    <span className="causality-type">{link.causality_type}</span>
                    <span className="arrow">→</span>
                    <span className="entity">{link.target_entity_id.slice(0, 12)}...</span>
                  </div>
                  {link.description && (
                    <p className="card-description">{link.description}</p>
                  )}
                  <div className="card-meta">
                    <span>Ishonch: {(link.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}

            {/* Epistemic */}
            {(activeTab === 'all' || activeTab === 'epistemic') &&
              combinedResults.epistemic.map((annotation) => (
                <div key={annotation.id} className="result-card epistemic-card">
                  <div className="card-type">Epistemik</div>
                  <div className="epistemic-header">
                    <span className={`basis-badge ${annotation.basis}`}>
                      {annotation.basis}
                    </span>
                    <span className="certainty">
                      {(annotation.certainty * 100).toFixed(0)}% aniqlik
                    </span>
                  </div>
                  {annotation.note && (
                    <p className="card-description">{annotation.note}</p>
                  )}
                  {annotation.source && (
                    <div className="card-meta">
                      <span>Manba: {annotation.source}</span>
                    </div>
                  )}
                </div>
              ))}

            {totalResults === 0 && (
              <div className="no-results">
                <span className="no-results-icon">🔍</span>
                <p>Hech narsa topilmadi</p>
                <p className="hint">Boshqa kalit so'zlar bilan qidirib ko'ring</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isSearching && !aiResult && !combinedResults && (
        <div className="empty-state">
          <span className="empty-icon">🔍</span>
          <h3>Qidiruvni boshlang</h3>
          <p>Ontologiya ma'lumotlarini qidirish uchun so'rov kiriting</p>
          <div className="suggestions">
            <p>Namuna so'rovlar:</p>
            <div className="suggestion-chips">
              <button onClick={() => setQuery('Abstract entities')}>Abstract entities</button>
              <button onClick={() => setQuery('Causal relationships')}>Causal relationships</button>
              <button onClick={() => setQuery('High confidence')}>High confidence</button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .ai-search {
          padding: 1.5rem;
          max-width: 1000px;
          margin: 0 auto;
        }

        .search-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .search-header h1 {
          margin: 0 0 0.5rem 0;
          color: var(--primary-color, #2563eb);
        }

        .search-header p {
          margin: 0;
          color: var(--text-secondary, #666);
        }

        .search-box {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
          margin-bottom: 1.5rem;
        }

        .search-input-wrapper {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.5rem;
          background: var(--bg-secondary, #f5f5f5);
          border-radius: 12px;
        }

        .search-icon {
          font-size: 1.25rem;
          padding-left: 0.5rem;
        }

        .search-input {
          flex: 1;
          padding: 0.75rem;
          border: none;
          background: transparent;
          font-size: 1rem;
          outline: none;
        }

        .search-btn {
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #2563eb);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .search-btn:hover:not(:disabled) {
          background: var(--primary-dark, #1d4ed8);
        }

        .search-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .filters {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 1rem;
          flex-wrap: wrap;
        }

        .filter-label {
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
        }

        .filter-btn {
          padding: 0.4rem 0.75rem;
          background: white;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 16px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          border-color: var(--primary-color, #2563eb);
        }

        .filter-btn.active {
          font-weight: 500;
        }

        .clear-btn {
          padding: 0.4rem 0.75rem;
          background: transparent;
          border: none;
          color: var(--primary-color, #2563eb);
          font-size: 0.85rem;
          cursor: pointer;
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

        .ai-interpretation {
          background: linear-gradient(135deg, #eff6ff, #f0fdf4);
          border-radius: 12px;
          padding: 1.25rem;
          margin-bottom: 1.5rem;
          border: 1px solid #dbeafe;
        }

        .ai-interpretation h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: var(--primary-color, #2563eb);
        }

        .interpretation-content {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .interpretation-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .interpretation-item .label {
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
        }

        .interpretation-item .value {
          font-weight: 500;
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .tag {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .tag.suggested {
          background: #dbeafe;
          color: #1e40af;
        }

        .tag.related {
          background: #dcfce7;
          color: #166534;
        }

        .tips {
          margin: 0;
          padding-left: 1.25rem;
        }

        .tips li {
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
          margin-bottom: 0.25rem;
        }

        .results-section {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .results-header {
          padding: 1rem 1.25rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
        }

        .results-header h3 {
          margin: 0 0 0.75rem 0;
        }

        .results-tabs {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .results-tabs .tab {
          padding: 0.5rem 1rem;
          background: transparent;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .results-tabs .tab:hover {
          border-color: var(--primary-color, #2563eb);
        }

        .results-tabs .tab.active {
          background: var(--primary-color, #2563eb);
          color: white;
          border-color: var(--primary-color, #2563eb);
        }

        .results-list {
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .result-card {
          padding: 1rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          transition: box-shadow 0.2s;
        }

        .result-card:hover {
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .card-type {
          font-size: 0.75rem;
          color: var(--text-secondary, #666);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 0.5rem;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .card-header h4 {
          margin: 0;
        }

        .root-badge {
          padding: 0.2rem 0.5rem;
          border-radius: 12px;
          color: white;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .card-description {
          margin: 0 0 0.5rem 0;
          color: var(--text-secondary, #666);
          font-size: 0.9rem;
          line-height: 1.4;
        }

        .card-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.8rem;
          color: var(--text-tertiary, #999);
        }

        .causality-flow {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex-wrap: wrap;
          margin-bottom: 0.5rem;
        }

        .causality-flow .entity {
          padding: 0.25rem 0.5rem;
          background: var(--bg-secondary, #f5f5f5);
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .causality-flow .arrow {
          color: var(--text-secondary, #666);
        }

        .causality-flow .causality-type {
          padding: 0.25rem 0.5rem;
          background: #fef3c7;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .epistemic-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .basis-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .basis-badge.axiomatic { background: #dbeafe; color: #1e40af; }
        .basis-badge.empirical { background: #dcfce7; color: #166534; }
        .basis-badge.consensus { background: #fef3c7; color: #92400e; }
        .basis-badge.speculative { background: #fae8ff; color: #86198f; }

        .certainty {
          font-size: 0.85rem;
          color: var(--text-secondary, #666);
        }

        .no-results {
          text-align: center;
          padding: 3rem 1rem;
        }

        .no-results-icon {
          font-size: 3rem;
          opacity: 0.5;
        }

        .no-results p {
          margin: 0.5rem 0;
          color: var(--text-secondary, #666);
        }

        .no-results .hint {
          font-size: 0.9rem;
          color: var(--text-tertiary, #999);
        }

        .empty-state {
          text-align: center;
          padding: 4rem 1rem;
          background: white;
          border-radius: 12px;
        }

        .empty-icon {
          font-size: 4rem;
          opacity: 0.3;
        }

        .empty-state h3 {
          margin: 1rem 0 0.5rem 0;
        }

        .empty-state > p {
          margin: 0;
          color: var(--text-secondary, #666);
        }

        .suggestions {
          margin-top: 2rem;
        }

        .suggestions p {
          margin: 0 0 0.75rem 0;
          font-size: 0.9rem;
          color: var(--text-secondary, #666);
        }

        .suggestion-chips {
          display: flex;
          justify-content: center;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .suggestion-chips button {
          padding: 0.5rem 1rem;
          background: var(--bg-secondary, #f5f5f5);
          border: none;
          border-radius: 16px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .suggestion-chips button:hover {
          background: #dbeafe;
        }

        @media (max-width: 640px) {
          .search-input-wrapper {
            flex-direction: column;
          }

          .search-input {
            width: 100%;
          }

          .search-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default AISearch;
