"use client";

import "@copilotkit/react-ui/styles.css";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import React, { useState, useRef, useEffect } from "react";
import { Upload, FileText, X } from "lucide-react";
import ChartDisplay from "./components/ChartDisplay";

export default function Home() {
  const [csvData, setCsvData] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [chartData, setChartData] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    setIsUploading(true);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setCsvData(text);
      setFileName(file.name);
      setIsUploading(false);
    };
    
    reader.onerror = () => {
      alert('Error reading file');
      setIsUploading(false);
    };
    
    reader.readAsText(file);
  };

  const clearFile = () => {
    setCsvData("");
    setFileName("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const useSampleData = () => {
    const sampleData = `Date,Sales,Region,Product
2024-01-01,1000,North,Widget A
2024-01-02,1200,South,Widget B
2024-01-03,800,East,Widget A
2024-01-04,1500,West,Widget C
2024-01-05,1100,North,Widget B
2024-01-06,1300,South,Widget A
2024-01-07,900,East,Widget C
2024-01-08,1600,West,Widget A`;
    
    setCsvData(sampleData);
    setFileName("sample_data.csv");
  };

  // Make CSV data available to CopilotKit context
  useCopilotReadable({
    description: "Current CSV data loaded by the user",
    value: csvData ? {
      csvData: csvData,
      fileName: fileName,
      hasData: true
    } : {
      csvData: "",
      fileName: "",
      hasData: false
    }
  });

  // Function to generate charts via backend API
  const generateChart = async (query: string) => {
    if (!csvData) {
      alert('Please upload CSV data first');
      return;
    }

    try {
      const response = await fetch('/api/generate-chart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          csv_data: csvData
        })
      });

      if (response.ok) {
        const result = await response.json();
        setChartData(result);
      }
    } catch (error) {
      console.error('Error generating chart:', error);
    }
  };

  // Enhanced CopilotKit integration - intercept messages to extract chart data
  const [lastMessage, setLastMessage] = useState<any>(null);

  // Monitor CopilotKit messages for chart data
  useEffect(() => {
    const interceptCopilotMessages = () => {
      // This is a workaround to capture chart data from CopilotKit responses
      const originalFetch = window.fetch;
      window.fetch = async function(...args) {
        const response = await originalFetch.apply(this, args);
        
        // Check if this is a CopilotKit API call
        if (args[0] && typeof args[0] === 'string' && args[0].includes('/api/copilotkit')) {
          try {
            const clonedResponse = response.clone();
            const data = await clonedResponse.json();
            
            // Check if the response contains chart data
            if (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.chart_data) {
              const chartData = data.choices[0].message.chart_data;
              setChartData(chartData);
            }
          } catch (e) {
            // Ignore JSON parsing errors
          }
        }
        
        return response;
      };
      
      return () => {
        window.fetch = originalFetch;
      };
    };
    
    const cleanup = interceptCopilotMessages();
    return cleanup;
  }, []);

  // CopilotKit action for generating charts (fallback method)
  useCopilotAction({
    name: "generateChart",
    description: "Generate a chart from CSV data based on user's natural language query",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "Natural language query describing what chart to create",
        required: true,
      }
    ],
    handler: async ({ query }) => {
      if (!csvData) {
        return "Please upload CSV data first before generating charts.";
      }

      try {
        const response = await fetch('/api/generate-chart', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query,
            csv_data: csvData
          })
        });

        if (response.ok) {
          const result = await response.json();
          setChartData(result);
          return `Chart generated successfully! ${result.summary || 'Chart shows ' + query}`;
        } else {
          return "Failed to generate chart. Please try again.";
        }
      } catch (error) {
        console.error('Error generating chart:', error);
        return "Error generating chart. Please check your data and try again.";
      }
    },
  });

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-4 text-center">
          📊 CSV Chart Agent
        </h1>
        <p className="text-lg text-gray-600 mb-8 text-center">
          Upload your CSV data and ask questions in natural language to get beautiful charts and insights!
        </p>
        
        {/* CSV Upload Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <Upload className="mr-2" />
            Upload CSV Data
          </h2>
          
          {!fileName ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                id="csv-upload"
              />
              <label
                htmlFor="csv-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <FileText className="w-12 h-12 text-gray-400 mb-4" />
                <span className="text-lg text-gray-600 mb-2">
                  {isUploading ? "Uploading..." : "Click to upload your CSV file"}
                </span>
                <span className="text-sm text-gray-400">
                  Supports .csv files up to 10MB
                </span>
              </label>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800 font-medium">{fileName}</span>
                <span className="text-green-600 ml-2">✓ Loaded successfully</span>
              </div>
              <button
                onClick={clearFile}
                className="text-red-500 hover:text-red-700 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
          
          <div className="mt-4 flex gap-2">
            <button
              onClick={useSampleData}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Use Sample Data
            </button>
            {csvData && (
              <button
                onClick={clearFile}
                className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors text-sm"
              >
                Clear Data
              </button>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Welcome to CSV Chart Agent
          </h2>
          <p className="text-gray-600 mb-4">
            This is your AI-powered CSV data analysis assistant. {csvData ? "Your CSV data is loaded! " : "Upload CSV data first, then "} Use the chat sidebar to:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>Ask questions about your CSV data</li>
            <li>Get recommendations for chart types</li>
            <li>Learn about data visualization techniques</li>
            <li>Understand statistical concepts</li>
            <li>Get insights about data patterns and trends</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            Sample Questions to Try:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-blue-800 font-medium">
                "What's the best chart for showing trends over time?"
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-green-800 font-medium">
                "How do I compare different categories in my data?"
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-purple-800 font-medium">
                "What chart should I use for correlation analysis?"
              </p>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <p className="text-orange-800 font-medium">
                "How can I visualize data distribution?"
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Display */}
      <ChartDisplay chartData={chartData} />

      <CopilotSidebar
        labels={{
          title: "CSV Chart Assistant",
          initial: "Hi! I'm your CSV data analysis expert. I can help you understand your data, suggest appropriate visualizations, and provide insights about data patterns and trends. How can I assist you today?",
        }}
      />
    </main>
  );
}