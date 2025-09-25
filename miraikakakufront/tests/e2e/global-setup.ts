import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for E2E tests
 * Handles test environment preparation
 */
async function globalSetup(config: FullConfig) {
  // Launch browser for setup tasks
  const browser = await chromium.launch(
  const page = await browser.newPage(
  try {
    // Check if the application is running
    const baseURL = config.projects[0].use.baseURL || 'http://localhost:3000';

    try {
      await page.goto(baseURL, { timeout: 30000 }
      await page.waitForSelector('body', { timeout: 10000 }
      } catch (error) {
      }

    // Check API availability
    const apiEndpoints = [
      'http://localhost:8080/health'
      'http://localhost:8080/api/finance/stocks/list'
    ];

    for (const endpoint of apiEndpoints) {
      try {
        const response = await page.request.get(endpoint
        ? '✅ Available' : '❌ Unavailable'}`
      } catch (error) {
        }
    }

    // Setup test data or configurations if needed
    // You can add any pre-test setup here
    // - Database seeding
    // - Cache warming
    // - Mock data preparation

    } catch (error) {
    throw error;
  } finally {
    await browser.close(
  }
}

export default globalSetup;