import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { causalityApi, rootsApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import EntitySelect from '../components/common/EntitySelect';
import type { CausalityLink, CausalityLinkCreate, CausalityType, Root } from '../types';

const CAUSALITY_TYPES: CausalityType[] = ['EFFICIENT', 'FINAL', 'MATERIAL', 'FORMAL', 'EMERGENT'];

const CAUSALITY_TYPE_COLORS: Record<CausalityType, string> = {
  EFFICIENT: 'badge-primary',
  FINAL: 'badge-success',
  MATERIAL: 'badge-warning',
  FORMAL: 'badge-info',
  EMERGENT: 'badge-danger',
};

function CausalityView() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [filterType, setFilterType] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [newLink, setNewLink] = useState<CausalityLinkCreate>({
    source_entity_id: '',
    target_entity_id: '',
    causality_type: 'EFFICIENT',
    confidence: 1.0,
    description: '',
  });

  const limit = 10;

  const { data, isLoading, error } = useQuery({
    queryKey: ['causalityLinks', page, filterType],
    queryFn: () => causalityApi.list(page * limit, limit, filterType || undefined),
  });

  const { data: summary } = useQuery({
    queryKey: ['causalitySummary'],
    queryFn: causalityApi.getSummary,
  });

  const { data: rootsData } = useQuery({
    queryKey: ['roots', 'entity-select'],
    queryFn: () => rootsApi.list(0, 1000),
    staleTime: 30_000,
  });

  const rootsById = useMemo(() => {
    const map = new Map<string, Root>();
    for (const root of rootsData?.items ?? []) {
      map.set(root.id, root);
    }
    return map;
  }, [rootsData]);

  const createMutation = useMutation({
    mutationFn: causalityApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['causalityLinks'] });
      queryClient.invalidateQueries({ queryKey: ['causalitySummary'] });
      setShowModal(false);
      setNewLink({
        source_entity_id: '',
        target_entity_id: '',
        causality_type: 'EFFICIENT',
        confidence: 1.0,
        description: '',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: causalityApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['causalityLinks'] });
      queryClient.invalidateQueries({ queryKey: ['causalitySummary'] });
    },
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load causality links" />;

  const handleCreate = () => {
    if (newLink.source_entity_id.trim() && newLink.target_entity_id.trim()) {
      createMutation.mutate(newLink);
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this causality link?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Causality Links</h1>
        <p className="page-subtitle">Manage causal relationships between entities</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Links</div>
          <div className="stat-value">{summary?.total_count || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Confidence</div>
          <div className="stat-value">{((summary?.avg_confidence || 0) * 100).toFixed(1)}%</div>
        </div>
        {CAUSALITY_TYPES.slice(0, 3).map((type) => (
          <div key={type} className="stat-card">
            <div className="stat-label">{type}</div>
            <div className="stat-value">{summary?.by_type[type] || 0}</div>
          </div>
        ))}
      </div>

      {/* Actions Bar */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              className="form-select"
              style={{ width: '200px' }}
              value={filterType}
              onChange={(e) => {
                setFilterType(e.target.value);
                setPage(0);
              }}
            >
              <option value="">All Types</option>
              {CAUSALITY_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Create Link
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Target</th>
                <th>Type</th>
                <th>Confidence</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((link: CausalityLink) => (
                <tr key={link.id}>
                  <td>
                    {rootsById.get(link.source_entity_id)?.name ?? (
                      <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                        {link.source_entity_id.slice(0, 8)}...
                      </span>
                    )}
                  </td>
                  <td>
                    {rootsById.get(link.target_entity_id)?.name ?? (
                      <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                        {link.target_entity_id.slice(0, 8)}...
                      </span>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${CAUSALITY_TYPE_COLORS[link.causality_type]}`}>
                      {link.causality_type}
                    </span>
                  </td>
                  <td>{(link.confidence * 100).toFixed(0)}%</td>
                  <td>{new Date(link.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(link.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                    No causality links found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            Previous
          </button>
          <span className="pagination-info">
            Page {page + 1} of {Math.ceil((data?.total || 0) / limit)}
          </span>
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => p + 1)}
            disabled={!data?.has_more}
          >
            Next
          </button>
        </div>
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create Causality Link</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Source Entity</label>
              <EntitySelect
                value={newLink.source_entity_id}
                onChange={(entityId) => setNewLink({ ...newLink, source_entity_id: entityId })}
                placeholder="Select source entity…"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Target Entity</label>
              <EntitySelect
                value={newLink.target_entity_id}
                onChange={(entityId) => setNewLink({ ...newLink, target_entity_id: entityId })}
                placeholder="Select target entity…"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Causality Type</label>
              <select
                className="form-select"
                value={newLink.causality_type}
                onChange={(e) =>
                  setNewLink({ ...newLink, causality_type: e.target.value as CausalityType })
                }
              >
                {CAUSALITY_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Confidence ({((newLink.confidence || 1) * 100).toFixed(0)}%)</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={newLink.confidence}
                onChange={(e) => setNewLink({ ...newLink, confidence: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <input
                type="text"
                className="form-input"
                value={newLink.description || ''}
                onChange={(e) => setNewLink({ ...newLink, description: e.target.value })}
                placeholder="Optional description"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleCreate}
                disabled={
                  !newLink.source_entity_id.trim() ||
                  !newLink.target_entity_id.trim() ||
                  createMutation.isPending
                }
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CausalityView;
