import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getReviewQueue, resolveReviewItem } from '../api/client';

export default function ReviewQueue() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('pending');

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['review-queue', activeTab],
    queryFn: () => getReviewQueue(activeTab),
  });

  const resolveMutation = useMutation({
    mutationFn: ({
      id,
      status,
      note,
    }: {
      id: string;
      status: string;
      note?: string;
    }) => resolveReviewItem(id, status, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-queue'] });
    },
  });

  const [resolveNote, setResolveNote] = useState<Record<string, string>>({});

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Review Queue</h2>

      {/* Tab bar */}
      <div className="flex gap-2 mb-4">
        {['pending', 'resolved', 'dismissed'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1 text-sm rounded capitalize ${
              activeTab === tab ? 'bg-blue-600 text-white' : 'bg-gray-100'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-gray-500 text-sm">No {activeTab} items.</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="text-sm font-medium">{item.reason}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    item.status === 'pending'
                      ? 'bg-yellow-100 text-yellow-700'
                      : item.status === 'resolved'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {item.status}
                </span>
              </div>

              {item.status === 'pending' && (
                <div className="mt-3 flex gap-2 items-end">
                  <input
                    type="text"
                    placeholder="Resolution note (optional)"
                    value={resolveNote[item.id] || ''}
                    onChange={(e) =>
                      setResolveNote((prev) => ({
                        ...prev,
                        [item.id]: e.target.value,
                      }))
                    }
                    className="flex-1 border rounded px-2 py-1 text-sm"
                  />
                  <button
                    onClick={() =>
                      resolveMutation.mutate({
                        id: item.id,
                        status: 'resolved',
                        note: resolveNote[item.id],
                      })
                    }
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded"
                  >
                    Resolve
                  </button>
                  <button
                    onClick={() =>
                      resolveMutation.mutate({
                        id: item.id,
                        status: 'dismissed',
                      })
                    }
                    className="px-3 py-1 bg-gray-400 text-white text-sm rounded"
                  >
                    Dismiss
                  </button>
                </div>
              )}

              {item.resolution_note && (
                <p className="text-xs text-gray-500 mt-2">
                  Note: {item.resolution_note}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
