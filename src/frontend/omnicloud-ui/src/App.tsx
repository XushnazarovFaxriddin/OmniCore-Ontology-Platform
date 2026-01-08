import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import GlobalDashboard from './pages/GlobalDashboard';
import RootsView from './pages/RootsView';
import CausalityView from './pages/CausalityView';
import EpistemicView from './pages/EpistemicView';
import MMOSchemaView from './pages/MMOSchemaView';
import SystemHealth from './pages/SystemHealth';
import AIChat from './pages/AIChat';
import AIAssistant from './pages/AIAssistant';
import AISearch from './pages/AISearch';
import AIModels from './pages/AIModels';
import UserGuide from './pages/UserGuide';
import Architecture from './pages/Architecture';
import StrategicDashboard from './pages/StrategicDashboard';
import DebateVisualizer from './pages/DebateVisualizer';

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
          {/* AI Routes */}
          <Route path="/ai/chat" element={<AIChat />} />
          <Route path="/ai/assistant" element={<AIAssistant />} />
          <Route path="/ai/search" element={<AISearch />} />
          <Route path="/ai/models" element={<AIModels />} />
          <Route path="/strategic" element={<StrategicDashboard />} />
          <Route path="/debate" element={<DebateVisualizer />} />
          <Route path="/guide" element={<UserGuide />} />
          <Route path="/architecture" element={<Architecture />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
