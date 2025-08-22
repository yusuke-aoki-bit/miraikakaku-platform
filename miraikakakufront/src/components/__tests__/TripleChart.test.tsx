import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TripleChart from '../charts/TripleChart';

// EnhancedStockChartのモック
jest.mock('../charts/EnhancedStockChart', () => {
  return function MockEnhancedStockChart({ symbol, chartType }: { symbol: string; chartType: string }) {
    return (
      <div data-testid={`enhanced-chart-${chartType}`}>
        Mock Enhanced Chart for {symbol} - {chartType}
      </div>
    );
  };
});

describe('TripleChart', () => {
  const defaultProps = {
    symbol: 'AAPL',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基本表示テスト', () => {
    it('コンポーネントが正常にレンダリングされる', () => {
      render(<TripleChart {...defaultProps} />);
      
      // 3つのチャートセクションが表示される
      expect(screen.getByText('実績')).toBeInTheDocument();
      expect(screen.getByText('過去予測')).toBeInTheDocument();
      expect(screen.getByText('未来予測')).toBeInTheDocument();
    });

    it('正しいレイアウトクラスが適用される', () => {
      const { container } = render(<TripleChart {...defaultProps} />);
      
      // グリッドレイアウトが適用されている
      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toHaveClass('grid-cols-1', 'md:grid-cols-3', 'gap-4');
    });

    it('各チャートカードが正しいスタイルを持つ', () => {
      const { container } = render(<TripleChart {...defaultProps} />);
      
      const chartCards = container.querySelectorAll('.bg-gray-900\\/50');
      expect(chartCards).toHaveLength(3);
      
      chartCards.forEach(card => {
        expect(card).toHaveClass(
          'bg-gray-900/50',
          'rounded-2xl',
          'border',
          'border-gray-800/50',
          'p-4'
        );
      });
    });
  });

  describe('チャートコンポーネント統合テスト', () => {
    it('3つのEnhancedStockChartコンポーネントが正しいプロパティで呼ばれる', () => {
      render(<TripleChart {...defaultProps} />);
      
      // 実績チャート
      expect(screen.getByTestId('enhanced-chart-historical')).toBeInTheDocument();
      expect(screen.getByText('Mock Enhanced Chart for AAPL - historical')).toBeInTheDocument();
      
      // 過去予測チャート
      expect(screen.getByTestId('enhanced-chart-past-prediction')).toBeInTheDocument();
      expect(screen.getByText('Mock Enhanced Chart for AAPL - past-prediction')).toBeInTheDocument();
      
      // 未来予測チャート
      expect(screen.getByTestId('enhanced-chart-future-prediction')).toBeInTheDocument();
      expect(screen.getByText('Mock Enhanced Chart for AAPL - future-prediction')).toBeInTheDocument();
    });

    it('symbolプロパティが各チャートに正しく渡される', () => {
      const testSymbol = 'GOOGL';
      render(<TripleChart symbol={testSymbol} />);
      
      expect(screen.getByText(`Mock Enhanced Chart for ${testSymbol} - historical`)).toBeInTheDocument();
      expect(screen.getByText(`Mock Enhanced Chart for ${testSymbol} - past-prediction`)).toBeInTheDocument();
      expect(screen.getByText(`Mock Enhanced Chart for ${testSymbol} - future-prediction`)).toBeInTheDocument();
    });

    it('各チャートが正しいプロパティを受け取る', () => {
      render(<TripleChart {...defaultProps} />);
      
      // 3つのEnhancedStockChartコンポーネントが存在することを確認
      expect(screen.getByTestId('enhanced-chart-historical')).toBeInTheDocument();
      expect(screen.getByTestId('enhanced-chart-past-prediction')).toBeInTheDocument();
      expect(screen.getByTestId('enhanced-chart-future-prediction')).toBeInTheDocument();
      
      // 各チャートにシンボルとチャートタイプが渡されていることを確認
      expect(screen.getByText('Mock Enhanced Chart for AAPL - historical')).toBeInTheDocument();
      expect(screen.getByText('Mock Enhanced Chart for AAPL - past-prediction')).toBeInTheDocument();
      expect(screen.getByText('Mock Enhanced Chart for AAPL - future-prediction')).toBeInTheDocument();
    });
  });

  describe('アクセシビリティテスト', () => {
    it('各セクションに適切な見出しがある', () => {
      render(<TripleChart {...defaultProps} />);
      
      const headings = screen.getAllByRole('heading', { level: 3 });
      expect(headings).toHaveLength(3);
      
      expect(headings[0]).toHaveTextContent('実績');
      expect(headings[1]).toHaveTextContent('過去予測');
      expect(headings[2]).toHaveTextContent('未来予測');
    });

    it('見出しが正しいスタイリングを持つ', () => {
      render(<TripleChart {...defaultProps} />);
      
      const headings = screen.getAllByRole('heading', { level: 3 });
      headings.forEach(heading => {
        expect(heading).toHaveClass(
          'text-lg',
          'font-bold',
          'text-white',
          'mb-2',
          'text-center'
        );
      });
    });
  });

  describe('レスポンシブデザインテスト', () => {
    it('グリッドレイアウトがレスポンシブクラスを持つ', () => {
      const { container } = render(<TripleChart {...defaultProps} />);
      
      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toHaveClass('grid-cols-1'); // モバイル
      expect(gridContainer).toHaveClass('md:grid-cols-3'); // デスクトップ
    });
  });

  describe('異なるシンボルでのテスト', () => {
    const testCases = [
      'AAPL',
      'GOOGL',
      'MSFT',
      'TSLA',
      '7203', // 日本株
      'BTC-USD' // 暗号通貨
    ];

    testCases.forEach(symbol => {
      it(`${symbol}シンボルで正常に動作する`, () => {
        render(<TripleChart symbol={symbol} />);
        
        expect(screen.getByText(`Mock Enhanced Chart for ${symbol} - historical`)).toBeInTheDocument();
        expect(screen.getByText(`Mock Enhanced Chart for ${symbol} - past-prediction`)).toBeInTheDocument();
        expect(screen.getByText(`Mock Enhanced Chart for ${symbol} - future-prediction`)).toBeInTheDocument();
      });
    });
  });
});