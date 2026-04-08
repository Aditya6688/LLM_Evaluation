import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { queryPipeline, ingestFile, ingestUrl } from '../api/client';
import type { QueryResponse } from '../types';

function scoreColor(score: number): string {
  if (score >= 0.8) return 'text-green-600 bg-green-50';
  if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
}

export default function QueryInterface() {
  const [question, setQuestion] = useState('');
  const [reference, setReference] = useState('');
  const [result, setResult] = useState<QueryResponse | null>(null);

  // Ingest state
  const [ingestMode, setIngestMode] = useState<'file' | 'url'>('file');
  const [url, setUrl] = useState('');

  const queryMutation = useMutation({
    mutationFn: () => queryPipeline(question, reference || undefined),
    onSuccess: (data) => setResult(data),
  });

  const ingestFileMutation = useMutation({
    mutationFn: (file: File) => ingestFile(file),
  });

  const ingestUrlMutation = useMutation({
    mutationFn: (u: string) => ingestUrl(u),
  });

  return (
    <div className="max-w-4xl">
      <h2 className="text-2xl font-bold mb-6">Query Pipeline</h2>

      {/* Ingest Section */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Ingest Documents</h3>
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setIngestMode('file')}
            className={`px-3 py-1 text-sm rounded ${ingestMode === 'file' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
          >
            PDF Upload
          </button>
          <button
            onClick={() => setIngestMode('url')}
            className={`px-3 py-1 text-sm rounded ${ingestMode === 'url' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
          >
            URL
          </button>
        </div>

        {ingestMode === 'file' ? (
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) ingestFileMutation.mutate(file);
            }}
            className="text-sm"
          />
        ) : (
          <div className="flex gap-2">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              className="flex-1 border rounded px-3 py-1 text-sm"
            />
            <button
              onClick={() => url && ingestUrlMutation.mutate(url)}
              disabled={ingestUrlMutation.isPending}
              className="px-4 py-1 bg-blue-600 text-white text-sm rounded disabled:opacity-50"
            >
              Ingest
            </button>
          </div>
        )}

        {(ingestFileMutation.isSuccess || ingestUrlMutation.isSuccess) && (
          <p className="text-green-600 text-sm mt-2">
            Ingested {(ingestFileMutation.data || ingestUrlMutation.data)?.chunks_stored} chunks
          </p>
        )}
      </div>

      {/* Query Section */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Ask a Question</h3>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question..."
          rows={3}
          className="w-full border rounded px-3 py-2 text-sm mb-2"
        />
        <input
          type="text"
          value={reference}
          onChange={(e) => setReference(e.target.value)}
          placeholder="Reference answer (optional, for context_recall metric)"
          className="w-full border rounded px-3 py-2 text-sm mb-3"
        />
        <button
          onClick={() => queryMutation.mutate()}
          disabled={!question || queryMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {queryMutation.isPending ? 'Processing...' : 'Submit Query'}
        </button>
      </div>

      {/* Results */}
      {queryMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4 text-sm text-red-700">
          Error: {queryMutation.error?.message}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-lg shadow p-4">
          {/* Meta */}
          <div className="flex gap-3 mb-4 text-xs">
            <span className="bg-gray-100 px-2 py-1 rounded">Model: {result.model_used}</span>
            {result.is_retry && (
              <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded">Retried</span>
            )}
          </div>

          {/* Answer */}
          <h4 className="text-sm font-semibold text-gray-600 mb-1">Answer</h4>
          <p className="text-sm mb-4 whitespace-pre-wrap">{result.answer}</p>

          {/* Eval Scores */}
          <h4 className="text-sm font-semibold text-gray-600 mb-2">Evaluation Scores</h4>
          <div className="grid grid-cols-4 gap-2 mb-4">
            {Object.entries(result.eval_scores).map(([key, value]) =>
              value !== null ? (
                <div key={key} className={`rounded p-2 text-center ${scoreColor(value)}`}>
                  <p className="text-xs capitalize">{key.replace('_', ' ')}</p>
                  <p className="text-lg font-bold">{value.toFixed(3)}</p>
                </div>
              ) : null
            )}
          </div>

          {/* Contexts */}
          <details className="text-sm">
            <summary className="cursor-pointer text-gray-600 font-semibold">
              Retrieved Contexts ({result.contexts.length})
            </summary>
            <div className="mt-2 space-y-2">
              {result.contexts.map((ctx, i) => (
                <div key={i} className="bg-gray-50 rounded p-2 text-xs">
                  {ctx}
                </div>
              ))}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
