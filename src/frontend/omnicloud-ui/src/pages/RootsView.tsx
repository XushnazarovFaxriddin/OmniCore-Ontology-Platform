import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rootsApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import type { Root, RootCreate, RootType } from '../types';

const ROOT_TYPES: RootType[] = ['EXTANT', 'ABSTRACT', 'MENTAL', 'FICTIVE'];

const ROOT_TYPE_COLORS: Record<RootType, string> = {
  EXTANT: 'badge-primary',
  ABSTRACT: 'badge-info',
  MENTAL: 'badge-warning',
  FICTIVE: 'badge-success',
};

function RootsView() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [filterType, setFilterType] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [newRoot, setNewRoot] = useState<RootCreate>({
    name: '',
    root_type: 'EXTANT',
    description: '',
  });

  const limit = 10;

  const { data, isLoading, error } = useQuery({
    queryKey: ['roots', page, filterType],
    queryFn: () => rootsApi.list(page * limit, limit, filterType || undefined),
  });

  const { data: summary } = useQuery({
    queryKey: ['rootsSummary'],
    queryFn: rootsApi.getSummary,
  });

  const createMutation = useMutation({
    mutationFn: rootsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roots'] });
      queryClient.invalidateQueries({ queryKey: ['rootsSummary'] });
      setShowModal(false);
      setNewRoot({ name: '', root_type: 'EXTANT', description: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: rootsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roots'] });
      queryClient.invalidateQueries({ queryKey: ['rootsSummary'] });
    },
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load roots" />;

  const handleCreate = () => {
    if (newRoot.name.trim()) {
      createMutation.mutate(newRoot);
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this root?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Roots</h1>
        <p className="page-subtitle">Manage fundamental ontological root types</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Roots</div>
          <div className="stat-value">{summary?.total_count || 0}</div>
        </div>
        {ROOT_TYPES.map((type) => (
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
              {ROOT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Create Root
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((root: Root) => (
                <tr key={root.id}>
                  <td>{root.name}</td>
                  <td>
                    <span className={`badge ${ROOT_TYPE_COLORS[root.root_type]}`}>
                      {root.root_type}
                    </span>
                  </td>
                  <td>{root.description || '-'}</td>
                  <td>{new Date(root.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(root.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '40px' }}>
                    No roots found
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
              <h3 className="modal-title">Create Root</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Name</label>
              <input
                type="text"
                className="form-input"
                value={newRoot.name}
                onChange={(e) => setNewRoot({ ...newRoot, name: e.target.value })}
                placeholder="Enter root name"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select
                className="form-select"
                value={newRoot.root_type}
                onChange={(e) => setNewRoot({ ...newRoot, root_type: e.target.value as RootType })}
              >
                {ROOT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <input
                type="text"
                className="form-input"
                value={newRoot.description || ''}
                onChange={(e) => setNewRoot({ ...newRoot, description: e.target.value })}
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
                disabled={!newRoot.name.trim() || createMutation.isPending}
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

export default RootsView;
