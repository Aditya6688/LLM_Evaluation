import { Link, useLocation } from 'react-router-dom';
import type { ReactNode } from 'react';

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/query', label: 'Query' },
  { path: '/reviews', label: 'Reviews' },
];

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-lg font-bold">LLM Eval</h1>
          <p className="text-xs text-gray-400">Pipeline Dashboard</p>
        </div>
        <nav className="flex-1 p-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-2 rounded mb-1 text-sm ${
                location.pathname === item.path
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  );
}
