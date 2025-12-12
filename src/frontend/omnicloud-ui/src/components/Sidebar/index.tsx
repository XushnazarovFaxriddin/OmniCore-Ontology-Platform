import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/roots', label: 'Roots', icon: '🌳' },
  { path: '/causality', label: 'Causality', icon: '🔗' },
  { path: '/epistemic', label: 'Epistemic', icon: '📚' },
  { path: '/mmo', label: 'MMO Schema', icon: '🔷' },
  { path: '/health', label: 'System Health', icon: '💚' },
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
      </nav>
    </aside>
  );
}

export default Sidebar;
