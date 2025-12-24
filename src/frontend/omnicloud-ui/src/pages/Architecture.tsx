import { Link } from 'react-router-dom';

const sections = [
  { id: 'overview', label: 'System Overview' },
  { id: 'services', label: 'Services & Responsibilities' },
  { id: 'api', label: 'API Gateway & Routing' },
  { id: 'auth', label: 'Auth & Security Flow' },
  { id: 'ai', label: 'AI / SLM Pipeline' },
  { id: 'deployment', label: 'Deployment Topology (Podman)' },
  { id: 'data', label: 'Data & Persistence' },
  { id: 'observability', label: 'Health, Logs & Operations' },
  { id: 'credits', label: 'Team & Credits' },
];

function SystemOverviewDiagram() {
  return (
    <div className="arch-diagram">
      <svg
        className="arch-svg"
        viewBox="0 0 1040 440"
        role="img"
        aria-label="OmniCore system overview diagram"
      >
        <defs>
          <linearGradient id="archGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(99,102,241,0.18)" />
            <stop offset="100%" stopColor="rgba(34,197,94,0.10)" />
          </linearGradient>
          <linearGradient id="archCard" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#f8fafc" />
          </linearGradient>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="416" rx="18" fill="url(#archGrad)" />

        {/* Browser */}
        <g filter="url(#shadow)">
          <rect x="50" y="64" width="170" height="80" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="135" y="98" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0f172a">Browser</text>
          <text x="135" y="120" textAnchor="middle" fontSize="12" fill="#64748b">User / VPN Client</text>
        </g>

        {/* Dashboard */}
        <g filter="url(#shadow)">
          <rect x="260" y="64" width="220" height="80" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="370" y="98" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0f172a">Dashboard UI</text>
          <text x="370" y="120" textAnchor="middle" fontSize="12" fill="#64748b">React + Vite</text>
        </g>

        {/* Gateway */}
        <g filter="url(#shadow)">
          <rect x="520" y="56" width="240" height="96" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="640" y="92" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0f172a">API Gateway</text>
          <text x="640" y="114" textAnchor="middle" fontSize="12" fill="#64748b">Auth · Routing · Rate Limit</text>
          <text x="640" y="134" textAnchor="middle" fontSize="12" fill="#64748b">/docs · /api/*</text>
        </g>

        {/* Services row */}
        {[
          { x: 90, label: 'Roots', port: '18001' },
          { x: 250, label: 'Causality', port: '18002' },
          { x: 410, label: 'Epistemic', port: '18003' },
          { x: 570, label: 'MMO', port: '18004' },
          { x: 730, label: 'Global', port: '18005' },
          { x: 890, label: 'SLM', port: '18006' },
        ].map((s) => (
          <g key={s.label} filter="url(#shadow)">
            <rect x={s.x} y="250" width="130" height="78" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
            <text x={s.x + 65} y="282" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">
              {s.label}
            </text>
            <text x={s.x + 65} y="304" textAnchor="middle" fontSize="12" fill="#64748b">
              :{s.port}
            </text>
          </g>
        ))}

        {/* Redis */}
        <g filter="url(#shadow)">
          <rect x="820" y="180" width="180" height="56" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="910" y="212" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">Redis</text>
          <text x="910" y="232" textAnchor="middle" fontSize="12" fill="#64748b">rate limiting / cache</text>
        </g>

        {/* Ollama */}
        <g filter="url(#shadow)">
          <rect x="820" y="338" width="180" height="56" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="910" y="370" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">Ollama</text>
          <text x="910" y="390" textAnchor="middle" fontSize="12" fill="#64748b">local model runtime</text>
        </g>

        {/* Data */}
        <g filter="url(#shadow)">
          <rect x="50" y="346" width="420" height="56" rx="14" fill="url(#archCard)" stroke="#e2e8f0" />
          <text x="260" y="378" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">Persistent Storage</text>
          <text x="260" y="398" textAnchor="middle" fontSize="12" fill="#64748b">SQLite + files (data/logs/ontologies/snapshots)</text>
        </g>

        {/* Arrows */}
        <path d="M 220 104 L 260 104" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 480 104 L 520 104" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 152 L 640 230" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 155 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 315 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 475 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 635 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 795 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 640 230 L 955 250" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />

        {/* Gateway -> Redis */}
        <path d="M 760 104 L 820 208" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />

        {/* Services -> Storage */}
        <path d="M 155 328 L 200 346" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 315 328 L 300 346" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
        <path d="M 475 328 L 400 346" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />

        {/* SLM -> Ollama */}
        <path d="M 955 328 L 910 338" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />

        {/* Labels */}
        <text x="250" y="92" fontSize="11" fill="#64748b">HTTP(S)</text>
        <text x="490" y="92" fontSize="11" fill="#64748b">/api (proxy)</text>
        <text x="670" y="206" fontSize="11" fill="#64748b">routes</text>
      </svg>
    </div>
  );
}

function AuthFlowDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 240" role="img" aria-label="JWT authentication flow diagram">
        <defs>
          <filter id="shadow2" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrow2" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="216" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        {[
          { x: 60, label: 'Dashboard UI', sub: 'browser session' },
          { x: 330, label: 'POST /api/auth/token', sub: 'Gateway endpoint' },
          { x: 600, label: 'JWT Token', sub: 'signed, expiring' },
          { x: 830, label: 'Authorized Calls', sub: 'Bearer <token>' },
        ].map((n) => (
          <g key={n.label} filter="url(#shadow2)">
            <rect x={n.x} y="70" width="190" height="90" rx="14" fill="#f8fafc" stroke="#e2e8f0" />
            <text x={n.x + 95} y="108" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">
              {n.label}
            </text>
            <text x={n.x + 95} y="132" textAnchor="middle" fontSize="12" fill="#64748b">
              {n.sub}
            </text>
          </g>
        ))}

        <path d="M 250 115 L 330 115" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow2)" />
        <path d="M 520 115 L 600 115" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow2)" />
        <path d="M 790 115 L 830 115" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow2)" />

        <text x="290" y="102" fontSize="11" fill="#64748b">auto-login</text>
        <text x="555" y="102" fontSize="11" fill="#64748b">returns</text>
        <text x="810" y="102" fontSize="11" fill="#64748b">adds header</text>

        <text x="520" y="200" textAnchor="middle" fontSize="12" fill="#64748b">
          Dashboard stores the token in localStorage and refreshes it if a request returns 401.
        </text>
      </svg>
    </div>
  );
}

function DeploymentDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 360" role="img" aria-label="Podman deployment topology diagram">
        <defs>
          <filter id="shadow3" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrow3" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="336" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        {/* Host */}
        <g filter="url(#shadow3)">
          <rect x="60" y="60" width="320" height="240" rx="16" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="220" y="92" textAnchor="middle" fontSize="14" fontWeight="800" fill="#0f172a">
            Host (AlmaLinux / Podman rootless)
          </text>

          <text x="90" y="130" fontSize="12" fill="#64748b">VPN/LAN clients</text>
          <text x="90" y="154" fontSize="12" fill="#64748b">→ 192.168.1.3:18000 (Gateway)</text>
          <text x="90" y="176" fontSize="12" fill="#64748b">→ 192.168.1.3:13000 (Dashboard)</text>
          <text x="90" y="206" fontSize="12" fill="#64748b">Optional: 18001..18006 for service debug</text>
        </g>

        {/* Containers */}
        <g filter="url(#shadow3)">
          <rect x="430" y="60" width="550" height="240" rx="16" fill="#ffffff" stroke="#e2e8f0" />
          <text x="705" y="92" textAnchor="middle" fontSize="14" fontWeight="800" fill="#0f172a">
            Container Network (omnicore-network)
          </text>

          <rect x="460" y="122" width="200" height="70" rx="14" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="560" y="152" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">api-gateway</text>
          <text x="560" y="174" textAnchor="middle" fontSize="12" fill="#64748b">container :8000</text>

          <rect x="700" y="122" width="240" height="70" rx="14" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="820" y="152" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">dashboard-ui</text>
          <text x="820" y="174" textAnchor="middle" fontSize="12" fill="#64748b">container :3000</text>

          <rect x="460" y="212" width="480" height="70" rx="14" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="700" y="242" textAnchor="middle" fontSize="13" fontWeight="700" fill="#0f172a">services + redis + ollama</text>
          <text x="700" y="264" textAnchor="middle" fontSize="12" fill="#64748b">roots/causality/epistemic/mmo/global/slm</text>
        </g>

        {/* Port mapping arrows */}
        <path d="M 380 154 L 460 154" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow3)" />
        <text x="420" y="142" fontSize="11" fill="#64748b">18000 → 8000</text>

        <path d="M 380 182 L 700 182" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow3)" />
        <text x="520" y="170" fontSize="11" fill="#64748b">13000 → 3000</text>
      </svg>
    </div>
  );
}

function DependencyDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 360" role="img" aria-label="Service dependency and health diagram">
        <defs>
          <filter id="shadowDeps" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrowDeps" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="336" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        <text x="520" y="44" textAnchor="middle" fontSize="14" fontWeight="800" fill="#0f172a">
          Health dependencies (typical)
        </text>

        {/* Core boxes */}
        {[
          { x: 420, y: 64, w: 200, h: 62, title: 'Dashboard UI', sub: 'calls /api/*' },
          { x: 420, y: 142, w: 200, h: 72, title: 'API Gateway', sub: 'auth · routing · rate limit' },
          { x: 220, y: 230, w: 220, h: 70, title: 'Global', sub: 'aggregates services' },
          { x: 540, y: 230, w: 220, h: 70, title: 'SLM', sub: 'AI endpoints' },
          { x: 840, y: 142, w: 160, h: 62, title: 'Redis', sub: 'rate limit/cache' },
          { x: 840, y: 230, w: 160, h: 70, title: 'Ollama', sub: 'optional models' },
        ].map((b) => (
          <g key={b.title} filter="url(#shadowDeps)">
            <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="14" fill="#f8fafc" stroke="#e2e8f0" />
            <text x={b.x + b.w / 2} y={b.y + 28} textAnchor="middle" fontSize="13" fontWeight="800" fill="#0f172a">
              {b.title}
            </text>
            <text x={b.x + b.w / 2} y={b.y + 50} textAnchor="middle" fontSize="12" fill="#64748b">
              {b.sub}
            </text>
          </g>
        ))}

        {/* Domain services */}
        {[
          { x: 140, label: 'Roots' },
          { x: 330, label: 'Causality' },
          { x: 520, label: 'Epistemic' },
          { x: 710, label: 'MMO' },
        ].map((s) => (
          <g key={s.label} filter="url(#shadowDeps)">
            <rect x={s.x} y="306" width="170" height="46" rx="14" fill="#ffffff" stroke="#e2e8f0" />
            <text x={s.x + 85} y="335" textAnchor="middle" fontSize="12.5" fontWeight="800" fill="#0f172a">
              {s.label}
            </text>
          </g>
        ))}

        {/* Arrows */}
        <path d="M 520 126 L 520 142" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />
        <text x="540" y="136" fontSize="11" fill="#64748b">depends on</text>

        <path d="M 520 214 L 330 230" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />
        <path d="M 520 214 L 650 230" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />

        <text x="420" y="224" fontSize="11" fill="#64748b">routes to</text>

        {/* Gateway -> Redis */}
        <path d="M 620 178 L 840 178" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />

        {/* Global -> domain services */}
        <path d="M 330 300 L 225 306" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />
        <path d="M 330 300 L 415 306" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />
        <path d="M 330 300 L 605 306" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />
        <path d="M 330 300 L 795 306" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" />

        <text x="220" y="292" fontSize="11" fill="#64748b">requires for aggregated views</text>

        {/* SLM -> Ollama (optional) */}
        <path d="M 760 265 L 840 265" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowDeps)" strokeDasharray="6 6" />
        <text x="790" y="252" fontSize="11" fill="#64748b">optional</text>
      </svg>
    </div>
  );
}

function RequestLifecycleDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 270" role="img" aria-label="Request lifecycle diagram">
        <defs>
          <filter id="shadowReq" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrowReq" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="246" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        {[
          { x: 60, label: 'Dashboard UI', sub: 'user action' },
          { x: 300, label: 'API Gateway', sub: 'auth + routing' },
          { x: 560, label: 'Service', sub: 'business logic' },
          { x: 810, label: 'SQLite / Files', sub: 'persisted state' },
        ].map((n) => (
          <g key={n.label} filter="url(#shadowReq)">
            <rect x={n.x} y="84" width="190" height="92" rx="14" fill="#f8fafc" stroke="#e2e8f0" />
            <text x={n.x + 95} y="122" textAnchor="middle" fontSize="13" fontWeight="800" fill="#0f172a">
              {n.label}
            </text>
            <text x={n.x + 95} y="146" textAnchor="middle" fontSize="12" fill="#64748b">
              {n.sub}
            </text>
          </g>
        ))}

        {/* Request path */}
        <path d="M 250 130 L 300 130" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowReq)" />
        <path d="M 490 130 L 560 130" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowReq)" />
        <path d="M 750 130 L 810 130" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowReq)" />

        <text x="270" y="116" fontSize="11" fill="#64748b">GET /api/roots</text>
        <text x="510" y="116" fontSize="11" fill="#64748b">routes</text>
        <text x="765" y="116" fontSize="11" fill="#64748b">read/write</text>

        {/* Response path */}
        <path d="M 810 198 L 60 198" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowReq)" />
        <text x="520" y="186" textAnchor="middle" fontSize="11" fill="#64748b">
          JSON response (200/4xx/5xx)
        </text>
      </svg>
    </div>
  );
}

function AIPipelineDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 300" role="img" aria-label="AI pipeline diagram">
        <defs>
          <filter id="shadowAI" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrowAI" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="276" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        {/* Nodes */}
        {[
          { x: 60, y: 110, w: 200, h: 86, title: 'Dashboard', sub: 'AI pages' },
          { x: 300, y: 110, w: 220, h: 86, title: 'Gateway', sub: '/api/slm/*' },
          { x: 560, y: 92, w: 220, h: 120, title: 'SLM Service', sub: 'model manager' },
          { x: 820, y: 72, w: 180, h: 76, title: 'Ollama', sub: 'preferred' },
          { x: 820, y: 170, w: 180, h: 76, title: 'Fallback', sub: 'degraded mode' },
        ].map((b) => (
          <g key={b.title} filter="url(#shadowAI)">
            <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="14" fill="#f8fafc" stroke="#e2e8f0" />
            <text x={b.x + b.w / 2} y={b.y + 32} textAnchor="middle" fontSize="13" fontWeight="800" fill="#0f172a">
              {b.title}
            </text>
            <text x={b.x + b.w / 2} y={b.y + 56} textAnchor="middle" fontSize="12" fill="#64748b">
              {b.sub}
            </text>
          </g>
        ))}

        {/* Flow arrows */}
        <path d="M 260 153 L 300 153" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowAI)" />
        <path d="M 520 153 L 560 153" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowAI)" />

        <path d="M 780 128 L 820 110" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowAI)" />
        <path d="M 780 176 L 820 208" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowAI)" strokeDasharray="6 6" />

        <text x="282" y="140" fontSize="11" fill="#64748b">prompt / query</text>
        <text x="538" y="140" fontSize="11" fill="#64748b">routes</text>
        <text x="790" y="96" fontSize="11" fill="#64748b">uses</text>
        <text x="790" y="236" fontSize="11" fill="#64748b">if unavailable</text>

        {/* Response */}
        <path d="M 820 260 L 60 260" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowAI)" />
        <text x="520" y="248" textAnchor="middle" fontSize="11" fill="#64748b">
          streamed or JSON response back to the UI
        </text>
      </svg>
    </div>
  );
}

