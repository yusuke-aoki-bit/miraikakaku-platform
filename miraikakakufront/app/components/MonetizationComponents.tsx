'use client';

import React from 'react';
import { ShoppingCart, DollarSign } from 'lucide-react';

export function AmazonAssociatesWidget() {
  return (
    <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-6">
      <div className="flex items-center mb-4">
        <ShoppingCart className="w-6 h-6 text-orange-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">
          Investment Resources
        </h3>
      </div>
      
      <div className="space-y-4">
        <div className="bg-white rounded-md p-4 border border-orange-100">
          <h4 className="font-medium text-gray-900 mb-2">
            📚 Recommended Investment Books
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Enhance your investment knowledge with these bestselling books on stock analysis and market strategies.
          </p>
          <button className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            View Book Recommendations
          </button>
        </div>
        
        <div className="bg-white rounded-md p-4 border border-orange-100">
          <h4 className="font-medium text-gray-900 mb-2">
            💼 Investment Tools & Software
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Professional-grade tools for portfolio management and market analysis.
          </p>
          <button className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            Shop Investment Tools
          </button>
        </div>
      </div>
      
      <p className="text-xs text-gray-500 mt-4">
        * As an Amazon Associate, we earn from qualifying purchases.
      </p>
    </div>
  );
}

export function GoogleAdSenseWidget() {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
      <div className="flex items-center mb-4">
        <DollarSign className="w-6 h-6 text-blue-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">
          Financial Services
        </h3>
      </div>
      
      <div className="space-y-4">
        <div className="bg-white rounded-md p-4 border border-blue-100">
          <h4 className="font-medium text-gray-900 mb-2">
            🏦 Open a Trading Account
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Start your investment journey with commission-free stock trading platforms.
          </p>
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            Compare Brokers
          </button>
        </div>
        
        <div className="bg-white rounded-md p-4 border border-blue-100">
          <h4 className="font-medium text-gray-900 mb-2">
            📊 Premium Market Data
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Access real-time market data and advanced analytics for better investment decisions.
          </p>
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            Get Premium Access
          </button>
        </div>
      </div>
    </div>
  );
}

export function NewsletterSignup() {
  return (
    <div className="bg-gradient-to-r from-green-50 to-teal-50 border border-green-200 rounded-lg p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        📈 Stay Updated
      </h3>
      <p className="text-gray-700 mb-4">
        Get weekly AI-powered market insights and stock predictions delivered to your inbox.
      </p>
      
      <div className="flex gap-3">
        <input
          type="email"
          placeholder="Enter your email"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md transition-colors font-medium">
          Subscribe
        </button>
      </div>
      
      <p className="text-xs text-gray-500 mt-2">
        No spam. Unsubscribe at any time.
      </p>
    </div>
  );
}