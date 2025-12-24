import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { epistemicApi, rootsApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import EntitySelect from '../components/common/EntitySelect';
import type { EpistemicAnnotation, EpistemicAnnotationCreate, EpistemicBasis, Root } from '../types';

const EPISTEMIC_BASES: EpistemicBasis[] = ['axiomatic', 'empirical', 'consensus', 'speculative'];

const BASIS_COLORS: Record<EpistemicBasis, string> = {
  axiomatic: 'badge-primary',
  empirical: 'badge-success',
  consensus: 'badge-info',
  speculative: 'badge-warning',
};

function EpistemicView() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [filterBasis, setFilterBasis] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [newAnnotation, setNewAnnotation] = useState<EpistemicAnnotationCreate>({
    entity_id: '',
    certainty: 0.5,
    basis: 'empirical',
    source: '',
    note: '',
  });

  const limit = 10;

  const { data, isLoading, error } = useQuery({
    queryKey: ['annotations', page, filterBasis],
    queryFn: () => epistemicApi.list(page * limit, limit, filterBasis || undefined),
  });

  const { data: summary } = useQuery({
    queryKey: ['epistemicSummary'],
    queryFn: epistemicApi.getSummary,
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
    mutationFn: epistemicApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['epistemicSummary'] });
      setShowModal(false);
      setNewAnnotation({
        entity_id: '',
        certainty: 0.5,
        basis: 'empirical',
        source: '',
        note: '',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: epistemicApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['epistemicSummary'] });
    },
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load annotations" />;

  const handleCreate = () => {
    if (newAnnotation.entity_id.trim()) {
      createMutation.mutate(newAnnotation);
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this annotation?')) {
      deleteMutation.mutate(id);
    }
  };

  const getCertaintyColor = (certainty: number) => {
    if (certainty >= 0.8) return 'var(--success-color)';
    if (certainty >= 0.5) return 'var(--warning-color)';
    return 'var(--danger-color)';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Epistemic Annotations</h1>
        <p className="page-subtitle">Manage knowledge certainty and basis annotations</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Annotations</div>
          <div className="stat-value">{summary?.total_count || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Certainty</div>
          <div className="stat-value">{((summary?.avg_certainty || 0) * 100).toFixed(1)}%</div>
        </div>
        {EPISTEMIC_BASES.map((basis) => (
          <div key={basis} className="stat-card">
            <div className="stat-label" style={{ textTransform: 'capitalize' }}>
              {basis}
            </div>
            <div className="stat-value">{summary?.by_basis[basis] || 0}</div>
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
              value={filterBasis}
              onChange={(e) => {
                setFilterBasis(e.target.value);
                setPage(0);
              }}
            >
              <option value="">All Bases</option>
              {EPISTEMIC_BASES.map((basis) => (
                <option key={basis} value={basis}>
                  {basis.charAt(0).toUpperCase() + basis.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Create Annotation
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Entity</th>
                <th>Certainty</th>
                <th>Basis</th>
                <th>Source</th>
                <th>Timestamp</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((annotation: EpistemicAnnotation) => (
                <tr key={annotation.id}>
                  <td>
                    {rootsById.get(annotation.entity_id)?.name ?? (
                      <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                        {annotation.entity_id.slice(0, 8)}...
                      </span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div
                        style={{
                          width: '60px',
                          height: '8px',
                          background: '#e2e8f0',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            width: `${annotation.certainty * 100}%`,
                            height: '100%',
                            background: getCertaintyColor(annotation.certainty),
                          }}
                        />
                      </div>
                      <span>{(annotation.certainty * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${BASIS_COLORS[annotation.basis]}`}>
                      {annotation.basis}
                    </span>
                  </td>
                  <td>{annotation.source || '-'}</td>
                  <td>{new Date(annotation.timestamp).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(annotation.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                    No annotations found
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
              <h3 className="modal-title">Create Epistemic Annotation</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Entity</label>
              <EntitySelect
                value={newAnnotation.entity_id}
                onChange={(entityId) => setNewAnnotation({ ...newAnnotation, entity_id: entityId })}
                placeholder="Select entity…"
              />
            </div>
            <div className="form-group">
              <label className="form-label">
                Certainty ({(newAnnotation.certainty * 100).toFixed(0)}%)
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={newAnnotation.certainty}
                onChange={(e) =>
                  setNewAnnotation({ ...newAnnotation, certainty: parseFloat(e.target.value) })
                }
                style={{ width: '100%' }}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Epistemic Basis</label>
              <select
                className="form-select"
                value={newAnnotation.basis}
                onChange={(e) =>
                  setNewAnnotation({ ...newAnnotation, basis: e.target.value as EpistemicBasis })
                }
              >
                {EPISTEMIC_BASES.map((basis) => (
                  <option key={basis} value={basis}>
                    {basis.charAt(0).toUpperCase() + basis.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Source (DOI, IRI, etc.)</label>
              <input
                type="text"
                className="form-input"
                value={newAnnotation.source || ''}
                onChange={(e) => setNewAnnotation({ ...newAnnotation, source: e.target.value })}
                placeholder="Optional source reference"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Note</label>
              <input
                type="text"
                className="form-input"
                value={newAnnotation.note || ''}
                onChange={(e) => setNewAnnotation({ ...newAnnotation, note: e.target.value })}
                placeholder="Optional note"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleCreate}
                disabled={!newAnnotation.entity_id.trim() || createMutation.isPending}
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

export default EpistemicView;
