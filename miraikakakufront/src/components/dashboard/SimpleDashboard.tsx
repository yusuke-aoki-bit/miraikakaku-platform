'use client';

import React from 'react';

export default function SimpleDashboard() {
  return (
    <div className="p-6 bg-red-100">
      <h1 className="text-3xl font-bold text-red-800">
        Simple Dashboard Test
      </h1>
      <p className="text-red-600 mt-4">
        このページが表示されれば、基本的な表示は動作しています。
      </p>
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="bg-red-200 p-4 rounded">
          <h2 className="font-bold text-red-900">日経平均</h2>
          <p className="text-red-700">33,000</p>
        </div>
        <div className="bg-red-200 p-4 rounded">
          <h2 className="font-bold text-red-900">TOPIX</h2>
          <p className="text-red-700">2,300</p>
        </div>
        <div className="bg-red-200 p-4 rounded">
          <h2 className="font-bold text-red-900">DOW</h2>
          <p className="text-red-700">34,000</p>
        </div>
        <div className="bg-red-200 p-4 rounded">
          <h2 className="font-bold text-red-900">S&P 500</h2>
          <p className="text-red-700">4,500</p>
        </div>
      </div>
    </div>
  );
}