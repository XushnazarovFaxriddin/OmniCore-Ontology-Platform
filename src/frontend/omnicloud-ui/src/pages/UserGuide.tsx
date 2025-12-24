import { Link } from 'react-router-dom';

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'quickstart', label: 'Quick Start' },
  { id: 'workflow', label: 'Workflow' },
  { id: 'features', label: 'Features' },
  { id: 'ai', label: 'AI / SLM' },
  { id: 'security', label: 'Security & Auth' },
  { id: 'troubleshooting', label: 'Troubleshooting' },
  { id: 'credits', label: 'Team & Credits' },
];

function UserGuide() {
  const gatewayPort = import.meta.env.VITE_GATEWAY_PORT || '18000';
  const gatewayPublicUrl = import.meta.env.VITE_GATEWAY_PUBLIC_URL;
  const gatewayBaseUrl =
    gatewayPublicUrl ||
    (typeof window !== 'undefined'
      ? `${window.location.protocol}//${window.location.hostname}:${gatewayPort}`
      : `http://localhost:${gatewayPort}`);

  const gatewayDocsUrl = `${gatewayBaseUrl}/docs`;
  const gatewayHealthUrl = `${gatewayBaseUrl}/health`;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">User Guide</h1>
        <p className="page-subtitle">
          A practical guide to using the OmniCore dashboard: pages, workflows, AI capabilities,
          and best practices.
        </p>
      </div>

      <div className="card guide-hero">
        <div className="guide-hero-inner">
          <div>
            <div className="guide-kicker">OmniCore Ontology Platform</div>
            <h2 className="guide-hero-title">A modern dashboard for ontology operations</h2>
            <p className="guide-hero-text">
              This UI provides a single control plane for the platform services (Roots, Causality,
              Epistemic, MMO, Global, SLM), including monitoring, CRUD operations, and AI-assisted
              tools. The goal is to keep ontology work structured, consistent, and auditable.
            </p>

            <div className="guide-actions">
              <Link className="btn btn-primary" to="/dashboard" style={{ textDecoration: 'none' }}>
                Dashboard
              </Link>
              <Link className="btn btn-secondary" to="/roots" style={{ textDecoration: 'none' }}>
                Roots
              </Link>
              <Link className="btn btn-secondary" to="/ai/chat" style={{ textDecoration: 'none' }}>
                AI Chat
              </Link>
            </div>
          </div>

          <div className="guide-hero-panel">
            <div className="guide-badges">
              <span className="badge badge-primary">Microservices</span>
              <span className="badge badge-success">Observable</span>
              <span className="badge badge-info">Explainable</span>
              <span className="badge badge-warning">AI-assisted</span>
            </div>

            <div className="guide-mini">
              <div className="guide-mini-title">Fast path</div>
              <ol className="guide-steps">
                <li>Create (or import) entities in Roots</li>
                <li>Connect them with Causality links</li>
                <li>Add Epistemic annotations (certainty + basis)</li>
                <li>Verify via Dashboard / System Health</li>
              </ol>
            </div>

            <div className="guide-mini">
              <div className="guide-mini-title">Endpoints</div>
              <div className="guide-mini-kv">
                <div className="guide-mini-k">API docs</div>
                <a className="guide-link" href={gatewayDocsUrl} target="_blank" rel="noreferrer">
                  {gatewayDocsUrl}
                </a>
              </div>
              <div className="guide-mini-kv">
                <div className="guide-mini-k">Gateway health</div>
                <a className="guide-link" href={gatewayHealthUrl} target="_blank" rel="noreferrer">
                  {gatewayHealthUrl}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="guide-layout">
        <aside className="card guide-toc">
          <div className="card-header">
            <h2 className="card-title">Contents</h2>
          </div>
          <ul className="guide-toc-list">
            {sections.map((s) => (
              <li key={s.id}>
                <a className="guide-toc-link" href={`#${s.id}`}>
                  {s.label}
                </a>
              </li>
            ))}
          </ul>
          <div className="guide-toc-footer">
            <div style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.6 }}>
              Tip: If you changed gateway port, set <code>VITE_GATEWAY_PORT</code> or{' '}
              <code>VITE_GATEWAY_PUBLIC_URL</code> for accurate links.
            </div>
          </div>
        </aside>

        <div className="guide-content">
          <section id="overview" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Overview</h2>
            </div>
            <p className="guide-paragraph">
              OmniCore is a meta-ontological platform for structuring, connecting, and evaluating
              knowledge representations. The dashboard is the operational interface: you can create
              entities, connect them, annotate evidence, observe system health, and use AI tools
              when available.
            </p>
            <p className="guide-paragraph">
              The platform is intentionally modular. Each service focuses on a single responsibility
              and the API Gateway provides a unified entry point for the dashboard and external
              clients.
            </p>

            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">Roots</div>
                <div className="guide-card-text">
                  Classify entities into fundamental root types: EXTANT, ABSTRACT, MENTAL, FICTIVE.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Causality</div>
                <div className="guide-card-text">
                  Create and manage causal relationships between entities (multiple causality types).
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Epistemic</div>
                <div className="guide-card-text">
                  Add evidence-weighted annotations: certainty + basis (axiomatic, empirical,
                  consensus, speculative).
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">MMO / Global / Health</div>
                <div className="guide-card-text">
                  Quality metrics, global statistics, and system observability.
                </div>
              </div>
            </div>
          </section>

          <section id="quickstart" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Quick Start</h2>
            </div>

            <ol className="guide-steps guide-steps-large">
              <li>
                Open <strong>Dashboard</strong> for overall stats:{' '}
                <Link className="guide-link" to="/dashboard">
                  /dashboard
                </Link>
              </li>
              <li>
                Create or find entities in <strong>Roots</strong>:{' '}
                <Link className="guide-link" to="/roots">
                  /roots
                </Link>
              </li>
              <li>
                Create relationships in <strong>Causality</strong>:{' '}
                <Link className="guide-link" to="/causality">
                  /causality
                </Link>
                <div className="guide-muted">No manual IDs: use the searchable selector.</div>
              </li>
              <li>
                Add certainty and basis in <strong>Epistemic</strong>:{' '}
                <Link className="guide-link" to="/epistemic">
                  /epistemic
                </Link>
              </li>
              <li>
                Check service status in <strong>System Health</strong>:{' '}
                <Link className="guide-link" to="/health">
                  /health
                </Link>
              </li>
            </ol>
          </section>

          <section id="workflow" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Workflow</h2>
            </div>

            <p className="guide-paragraph">
              A pragmatic workflow that works well in practice:
            </p>

            <div className="guide-timeline">
              <div className="guide-timeline-item">
                <div className="guide-dot" />
                <div>
                  <div className="guide-timeline-title">1) Establish ontology foundations</div>
                  <div className="guide-timeline-text">
                    Use Roots to classify entities correctly. Downstream operations become consistent
                    when roots are clean.
                  </div>
                </div>
              </div>
              <div className="guide-timeline-item">
                <div className="guide-dot" />
                <div>
                  <div className="guide-timeline-title">2) Add relationships</div>
                  <div className="guide-timeline-text">
                    Create causal links (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT) to connect
                    entities into a coherent graph.
                  </div>
                </div>
              </div>
              <div className="guide-timeline-item">
                <div className="guide-dot" />
                <div>
                  <div className="guide-timeline-title">3) Add an evidence layer</div>
                  <div className="guide-timeline-text">
                    Epistemic annotations capture how confident we are, together with the basis for
                    that confidence.
                  </div>
                </div>
              </div>
              <div className="guide-timeline-item">
                <div className="guide-dot" />
                <div>
                  <div className="guide-timeline-title">4) Monitor and iterate</div>
                  <div className="guide-timeline-text">
                    Use Dashboard / Global / Health to detect issues early, then refine data and
                    relationships iteratively.
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="features" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Features</h2>
            </div>

            <p className="guide-paragraph">
              The dashboard focuses on operational clarity: fewer manual steps, fewer copy/paste IDs,
              and more visibility into what the system is doing.
            </p>

            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">Searchable entity selector</div>
                <div className="guide-card-text">
                  Pick entities from a searchable list in Causality/Epistemic. This reduces errors
                  and improves speed.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Unified API Gateway</div>
                <div className="guide-card-text">
                  A single entry point for all services. This is where authentication, routing, and
                  docs live.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Observability</div>
                <div className="guide-card-text">
                  System Health provides a fast snapshot of service availability and helps diagnose
                  "why a feature is not working".
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Audit-friendly structure</div>
                <div className="guide-card-text">
                  Roots + Causality + Epistemic create a consistent and auditable knowledge layer.
                </div>
              </div>
            </div>
          </section>

          <section id="ai" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">AI / SLM</h2>
            </div>

            <p className="guide-paragraph">
              The AI area (AI Chat, AI Assistant, AI Search, AI Models) is designed to accelerate
              ontology work. If Ollama is available, the SLM service can run local inference for
              tasks like classification, relationship extraction, and draft suggestions.
            </p>

            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">AI Chat</div>
                <div className="guide-card-text">Ask questions and get fast explanations.</div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">AI Assistant</div>
                <div className="guide-card-text">
                  Guided workflows: root inference, causality extraction, epistemic annotation, and
                  more.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">AI Models</div>
                <div className="guide-card-text">See model status and run setup when needed.</div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Limitations</div>
                <div className="guide-card-text">
                  Always review AI outputs. The platform helps with traces and auditability, but
                  results are not guaranteed.
                </div>
              </div>
            </div>
          </section>

          <section id="security" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Security & Auth</h2>
            </div>

            <p className="guide-paragraph">
              In production mode, the API Gateway requires authentication (JWT or API key). The
              dashboard automatically obtains a JWT and includes it in requests. External clients can
              use the same token endpoint or API keys depending on your configuration.
            </p>

            <details className="guide-details">
              <summary className="guide-summary">How do I get a JWT token?</summary>
              <div className="guide-details-body">
                <p className="guide-paragraph">
                  Token endpoint: <code>/api/auth/token</code>. The UI does this automatically.
                  Manual test:
                </p>
                <pre className="guide-code">
                  <code>{`curl -X POST http://localhost:${gatewayPort}/api/auth/token \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"username\":\"admin\",\"scopes\":[\"read\",\"write\"]}'`}</code>
                </pre>
              </div>
            </details>

            <details className="guide-details">
              <summary className="guide-summary">Production recommendations</summary>
              <div className="guide-details-body">
                <ul className="guide-list">
                  <li>
                    Change <strong>JWT_SECRET_KEY</strong> before going public.
                  </li>
                  <li>
                    Configure <strong>VALID_API_KEYS</strong> for integrations and automation.
                  </li>
                  <li>Even with VPN/LAN, expose only the ports you need.</li>
                </ul>
              </div>
            </details>
          </section>

          <section id="troubleshooting" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Troubleshooting</h2>
            </div>

            <details className="guide-details" open>
              <summary className="guide-summary">401 Unauthorized</summary>
              <div className="guide-details-body">
                <p className="guide-paragraph">
                  Usually caused by a missing/expired token. Try a hard refresh (Ctrl+F5) or reopen
                  the dashboard.
                </p>
              </div>
            </details>

            <details className="guide-details">
              <summary className="guide-summary">"Service is unavailable"</summary>
              <div className="guide-details-body">
                <ul className="guide-list">
                  <li>
                    Open <Link className="guide-link" to="/health">System Health</Link> and confirm
                    services are healthy.
                  </li>
                  <li>
                    Check gateway health: <a className="guide-link" href={gatewayHealthUrl} target="_blank" rel="noreferrer">{gatewayHealthUrl}</a>
                  </li>
                  <li>
                    If a specific service is down, check container logs on the server.
                  </li>
                </ul>
              </div>
            </details>

            <details className="guide-details">
              <summary className="guide-summary">Dashboard does not open</summary>
              <div className="guide-details-body">
                <ul className="guide-list">
                  <li>
                    With Podman, the host port is usually <code>13000</code> (container port is{' '}
                    <code>3000</code>).
                  </li>
                  <li>
                    Check UI logs on the server: <code>podman logs --tail 200 omnicore-ui</code>
                  </li>
                  <li>
                    Verify gateway: <code>curl -f http://127.0.0.1:18000/health</code>
                  </li>
                </ul>
              </div>
            </details>
          </section>

          <section id="credits" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Team & Credits</h2>
            </div>

            <p className="guide-paragraph">
              This project is developed by <strong>Team BSU Masters 2025</strong>.
            </p>
            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">Supervisor</div>
                <div className="guide-card-text">
                  <strong>Teacher KREMENCHUTSKIY ANATOLIY</strong>
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Developer</div>
                <div className="guide-card-text">
                  <strong>Fakhriddin Khushnazarov</strong>
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Team</div>
                <div className="guide-card-text">
                  BSU Masters 2025
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Support</div>
                <div className="guide-card-text">
                  For faster fixes: include the endpoint, status code, and logs when reporting issues.
                </div>
              </div>
            </div>

            <p className="guide-paragraph guide-muted" style={{ marginTop: 16 }}>
              Built for operational clarity: strong defaults, clear flows, and pragmatic tooling for real deployments.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

export default UserGuide;