function StorageLayoutDiagram() {
  return (
    <div className="arch-diagram">
      <svg className="arch-svg" viewBox="0 0 1040 290" role="img" aria-label="Data persistence layout diagram">
        <defs>
          <filter id="shadowData" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="rgba(15,23,42,0.18)" />
          </filter>
          <marker id="arrowData" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>

        <rect x="12" y="12" width="1016" height="266" rx="18" fill="#ffffff" stroke="#e2e8f0" />

        {/* Host box */}
        <g filter="url(#shadowData)">
          <rect x="60" y="64" width="410" height="170" rx="16" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="265" y="96" textAnchor="middle" fontSize="14" fontWeight="800" fill="#0f172a">
            Host filesystem (durable)
          </text>
          <text x="90" y="132" fontSize="12" fill="#64748b">OMNICORE_DATA_PATH        (SQLite)</text>
          <text x="90" y="156" fontSize="12" fill="#64748b">OMNICORE_LOGS_PATH        (logs)</text>
          <text x="90" y="180" fontSize="12" fill="#64748b">OMNICORE_SNAPSHOTS_PATH   (snapshots)</text>
          <text x="90" y="204" fontSize="12" fill="#64748b">OMNICORE_ONTOLOGIES_PATH  (ontologies)</text>
        </g>

        {/* Container box */}
        <g filter="url(#shadowData)">
          <rect x="570" y="64" width="410" height="170" rx="16" fill="#f8fafc" stroke="#e2e8f0" />
          <text x="775" y="96" textAnchor="middle" fontSize="14" fontWeight="800" fill="#0f172a">
            Containers (/app/* mounts)
          </text>
          <text x="600" y="132" fontSize="12" fill="#64748b">/app/data        → db files per service</text>
          <text x="600" y="156" fontSize="12" fill="#64748b">/app/logs        → service logs</text>
          <text x="600" y="180" fontSize="12" fill="#64748b">/app/snapshots   → exported artifacts</text>
          <text x="600" y="204" fontSize="12" fill="#64748b">/app/ontologies  → ontology files</text>
        </g>

        {/* Mount arrow */}
        <path d="M 470 148 L 570 148" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowData)" />
        <text x="520" y="132" textAnchor="middle" fontSize="11" fill="#64748b">bind mount</text>

        <text x="520" y="262" textAnchor="middle" fontSize="12" fill="#64748b">
          Keep these mapped to a stable host path so data survives container rebuilds and restarts.
        </text>
      </svg>
    </div>
  );
}

