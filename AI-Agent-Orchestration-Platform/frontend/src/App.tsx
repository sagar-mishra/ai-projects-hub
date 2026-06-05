import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Workflows from './pages/Workflows';
import Monitor from './pages/Monitor';
import Templates from './pages/Templates';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/monitor" element={<Monitor />} />
          <Route path="/templates" element={<Templates />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
