'use client';

import { useEffect, useState } from 'react';

export default function TestPage() {
  const [apiStatus, setApiStatus] = useState('testing...'
  const [popularStocks, setPopularStocks] = useState([]
  useEffect(() => {
    const testApi = async () => {
      try {
        // Test health endpoint
        const healthResponse = await fetch('/api/health'
        const healthData = await healthResponse.json(
        // Test popular stocks endpoint
        const stocksResponse = await fetch('/api/finance/stocks/search/popular'
        const stocksData = await stocksResponse.json(
        setApiStatus(`Health: ${healthData.status}, Stocks: ${stocksData.count} items`
        setPopularStocks(stocksData.popular_stocks || []
      } catch (error) {
        setApiStatus(`Error: ${error.message}`
      }
    };

    testApi(
  }, []
  return (
    <div style={{ padding: '20px', backgroundColor: '#0f0f0f', color: '#f1f1f1', minHeight: '100vh' }}>
      <h1>API Connection Test</h1>
      <p>Status: {apiStatus}</p>

      <h2>Popular Stocks ({popularStocks.length})</h2>
      <ul>
        {popularStocks.slice(0, 5).map((stock, index) => (
          <li key={index}>
            <strong>{stock.symbol}</strong> - {stock.display}
          </li>
        ))}
      </ul>

      <div style={{ marginTop: '30px' }}>
        <a href="/" style={{ color: '#3ea6ff' }}>← Back to Home</a>
      </div>
    </div>
}