function Architecture() {
  const gatewayPort = import.meta.env.VITE_GATEWAY_PORT || '18000';
  const gatewayPublicUrl = import.meta.env.VITE_GATEWAY_PUBLIC_URL;
  const gatewayBaseUrl =
    gatewayPublicUrl ||
    (typeof window !== 'undefined'
      ? `${window.location.protocol}//${window.location.hostname}:${gatewayPort}`
      : `http://localhost:${gatewayPort}`);

  const gatewayDocsUrl = `${gatewayBaseUrl}/docs`;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Architecture</h1>
        <p className="page-subtitle">
          A visual and detailed reference for the OmniCore platform architecture: services, routing,
          data flow, deployment topology, ports, and operational practices.
        </p>
      </div>

      <div className="card guide-hero">
        <div className="guide-hero-inner">
          <div>
            <div className="guide-kicker">Reference</div>
            <h2 className="guide-hero-title">How OmniCore fits together</h2>
            <p className="guide-hero-text">
              OmniCore uses a microservice layout with a single API Gateway and a React dashboard.
              Each service owns its own storage and API, while the gateway provides unified access,
              authentication, and consistent routing.
            </p>
            <div className="guide-actions">
              <Link className="btn btn-primary" to="/guide" style={{ textDecoration: 'none' }}>
                User Guide
              </Link>
              <a className="btn btn-secondary" href={gatewayDocsUrl} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                API Docs
              </a>
              <Link className="btn btn-secondary" to="/health" style={{ textDecoration: 'none' }}>
                System Health
              </Link>
            </div>
          </div>
          <div className="guide-hero-panel">
            <div className="guide-mini">
              <div className="guide-mini-title">What you will find here</div>
              <ul className="guide-list">
                <li>System overview diagram (UI → Gateway → Services)</li>
                <li>Routing map for key API prefixes</li>
                <li>JWT auth flow used by the dashboard</li>
                <li>Deployment topology and port mapping (Podman)</li>
                <li>Persistence model (data/logs/snapshots/ontologies)</li>
              </ul>
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
              API docs:{' '}
              <a className="guide-link" href={gatewayDocsUrl} target="_blank" rel="noreferrer">
                {gatewayDocsUrl}
              </a>
            </div>
          </div>
        </aside>

        <div className="guide-content">
          <section id="overview" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">System Overview</h2>
            </div>
            <p className="guide-paragraph">
              At runtime, users interact with the Dashboard UI. The UI calls <code>/api/*</code> which
              is proxied to the API Gateway. The gateway enforces auth, applies rate limiting (Redis),
              and forwards calls to the correct service. Each service owns its own storage (SQLite
              files under the mounted <code>/app/data</code> directory by default).
            </p>
            <SystemOverviewDiagram />
          </section>

          <section id="services" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Services & Responsibilities</h2>
            </div>
            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">API Gateway</div>
                <div className="guide-card-text">
                  Unified entry point: JWT/API key auth, routing, rate limiting, and aggregated health.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Roots</div>
                <div className="guide-card-text">
                  Manages fundamental root types (EXTANT/ABSTRACT/MENTAL/FICTIVE) and the canonical entity registry.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Causality</div>
                <div className="guide-card-text">
                  Stores causal links between entities and supports summary analytics by causality type.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Epistemic</div>
                <div className="guide-card-text">
                  Stores epistemic annotations (certainty + basis) for entities to capture evidence and confidence.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">MMO</div>
                <div className="guide-card-text">
                  Meta-meta-ontology schema + metrics used to assess structure and quality.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Global</div>
                <div className="guide-card-text">
                  Global stats and system-level views. Often depends on other services being healthy.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">SLM</div>
                <div className="guide-card-text">
                  AI/SLM service for inference tasks (often backed by Ollama). Exposed via <code>/api/slm/*</code>.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Redis / Ollama</div>
              <div className="guide-card-text">
                Redis supports rate limiting and caching. Ollama hosts local models for SLM inference.
              </div>
            </div>
          </div>
          <p className="guide-paragraph" style={{ marginTop: 10 }}>
            The diagram below highlights practical runtime/health dependencies. It helps explain why the gateway may be
            considered unavailable if key dependencies fail to start or become healthy.
          </p>
          <DependencyDiagram />
        </section>

        <section id="api" className="card guide-section">
          <div className="card-header">
            <h2 className="card-title">API Gateway & Routing</h2>
            </div>
            <p className="guide-paragraph">
              The gateway routes requests by prefix. The most important mapping (dashboard-facing) looks like this:
            </p>
            <pre className="guide-code">
              <code>{`/api/roots*             -> roots-service
/api/causality-links*    -> causality-service
/api/causality-summary   -> causality-service
/api/annotations*        -> epistemic-service
/api/classes*            -> mmo-service
/api/slots*              -> mmo-service
/api/metrics*            -> mmo-service
/api/global/*            -> global-ontology-service
/api/system/health       -> global-ontology-service
/api/slm/*               -> slm-service`}</code>
            </pre>
            <p className="guide-paragraph">
              This design keeps the UI simple (one base URL) while allowing services to evolve independently.
            </p>
            <RequestLifecycleDiagram />
          </section>

          <section id="auth" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Auth & Security Flow</h2>
            </div>
            <p className="guide-paragraph">
              In production, the gateway requires authentication. The dashboard automatically requests a JWT from{' '}
              <code>/api/auth/token</code>, stores it locally, and attaches it to all requests. If a request returns 401,
              the UI drops the token and retries once.
            </p>
            <AuthFlowDiagram />
          </section>

          <section id="ai" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">AI / SLM Pipeline</h2>
            </div>
            <p className="guide-paragraph">
              The AI features are exposed via the gateway under <code>/api/slm/*</code>. The SLM service can use an
              Ollama backend when available. If Ollama is not available, the system may degrade AI capabilities but
              core CRUD features remain operational.
            </p>
            <pre className="guide-code">
              <code>{`Dashboard (AI pages)
   -> /api/slm/* (Gateway)
       -> slm-service
            -> Ollama (optional)  -> local model inference
            -> fallback/provider  -> limited or alternate behavior`}</code>
            </pre>
            <AIPipelineDiagram />
            <p className="guide-paragraph">
              Operational advice: treat AI outputs as suggestions. For production decision making, keep human review and
              provenance.
            </p>
          </section>

          <section id="deployment" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Deployment Topology (Podman)</h2>
            </div>
            <p className="guide-paragraph">
              On AlmaLinux with rootless Podman, the stack runs in an isolated container network. The gateway and dashboard
              are exposed on host ports for VPN/LAN access. Redis and Ollama can remain internal-only.
            </p>
            <DeploymentDiagram />
            <p className="guide-paragraph">
              Common host ports (recommended defaults):
            </p>
            <pre className="guide-code">
              <code>{`Gateway (public):     18000  -> container :8000
Dashboard (public):   13000  -> container :3000
Services (optional):  18001..18006 (same port in/out)
Redis/Ollama:         internal-only (no host bind by default)`}</code>
            </pre>
          </section>

          <section id="data" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Data & Persistence</h2>
            </div>
            <p className="guide-paragraph">
              Services use local storage (SQLite and file artifacts) under mounted directories. In Podman deployments,
              you should map these directories to a durable host location (e.g. <code>/mnt/extra/...</code>).
            </p>
            <pre className="guide-code">
              <code>{`Host paths (recommended)
  OMNICORE_DATA_PATH        -> /app/data
  OMNICORE_LOGS_PATH        -> /app/logs
  OMNICORE_SNAPSHOTS_PATH   -> /app/snapshots
  OMNICORE_ONTOLOGIES_PATH  -> /app/ontologies

Why this matters:
  - container rebuilds/restarts won't delete your data
   - logs are persisted for diagnosis
   - ontologies + snapshots remain available for reprocessing`}</code>
            </pre>
            <StorageLayoutDiagram />
          </section>

          <section id="observability" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Health, Logs & Operations</h2>
            </div>
            <div className="guide-grid">
              <div className="guide-card">
                <div className="guide-card-title">Health checks</div>
                <div className="guide-card-text">
                  Gateway health: <code>/health</code>. System overview: <code>/api/health/overview</code>.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Logs</div>
                <div className="guide-card-text">
                  Check container logs first, then persist logs to the host for longer history.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Common diagnosis</div>
                <div className="guide-card-text">
                  If a UI feature breaks: verify gateway health, then check System Health, then inspect the relevant service logs.
                </div>
              </div>
              <div className="guide-card">
                <div className="guide-card-title">Ports</div>
                <div className="guide-card-text">
                  If a port is busy, prefer changing host ports via env variables rather than editing code.
                </div>
              </div>
            </div>
            <details className="guide-details">
              <summary className="guide-summary">Common commands (Podman)</summary>
              <div className="guide-details-body">
                <pre className="guide-code">
                  <code>{`podman ps --format \"table {{.Names}}\\t{{.Status}}\\t{{.Ports}}\"
podman logs --tail 200 omnicore-gateway
podman logs --tail 200 omnicore-ui
curl -f http://127.0.0.1:18000/health`}</code>
                </pre>
              </div>
            </details>
          </section>

          <section id="credits" className="card guide-section">
            <div className="card-header">
              <h2 className="card-title">Team & Credits</h2>
            </div>
            <p className="guide-paragraph">
              This project is developed by <strong>Team BSU Masters 2025</strong>. Supervisor:{' '}
              <strong>Teacher KREMENCHUTSKIY ANATOLIY</strong>. Developer:{' '}
              <strong>Fakhriddin Khushnazarov</strong>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

export default Architecture;
