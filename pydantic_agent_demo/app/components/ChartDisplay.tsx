"use client";

import React from 'react';
import { useState, useEffect } from 'react';

interface ChartData {
  chart_base64?: string;
  chart_html?: string;
  summary?: string;
  data_insights?: string[];
}

interface ChartDisplayProps {
  chartData: ChartData | null;
}

export const ChartDisplay: React.FC<ChartDisplayProps> = ({ chartData }) => {
  const [displayType, setDisplayType] = useState<'static' | 'interactive'>('static');

  if (!chartData) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-gray-800">📊 Generated Chart</h3>
        {chartData.chart_base64 && chartData.chart_html && (
          <div className="flex gap-2">
            <button
              onClick={() => setDisplayType('static')}
              className={`px-3 py-1 rounded text-sm ${
                displayType === 'static' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Static
            </button>
            <button
              onClick={() => setDisplayType('interactive')}
              className={`px-3 py-1 rounded text-sm ${
                displayType === 'interactive' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Interactive
            </button>
          </div>
        )}
      </div>

      {/* Chart Display */}
      <div className="mb-4">
        {displayType === 'static' && chartData.chart_base64 ? (
          <div className="text-center">
            <img 
              src={`data:image/png;base64,${chartData.chart_base64}`} 
              alt="Generated Chart" 
              className="max-w-full h-auto mx-auto rounded border"
            />
          </div>
        ) : displayType === 'interactive' && chartData.chart_html ? (
          <div 
            dangerouslySetInnerHTML={{ __html: chartData.chart_html }}
            className="w-full"
          />
        ) : chartData.chart_base64 ? (
          <div className="text-center">
            <img 
              src={`data:image/png;base64,${chartData.chart_base64}`} 
              alt="Generated Chart" 
              className="max-w-full h-auto mx-auto rounded border"
            />
          </div>
        ) : (
          <div className="text-center p-8 text-gray-500">
            <p>Chart generation in progress...</p>
          </div>
        )}
      </div>

      {/* Summary */}
      {chartData.summary && (
        <div className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-2">Summary</h4>
          <p className="text-gray-600">{chartData.summary}</p>
        </div>
      )}

      {/* Insights */}
      {chartData.data_insights && chartData.data_insights.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Key Insights</h4>
          <ul className="list-disc list-inside space-y-1">
            {chartData.data_insights.map((insight, index) => (
              <li key={index} className="text-gray-600">{insight}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ChartDisplay;