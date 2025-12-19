import { useQuery } from '@tanstack/react-query';
import { globalApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import StatCard from '../components/common/StatCard';
import { Link } from 'react-router-dom';

function Home() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['globalStats'],
    queryFn: globalApi.getStats,
  });

  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load statistics" />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Welcome to OmniCore</h1>
        <p className="page-subtitle">
          Self-evolving meta-ontological platform for unified knowledge representation
        </p>
      </div>

      <div className="stats-grid">
        <StatCard label="Total Roots" value={stats?.total_roots || 0} />
        <StatCard label="Causality Links" value={stats?.total_causality_links || 0} />
        <StatCard label="Epistemic Annotations" value={stats?.total_epistemic_annotations || 0} />
        <StatCard label="MMO Classes" value={stats?.total_mmo_classes || 0} />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Quick Navigation</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <Link to="/dashboard" className="btn btn-primary" style={{ textDecoration: 'none' }}>
            View Dashboard
          </Link>
          <Link to="/roots" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
            Manage Roots
          </Link>
          <Link to="/causality" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
            View Causality
          </Link>
          <Link to="/mmo" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
            MMO Schema
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">About OmniCore</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.8' }}>
          OmniCore is a meta-ontological platform designed to unify heterogeneous ontologies
          into a coherent Meta-Ontology (MO). The system evaluates MO quality via a self-improving
          Meta-Meta-Ontology (MMO) and supports explainable, auditable AI reasoning grounded in
          formal roots and causality.
        </p>
        <div style={{ marginTop: '20px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Core Components:</h3>
          <ul style={{ paddingLeft: '20px', color: 'var(--text-secondary)' }}>
            <li><strong>Roots:</strong> Four fundamental ontological types (EXTANT, ABSTRACT, MENTAL, FICTIVE)</li>
            <li><strong>Causality:</strong> Five causality types (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT)</li>
            <li><strong>Epistemic:</strong> Knowledge annotations with certainty and basis</li>
            <li><strong>MMO:</strong> Meta-Meta-Ontology for quality evaluation</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Home;
