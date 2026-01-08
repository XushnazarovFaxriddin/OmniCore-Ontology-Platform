import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { healthApi, adminApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import type { ServiceHealth, HealthStatus } from '../types';

const STATUS_COLORS: Record<HealthStatus, string> = {
  healthy: 'var(--success-color)',
  up: 'var(--success-color)',
  degraded: 'var(--warning-color)',
  unhealthy: 'var(--danger-color)',
  down: 'var(--danger-color)',
};

function SystemHealth() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: healthApi.getOverview,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load system health" />;

  const getStatusBadge = (status: HealthStatus) => {
    const colorClass =
      status === 'healthy' || status === 'up'
        ? 'badge-success'
        : status === 'degraded'
          ? 'badge-warning'
          : 'badge-danger';
    return <span className={`badge ${colorClass}`}>{status.toUpperCase()}</span>;
  };

  const overallStatus = data?.status || 'unknown';

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">System Health</h1>
        <p className="page-subtitle">Monitor the health of all OmniCore services</p>
      </div>

      {/* Overall Status */}
      <div className="card">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div
              style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background:
                  overallStatus === 'healthy'
                    ? 'rgba(34, 197, 94, 0.1)'
                    : overallStatus === 'degraded'
                      ? 'rgba(245, 158, 11, 0.1)'
                      : 'rgba(239, 68, 68, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
              }}
            >
              {overallStatus === 'healthy' ? '✓' : overallStatus === 'degraded' ? '!' : '✗'}
            </div>
            <div>
              <h2 style={{ fontSize: '24px', marginBottom: '4px' }}>Overall System Status</h2>
              <p style={{ color: STATUS_COLORS[overallStatus as HealthStatus], fontWeight: '600' }}>
                {overallStatus.toUpperCase()}
              </p>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => refetch()}>
            Refresh
          </button>
        </div>
        <p style={{ marginTop: '16px', color: 'var(--text-secondary)', fontSize: '14px' }}>
          Last checked: {data?.timestamp ? new Date(data.timestamp).toLocaleString() : 'Unknown'}
        </p>
      </div>

      {/* Services Grid */}
      <h3 style={{ margin: '24px 0 16px', fontSize: '18px' }}>Service Status</h3>
      <div className="health-grid">
        {Object.entries(data?.services || {}).map(([key, service]) => {
          const svc = service as ServiceHealth;
          return (
            <div
              key={key}
              className={`health-card ${svc.status === 'up' ? 'healthy' : svc.status}`}
            >
              <div className="health-service-name">{svc.name}</div>
              <div className="health-status">
                <div className={`health-dot ${svc.status === 'up' ? 'healthy' : svc.status}`} />
                {getStatusBadge(svc.status)}
              </div>
              <div className="health-latency">
                Latency: {svc.latency_ms.toFixed(0)}ms
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                Last check: {new Date(svc.last_check).toLocaleTimeString()}
              </div>
              {svc.error && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '8px 12px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: 'var(--danger-color)',
                  }}
                >
                  {svc.error}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Health Info */}
      <div className="card" style={{ marginTop: '24px' }}>
        <h3 className="card-title" style={{ marginBottom: '16px' }}>
          Health Check Information
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Monitored Services
            </h4>
            <ul style={{ paddingLeft: '20px', color: 'var(--text-primary)' }}>
              <li>Roots Service (Port 18001)</li>
              <li>Causality Service (Port 18002)</li>
              <li>Epistemic Service (Port 18003)</li>
              <li>MMO Service (Port 18004)</li>
              <li>Global Service (Port 18005)</li>
            </ul>
          </div>
          <div>
            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Status Meanings
            </h4>
            <ul style={{ paddingLeft: '20px' }}>
              <li style={{ color: 'var(--success-color)' }}>
                <strong>Healthy/Up:</strong> Service responding normally
              </li>
              <li style={{ color: 'var(--warning-color)' }}>
                <strong>Degraded:</strong> Some services have issues
              </li>
              <li style={{ color: 'var(--danger-color)' }}>
                <strong>Unhealthy/Down:</strong> Service not responding
              </li>
            </ul>
          </div>
          <div>
            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Auto-Refresh
            </h4>
            <p style={{ color: 'var(--text-primary)' }}>
              Health status automatically refreshes every 30 seconds. Click the Refresh button for
              immediate update.
            </p>
          </div>
        </div>
      </div>

      {/* System Management */}
      <div className="card" style={{ marginTop: '24px', borderColor: 'var(--danger-color)' }}>
        <h3 className="card-title" style={{ marginBottom: '16px', color: 'var(--danger-color)' }}>
          System Management (Danger Zone)
        </h3>
        <p style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>
          These actions affect the entire platform state. Proceed with caution.
        </p>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <AdminActionButton
            label="Reset Database"
            action={async () => {
              if (confirm('WARNING: THIS WILL DELETE ALL DATA. Are you sure?')) {
                await adminApi.resetDatabase();
                alert('Database reset successfully. Please restart services if needed.');
                window.location.reload();
              }
            }}
            danger={true}
          />
          <AdminActionButton
            label="Seed Sample Data"
            action={async () => {
              if (confirm('This will insert sample data into the database. Continue?')) {
                const res = await adminApi.seedDatabase();
                alert(`Seeding complete: ${JSON.stringify(res.details)}`);
                window.location.reload();
              }
            }}
            danger={false}
          />
        </div>
      </div>
    </div>
  );
}

function AdminActionButton({ label, action, danger }: { label: string; action: () => Promise<void>; danger: boolean }) {
  const [loading, setLoading] = useState(false);

  return (
    <button
      className={`btn ${danger ? 'btn-danger' : 'btn-secondary'}`}
      disabled={loading}
      onClick={async () => {
        setLoading(true);
        try {
          await action();
        } catch (e) {
          alert('Action failed: ' + String(e));
        } finally {
          setLoading(false);
        }
      }}
    >
      {loading ? 'Processing...' : label}
    </button>
  );
}

export default SystemHealth;
