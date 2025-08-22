'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Star, TrendingUp, TrendingDown, Activity, DollarSign, Calendar, Info } from 'lucide-react';
import Link from 'next/link';
import TripleChart from '@/components/charts/TripleChart';
import InvestmentRecommendation from '@/components/investment/InvestmentRecommendation';

interface StockData {
  symbol: string;
  companyName: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  volume: string;
  marketCap: string;
  per: number;
  pbr: number;
  dividendYield: number;
}

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params?.symbol as string;
  
  const [stockData, setStockData] = useState<StockData>({
    symbol: symbol || '7203',
    companyName: 'トヨタ自動車',
    currentPrice: 2543.0,
    change: 45.5,
    changePercent: 1.82,
    high: 2555,
    low: 2498,
    open: 2500,
    previousClose: 2497.5,
    volume: '12.3M',
    marketCap: '35.2兆円',
    per: 10.5,
    pbr: 1.2,
    dividendYield: 2.8
  });

  const [isInWatchlist, setIsInWatchlist] = useState(false);

  // Check if stock is in watchlist
  useEffect(() => {
    const watchlist = localStorage.getItem('watchlist');
    if (watchlist) {
      const parsed = JSON.parse(watchlist);
      setIsInWatchlist(parsed.some((item: any) => item.symbol === symbol));
    }
  }, [symbol]);

  const toggleWatchlist = () => {
    const watchlist = localStorage.getItem('watchlist');
    let parsed = watchlist ? JSON.parse(watchlist) : [];
    
    if (isInWatchlist) {
      parsed = parsed.filter((item: any) => item.symbol !== symbol);
    } else {
      parsed.push({
        symbol: stockData.symbol,
        name: stockData.companyName,
        price: stockData.currentPrice,
        change: stockData.change,
        changePercent: stockData.changePercent
      });
    }
    
    localStorage.setItem('watchlist', JSON.stringify(parsed));
    setIsInWatchlist(!isInWatchlist);
  };

  return (
    <div className="min-h-full bg-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Link 
              href="/"
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              aria-label="戻る"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </Link>
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-white">{stockData.symbol}</h1>
                <button
                  onClick={toggleWatchlist}
                  className={`p-2 rounded-lg transition-all ${
                    isInWatchlist 
                      ? 'bg-yellow-500/20 text-yellow-400' 
                      : 'bg-gray-800 text-gray-400 hover:text-yellow-400'
                  }`}
                  aria-label={isInWatchlist ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
                >
                  <Star className={`w-5 h-5 ${isInWatchlist ? 'fill-current' : ''}`} />
                </button>
              </div>
              <p className="text-gray-400">{stockData.companyName}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold text-white">
              ¥{stockData.currentPrice.toLocaleString()}
            </div>
            <div className={`flex items-center justify-end space-x-2 ${
              stockData.change > 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {stockData.change > 0 ? (
                <><TrendingUp className="w-5 h-5" /><span className="sr-only">上昇</span></>
              ) : (
                <><TrendingDown className="w-5 h-5" /><span className="sr-only">下落</span></>
              )}
              <span className="font-medium">
                {stockData.change > 0 ? '+' : ''}{stockData.change} ({stockData.changePercent > 0 ? '+' : ''}{stockData.changePercent}%)
              </span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart Section */}
          <div className="lg:col-span-2">
            <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-6">
              <TripleChart symbol={symbol} />
            </div>

            {/* Key Stats */}
            <div className="mt-6 bg-gray-900/50 rounded-2xl border border-gray-800/50 p-6">
              <h3 className="text-xl font-bold text-white mb-4">主要指標</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="始値" value={`¥${stockData.open.toLocaleString()}`} />
                <StatCard label="高値" value={`¥${stockData.high.toLocaleString()}`} />
                <StatCard label="安値" value={`¥${stockData.low.toLocaleString()}`} />
                <StatCard label="前日終値" value={`¥${stockData.previousClose.toLocaleString()}`} />
                <StatCard label="出来高" value={stockData.volume} />
                <StatCard label="時価総額" value={stockData.marketCap} />
                <StatCard label="PER" value={`${stockData.per}倍`} />
                <StatCard label="配当利回り" value={`${stockData.dividendYield}%`} />
              </div>
            </div>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Trading Actions */}
            <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-6">
              <h3 className="text-xl font-bold text-white mb-4">取引</h3>
              <div className="space-y-3">
                <button className="w-full py-3 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-500/30 transition-all">
                  買い注文
                </button>
                <button className="w-full py-3 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-all">
                  売り注文
                </button>
              </div>
            </div>

            {/* AI Investment Recommendation */}
            <div>
              <InvestmentRecommendation 
                symbol={stockData.symbol} 
                currentPrice={stockData.currentPrice}
                showDetailed={true}
              />
            </div>

            {/* Related Stocks */}
            <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-6">
              <h3 className="text-xl font-bold text-white mb-4">関連銘柄</h3>
              <div className="space-y-3">
                <RelatedStock symbol="7201" name="日産自動車" change={2.3} />
                <RelatedStock symbol="7267" name="ホンダ" change={-0.8} />
                <RelatedStock symbol="7269" name="スズキ" change={1.5} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-black/30 rounded-lg p-3">
      <div className="text-gray-400 text-sm mb-1">{label}</div>
      <div className="text-white font-medium">{value}</div>
    </div>
  );
}

function RelatedStock({ symbol, name, change }: { symbol: string; name: string; change: number }) {
  return (
    <Link 
      href={`/stock/${symbol}`}
      className="flex items-center justify-between p-3 bg-black/30 rounded-lg hover:bg-black/50 transition-colors cursor-pointer"
    >
      <div>
        <div className="text-white font-medium">{symbol}</div>
        <div className="text-gray-400 text-sm">{name}</div>
      </div>
      <div className={`font-medium ${change > 0 ? 'text-green-400' : 'text-red-400'}`}>
        {change > 0 ? '+' : ''}{change}%
      </div>
    </Link>
  );
}