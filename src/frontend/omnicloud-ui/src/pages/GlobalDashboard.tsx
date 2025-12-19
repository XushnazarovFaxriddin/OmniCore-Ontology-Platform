import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { globalApi, mmoApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import StatCard from '../components/common/StatCard';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#22c55e'];

function GlobalDashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['globalStats'],
    queryFn: globalApi.getStats,
  });

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['mmoMetrics'],
    queryFn: mmoApi.getMetrics,
  });

  if (statsLoading || metricsLoading) return <Loading />;
  if (statsError) return <ErrorMessage message="Failed to load dashboard data" />;

  // Transform data for charts
  const rootsChartData = Object.entries(stats?.roots_by_type || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const causalityChartData = Object.entries(stats?.causality_by_type || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const epistemicChartData = Object.entries(stats?.epistemic_by_basis || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const getMetricClass = (value: number, target: number) => {
    if (value >= target) return 'good';
    if (value >= target * 0.7) return 'medium';
    return 'poor';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Global Dashboard</h1>
        <p className="page-subtitle">Comprehensive overview of the ontology platform</p>
      </div>

      <div className="stats-grid">
        <StatCard label="Total Roots" value={stats?.total_roots || 0} />
        <StatCard label="Causality Links" value={stats?.total_causality_links || 0} />
        <StatCard label="Epistemic Annotations" value={stats?.total_epistemic_annotations || 0} />
        <StatCard label="MMO Classes" value={stats?.total_mmo_classes || 0} />
        <StatCard
          label="Avg Causality Confidence"
          value={`${((stats?.avg_causality_confidence || 0) * 100).toFixed(1)}%`}
        />
        <StatCard
          label="Avg Epistemic Certainty"
          value={`${((stats?.avg_epistemic_certainty || 0) * 100).toFixed(1)}%`}
        />
      </div>

      {/* MMO Metrics */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">MMO Quality Metrics</h2>
        </div>
        <div className="metrics-grid">
          <div className="metric-gauge">
            <div className={`metric-value ${getMetricClass(metrics?.completeness || 0, 0.85)}`}>
              {((metrics?.completeness || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">Completeness</div>
            <div className="metric-target">Target: 85%</div>
          </div>
          <div className="metric-gauge">
            <div className={`metric-value ${getMetricClass(metrics?.coverage || 0, 0.70)}`}>
              {((metrics?.coverage || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">Coverage</div>
            <div className="metric-target">Target: 70%</div>
          </div>
          <div className="metric-gauge">
            <div className={`metric-value ${getMetricClass(metrics?.coherence || 0, 0.95)}`}>
              {((metrics?.coherence || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">Coherence</div>
            <div className="metric-target">Target: 95%</div>
          </div>
          <div className="metric-gauge">
            <div className={`metric-value ${getMetricClass(metrics?.utility || 0, 0.80)}`}>
              {((metrics?.utility || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">Utility</div>
            <div className="metric-target">Target: 80%</div>
          </div>
          <div className="metric-gauge">
            <div className={`metric-value ${getMetricClass(metrics?.inclusivity || 0, 0.65)}`}>
              {((metrics?.inclusivity || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">Inclusivity</div>
            <div className="metric-target">Target: 65%</div>
          </div>
          <div className="metric-gauge">
            <div className="metric-value" style={{ color: 'var(--primary-color)' }}>
              {((metrics?.mmo_score || 0) * 100).toFixed(0)}%
            </div>
            <div className="metric-label">MMO Score</div>
            <div className="metric-target">Weighted Average</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Roots by Type</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={rootsChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {rootsChartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Causality by Type</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={causalityChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Epistemic by Basis</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={epistemicChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {epistemicChartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default GlobalDashboard;
