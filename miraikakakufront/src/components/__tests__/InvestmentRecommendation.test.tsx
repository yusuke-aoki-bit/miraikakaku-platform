import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import InvestmentRecommendation from '../investment/InvestmentRecommendation';
import { INVESTMENT_CONFIG } from '@/config/constants';

// ThumbnailChartコンポーネントのモック
jest.mock('../charts/ThumbnailChart', () => {
  return function MockThumbnailChart() {
    return <div data-testid="thumbnail-chart">Mock Thumbnail Chart</div>;
  };
});

describe('InvestmentRecommendation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Math.randomのモック
    jest.spyOn(Math, 'random').mockReturnValue(0.5);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const defaultProps = {
    symbol: 'AAPL',
    currentPrice: 150.0,
    showDetailed: false,
  };

  describe('基本表示テスト', () => {
    it('コンポーネントが正常にレンダリングされる', () => {
      render(<InvestmentRecommendation {...defaultProps} />);
      
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    it('シンボルが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} />);
      
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    it('評価スコアが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} />);
      
      // パーセンテージ表示があることを確認（複数ある場合は最初の要素を取得）
      expect(screen.getAllByText(/%/)).toHaveLength(2);
    });

    it('ThumbnailChartが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} />);
      
      expect(screen.getByTestId('thumbnail-chart')).toBeInTheDocument();
    });
  });

  describe('投資推奨ロジックテスト', () => {
    it('推奨レベルが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);

      // 推奨アイコンが表示される
      const recommendationIcon = document.querySelector('svg');
      expect(recommendationIcon).toBeInTheDocument();
    });

    it('期待リターンが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);

      expect(screen.getByText(/期待:/)).toBeInTheDocument();
    });

    it('モデル名が表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);

      // LSTM または VertexAI のどちらかが表示される
      const isLSTM = screen.queryByText('LSTM');
      const isVertexAI = screen.queryByText('VertexAI');
      expect(isLSTM || isVertexAI).toBeTruthy();
    });
  });

  describe('推奨レベルテスト', () => {
    it('推奨レベルアイコンが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      // SVGアイコンが表示されることを確認
      const svgIcon = document.querySelector('svg.lucide-trending-up, svg.lucide-trending-down, svg.lucide-target');
      expect(svgIcon).toBeInTheDocument();
    });

    it('評価スコアが数値で表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      // パーセンテージが表示される
      const percentageElements = screen.getAllByText(/%/);
      expect(percentageElements.length).toBeGreaterThan(0);
    });

    it('期待リターンが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      expect(screen.getByText(/期待:/)).toBeInTheDocument();
    });
  });

  describe('データ表示テスト', () => {
    it('シンボルが正しく表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    it('ThumbnailChartコンポーネントが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      expect(screen.getByTestId('thumbnail-chart')).toBeInTheDocument();
    });
  });

  describe('詳細表示モードテスト', () => {
    it('詳細モードが無効の場合、シンプルな表示になる', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={false} />);
      
      expect(screen.queryByText('AI投資スコア')).not.toBeInTheDocument();
      expect(screen.queryByText('目標株価')).not.toBeInTheDocument();
    });

    it('詳細モードが有効の場合、詳細情報が表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={true} />);

      expect(screen.getByText('AI投資スコア')).toBeInTheDocument();
      expect(screen.getByText('目標株価')).toBeInTheDocument();
      expect(screen.getByText('期待リターン')).toBeInTheDocument();
      expect(screen.getByText('ストップロス')).toBeInTheDocument();
    });

    it('詳細モードでLSTMとVertexAIが表示される', () => {
      render(<InvestmentRecommendation {...defaultProps} showDetailed={true} />);

      expect(screen.getByText('LSTM')).toBeInTheDocument();
      expect(screen.getByText('VertexAI')).toBeInTheDocument();
    });
  });

  describe('設定値テスト', () => {
    it('投資設定の定数が正しく使用される', () => {
      // INVESTMENT_CONFIGの値が正しく参照されているか確認
      expect(INVESTMENT_CONFIG.LSTM_ACCURACY.BASE).toBe(75);
      expect(INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.STRONG_BUY).toBe(85);
      expect(INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.BUY).toBe(75);
      expect(INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.HOLD).toBe(60);
    });
  });
});