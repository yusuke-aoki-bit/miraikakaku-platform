import { render, screen } from '@testing-library/react'
import { StockChart } from '../charts/StockChart'

describe('StockChart', () => {
  const mockData = [
    { date: '2024-01-01', price: 100, volume: 1000000 },
    { date: '2024-01-02', price: 102, volume: 1200000 },
    { date: '2024-01-03', price: 98, volume: 800000 },
  ]

  it('チャートが正常にレンダリングされる', () => {
    render(<StockChart data={mockData} symbol="AAPL" />)
    
    // チャートコンテナが存在することを確認
    const chartContainer = screen.getByTestId('stock-chart')
    expect(chartContainer).toBeInTheDocument()
  })

  it('データが空の場合エラーメッセージが表示される', () => {
    render(<StockChart data={[]} symbol="AAPL" />)
    
    // エラーメッセージが表示されることを確認
    expect(screen.getByText(/データがありません/)).toBeInTheDocument()
  })

  it('銘柄コードが正しく表示される', () => {
    render(<StockChart data={mockData} symbol="AAPL" />)
    
    // 銘柄コードが表示されることを確認
    expect(screen.getByText(/AAPL/)).toBeInTheDocument()
  })

  it('ローディング状態が正しく表示される', () => {
    render(<StockChart data={mockData} symbol="AAPL" loading={true} />)
    
    // ローディングインジケーターが表示されることを確認
    expect(screen.getByText(/読み込み中/)).toBeInTheDocument()
  })
})