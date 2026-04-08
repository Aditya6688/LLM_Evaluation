import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { getDashboardStats } from '../api/client';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444'];

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    refetchInterval: 30000,
  });

  if (isLoading || !stats) {
    return <div className="text-gray-500">Loading dashboard...</div>;
  }

  const pieData = Object.entries(stats.model_usage).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KpiCard title="Total Queries" value={stats.total_queries} />
        <KpiCard
          title="Avg Faithfulness"
          value={stats.avg_faithfulness.toFixed(3)}
          color={stats.avg_faithfulness >= 0.7 ? 'text-green-600' : 'text-red-600'}
        />
        <KpiCard
          title="Retry Rate"
          value={`${(stats.retry_rate * 100).toFixed(1)}%`}
          color={stats.retry_rate > 0.3 ? 'text-red-600' : 'text-green-600'}
        />
        <KpiCard
          title="Pending Reviews"
          value={stats.review_queue_pending}
          color={stats.review_queue_pending > 0 ? 'text-yellow-600' : 'text-green-600'}
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Score Trend Chart */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-semibold mb-4 text-gray-600">Score Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.score_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="avg_faithfulness"
                stroke="#3b82f6"
                name="Faithfulness"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="avg_relevancy"
                stroke="#10b981"
                name="Relevancy"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Model Usage Pie */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-semibold mb-4 text-gray-600">Model Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) =>
                  `${name} (${(percent * 100).toFixed(0)}%)`
                }
              >
                {pieData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cost */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <span className="text-sm text-gray-600">Total Cost: </span>
        <span className="text-lg font-bold">${stats.cost_total_usd.toFixed(4)}</span>
      </div>
    </div>
  );
}

function KpiCard({
  title,
  value,
  color = 'text-gray-900',
}: {
  title: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{title}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}
