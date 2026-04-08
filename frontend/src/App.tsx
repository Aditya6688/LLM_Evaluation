import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import QueryInterface from './components/QueryInterface';
import ReviewQueue from './components/ReviewQueue';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/query" element={<QueryInterface />} />
        <Route path="/reviews" element={<ReviewQueue />} />
      </Routes>
    </Layout>
  );
}

export default App;
