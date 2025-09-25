// ランキング表示のデバッグスクリプト
const { chromium } = require('playwright'
(async () => {
  const browser = await chromium.launch({ headless: false }
  const page = await browser.newPage(
  // コンソールログをキャプチャ
  page.on('console', msg => {
    if (msg.text().includes('ranking') || msg.text().includes('ランキング') || msg.text().includes('Error')) {
      }: ${msg.text()}`
    }
  }
  // ネットワークリクエストをキャプチャ
  page.on('response', response => {
    if (response.url().includes('rankings')) {
      } ${response.url()}`
    }
  }
  await page.goto('http://localhost:3000'
  await page.waitForLoadState('networkidle'
  await page.waitForTimeout(5000
  // ランキング要素を確認
  const rankingElements = await page.locator('[data-testid="rankings"]').count(
  // ランキングカードを確認
  const rankingCards = await page.locator('.theme-section').count(
  // スクリーンショット撮影
  await page.screenshot({ path: '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakufront/debug-rankings.png' }
  await browser.close(
})();