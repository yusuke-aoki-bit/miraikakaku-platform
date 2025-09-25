import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e'
  /* Run tests sequentially to avoid resource conflicts */
  fullyParallel: false
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1
  /* Limited workers to reduce resource contention */
  workers: process.env.CI ? 1 : 2
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html'
  /* Global timeout for all tests */
  timeout: 45000
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3002'
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry'
    /* Screenshots on failure */
    screenshot: 'only-on-failure'
    /* Video recording */
    video: 'retain-on-failure'
    /* Optimized timeouts for better stability */
    navigationTimeout: 20000
    actionTimeout: 10000
  }
  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium'
      use: {
        ...devices['Desktop Chrome']
        // Use practical timeouts for better success rate
        navigationTimeout: 60000
        actionTimeout: 30000
      }
    }
  ]
  /* Local dev server is already running on port 3000 */
});