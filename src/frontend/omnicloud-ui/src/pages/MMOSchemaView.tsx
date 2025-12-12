import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mmoApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import type { MMOClass, MMOClassCreate, MMOSlot, MMOSlotCreate } from '../types';

function MMOSchemaView() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'classes' | 'slots' | 'metrics'>('classes');
  const [showClassModal, setShowClassModal] = useState(false);
  const [showSlotModal, setShowSlotModal] = useState(false);

  const [newClass, setNewClass] = useState<MMOClassCreate>({
    name: '',
    description: '',
    properties: [],
  });

  const [newSlot, setNewSlot] = useState<MMOSlotCreate>({
    name: '',
    domain_class_id: '',
    range_type: 'string',
    cardinality: '0..*',
    description: '',
  });

  const { data: schema, isLoading, error } = useQuery({
    queryKey: ['mmoSchema'],
    queryFn: mmoApi.getSchema,
  });

  const createClassMutation = useMutation({
    mutationFn: mmoApi.createClass,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mmoSchema'] });
      setShowClassModal(false);
      setNewClass({ name: '', description: '', properties: [] });
    },
  });

  const deleteClassMutation = useMutation({
    mutationFn: mmoApi.deleteClass,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mmoSchema'] });
    },
  });

  const createSlotMutation = useMutation({
    mutationFn: mmoApi.createSlot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mmoSchema'] });
      setShowSlotModal(false);
      setNewSlot({
        name: '',
        domain_class_id: '',
        range_type: 'string',
        cardinality: '0..*',
        description: '',
      });
    },
  });

  const deleteSlotMutation = useMutation({
    mutationFn: mmoApi.deleteSlot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mmoSchema'] });
    },
  });

  const recalculateMutation = useMutation({
    mutationFn: mmoApi.recalculateMetrics,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mmoSchema'] });
    },
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load MMO schema" />;

  const getMetricClass = (value: number, target: number) => {
    if (value >= target) return 'good';
    if (value >= target * 0.7) return 'medium';
    return 'poor';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">MMO Schema</h1>
        <p className="page-subtitle">Meta-Meta-Ontology structure and metrics</p>
      </div>

      {/* Tabs */}
      <div className="card" style={{ padding: '0' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)' }}>
          {['classes', 'slots', 'metrics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as 'classes' | 'slots' | 'metrics')}
              style={{
                padding: '16px 24px',
                border: 'none',
                background: activeTab === tab ? 'white' : 'transparent',
                borderBottom: activeTab === tab ? '2px solid var(--primary-color)' : 'none',
                cursor: 'pointer',
                fontWeight: activeTab === tab ? '600' : '400',
                color: activeTab === tab ? 'var(--primary-color)' : 'var(--text-secondary)',
                textTransform: 'capitalize',
              }}
            >
              {tab} ({tab === 'classes' ? schema?.classes.length : tab === 'slots' ? schema?.slots.length : '5'})
            </button>
          ))}
        </div>
      </div>

      {/* Classes Tab */}
      {activeTab === 'classes' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">MMO Classes</h2>
            <button className="btn btn-primary" onClick={() => setShowClassModal(true)}>
              + Add Class
            </button>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Parent</th>
                  <th>Properties</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {schema?.classes.map((cls: MMOClass) => (
                  <tr key={cls.id}>
                    <td style={{ fontWeight: '500' }}>{cls.name}</td>
                    <td>{cls.description || '-'}</td>
                    <td>
                      {cls.parent_class_id
                        ? schema?.classes.find((c) => c.id === cls.parent_class_id)?.name || '-'
                        : '-'}
                    </td>
                    <td>{cls.properties.length > 0 ? cls.properties.join(', ') : '-'}</td>
                    <td>{new Date(cls.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => {
                          if (confirm('Delete this class?')) deleteClassMutation.mutate(cls.id);
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {schema?.classes.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                      No classes defined
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Slots Tab */}
      {activeTab === 'slots' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">MMO Slots (Properties)</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowSlotModal(true)}
              disabled={schema?.classes.length === 0}
            >
              + Add Slot
            </button>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Domain Class</th>
                  <th>Range Type</th>
                  <th>Cardinality</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {schema?.slots.map((slot: MMOSlot) => (
                  <tr key={slot.id}>
                    <td style={{ fontWeight: '500' }}>{slot.name}</td>
                    <td>{schema?.classes.find((c) => c.id === slot.domain_class_id)?.name || '-'}</td>
                    <td>
                      <span className="badge badge-info">{slot.range_type}</span>
                    </td>
                    <td>{slot.cardinality}</td>
                    <td>{slot.description || '-'}</td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => {
                          if (confirm('Delete this slot?')) deleteSlotMutation.mutate(slot.id);
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {schema?.slots.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                      No slots defined
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">MMO Quality Metrics</h2>
            <button
              className="btn btn-primary"
              onClick={() => recalculateMutation.mutate()}
              disabled={recalculateMutation.isPending}
            >
              {recalculateMutation.isPending ? 'Recalculating...' : 'Recalculate'}
            </button>
          </div>
          <div className="metrics-grid">
            <div className="metric-gauge">
              <div className={`metric-value ${getMetricClass(schema?.metrics.completeness || 0, 0.85)}`}>
                {((schema?.metrics.completeness || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Completeness</div>
              <div className="metric-target">Target: 85%</div>
            </div>
            <div className="metric-gauge">
              <div className={`metric-value ${getMetricClass(schema?.metrics.coverage || 0, 0.70)}`}>
                {((schema?.metrics.coverage || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Coverage</div>
              <div className="metric-target">Target: 70%</div>
            </div>
            <div className="metric-gauge">
              <div className={`metric-value ${getMetricClass(schema?.metrics.coherence || 0, 0.95)}`}>
                {((schema?.metrics.coherence || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Coherence</div>
              <div className="metric-target">Target: 95%</div>
            </div>
            <div className="metric-gauge">
              <div className={`metric-value ${getMetricClass(schema?.metrics.utility || 0, 0.80)}`}>
                {((schema?.metrics.utility || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Utility</div>
              <div className="metric-target">Target: 80%</div>
            </div>
            <div className="metric-gauge">
              <div className={`metric-value ${getMetricClass(schema?.metrics.inclusivity || 0, 0.65)}`}>
                {((schema?.metrics.inclusivity || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">Inclusivity</div>
              <div className="metric-target">Target: 65%</div>
            </div>
            <div className="metric-gauge">
              <div className="metric-value" style={{ color: 'var(--primary-color)' }}>
                {((schema?.metrics.mmo_score || 0) * 100).toFixed(0)}%
              </div>
              <div className="metric-label">MMO Score</div>
              <div className="metric-target">Weighted Average</div>
            </div>
          </div>
          <p style={{ marginTop: '20px', color: 'var(--text-secondary)', fontSize: '14px' }}>
            Last updated: {schema?.metrics.last_updated ? new Date(schema.metrics.last_updated).toLocaleString() : 'Never'}
          </p>
        </div>
      )}

      {/* Class Modal */}
      {showClassModal && (
        <div className="modal-overlay" onClick={() => setShowClassModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create MMO Class</h3>
              <button className="modal-close" onClick={() => setShowClassModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Name</label>
              <input
                type="text"
                className="form-input"
                value={newClass.name}
                onChange={(e) => setNewClass({ ...newClass, name: e.target.value })}
                placeholder="Class name"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <input
                type="text"
                className="form-input"
                value={newClass.description || ''}
                onChange={(e) => setNewClass({ ...newClass, description: e.target.value })}
                placeholder="Optional description"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Parent Class</label>
              <select
                className="form-select"
                value={newClass.parent_class_id || ''}
                onChange={(e) => setNewClass({ ...newClass, parent_class_id: e.target.value || undefined })}
              >
                <option value="">None (root class)</option>
                {schema?.classes.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowClassModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={() => newClass.name && createClassMutation.mutate(newClass)}
                disabled={!newClass.name || createClassMutation.isPending}
              >
                {createClassMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Slot Modal */}
      {showSlotModal && (
        <div className="modal-overlay" onClick={() => setShowSlotModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create MMO Slot</h3>
              <button className="modal-close" onClick={() => setShowSlotModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Name</label>
              <input
                type="text"
                className="form-input"
                value={newSlot.name}
                onChange={(e) => setNewSlot({ ...newSlot, name: e.target.value })}
                placeholder="Slot name"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Domain Class</label>
              <select
                className="form-select"
                value={newSlot.domain_class_id}
                onChange={(e) => setNewSlot({ ...newSlot, domain_class_id: e.target.value })}
              >
                <option value="">Select a class</option>
                {schema?.classes.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Range Type</label>
              <select
                className="form-select"
                value={newSlot.range_type}
                onChange={(e) => setNewSlot({ ...newSlot, range_type: e.target.value })}
              >
                <option value="string">String</option>
                <option value="int">Integer</option>
                <option value="float">Float</option>
                <option value="boolean">Boolean</option>
                {schema?.classes.map((cls) => (
                  <option key={cls.id} value={`reference:${cls.id}`}>
                    Reference: {cls.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Cardinality</label>
              <select
                className="form-select"
                value={newSlot.cardinality}
                onChange={(e) => setNewSlot({ ...newSlot, cardinality: e.target.value })}
              >
                <option value="1">1 (exactly one)</option>
                <option value="0..1">0..1 (optional)</option>
                <option value="1..*">1..* (one or more)</option>
                <option value="0..*">0..* (any number)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <input
                type="text"
                className="form-input"
                value={newSlot.description || ''}
                onChange={(e) => setNewSlot({ ...newSlot, description: e.target.value })}
                placeholder="Optional description"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowSlotModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={() =>
                  newSlot.name && newSlot.domain_class_id && createSlotMutation.mutate(newSlot)
                }
                disabled={!newSlot.name || !newSlot.domain_class_id || createSlotMutation.isPending}
              >
                {createSlotMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MMOSchemaView;
