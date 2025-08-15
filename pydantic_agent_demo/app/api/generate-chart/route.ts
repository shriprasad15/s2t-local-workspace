import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query, csv_data } = await request.json();

    if (!query || !csv_data) {
      return NextResponse.json(
        { error: 'Query and CSV data are required' },
        { status: 400 }
      );
    }

    // Call the Python backend to generate the chart
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        csv_data: csv_data,
        chart_type: 'auto'
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.statusText}`);
    }

    const chartData = await response.json();
    return NextResponse.json(chartData);

  } catch (error) {
    console.error('Chart generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate chart' },
      { status: 500 }
    );
  }
}