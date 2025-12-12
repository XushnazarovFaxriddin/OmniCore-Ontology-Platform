import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import GlobalDashboard from './pages/GlobalDashboard';
import RootsView from './pages/RootsView';
import CausalityView from './pages/CausalityView';
import EpistemicView from './pages/EpistemicView';
import MMOSchemaView from './pages/MMOSchemaView';
import SystemHealth from './pages/SystemHealth';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<GlobalDashboard />} />
          <Route path="/roots" element={<RootsView />} />
          <Route path="/causality" element={<CausalityView />} />
          <Route path="/epistemic" element={<EpistemicView />} />
          <Route path="/mmo" element={<MMOSchemaView />} />
          <Route path="/health" element={<SystemHealth />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
