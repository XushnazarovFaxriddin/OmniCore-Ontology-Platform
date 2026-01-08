import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/roots', label: 'Roots', icon: '🌳' },
  { path: '/causality', label: 'Causality', icon: '🔗' },
  { path: '/epistemic', label: 'Epistemic', icon: '📚' },
  { path: '/mmo', label: 'MMO Schema', icon: '🔷' },
  { path: '/health', label: 'System Health', icon: '💚' },
  { path: '/architecture', label: 'Architecture', icon: '🧭' },
  { path: '/guide', label: 'User Guide', icon: '📘' },
];

const aiNavItems = [
  { path: '/ai/chat', label: 'AI Chat', icon: '💬' },
  { path: '/ai/assistant', label: 'AI Assistant', icon: '🤖' },
  { path: '/ai/search', label: 'AI Search', icon: '🔍' },
  { path: '/ai/models', label: 'AI Models', icon: '⚙️' },
  { path: '/strategic', label: 'Strategic AI', icon: '🎯' },
  { path: '/debate', label: 'Debate Lab', icon: '⚖️' },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">OmniCore</h1>
        <p className="sidebar-subtitle">Ontology Platform</p>
      </div>
      <nav>
        <ul className="sidebar-nav">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-nav-item ${isActive ? 'active' : ''}`
                }
              >
                <span className="sidebar-icon">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="sidebar-section">
          <h3 className="sidebar-section-title">AI / SLM</h3>
          <ul className="sidebar-nav">
            {aiNavItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `sidebar-nav-item ${isActive ? 'active' : ''}`
                  }
                >
                  <span className="sidebar-icon">{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;
