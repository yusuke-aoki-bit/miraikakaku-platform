import { test } from '@playwright/test';

test('take screenshots', async ({ page }) => {
  // Homepage screenshot
  await page.goto('http://localhost:3000'
  await page.waitForTimeout(3000
  await page.screenshot({ path: 'homepage-final.png', fullPage: true }
  // Chart page screenshot
  await page.goto('http://localhost:3000/details/AAPL'
  await page.waitForTimeout(5000
  await page.screenshot({ path: 'chart-final.png', fullPage: true }
});