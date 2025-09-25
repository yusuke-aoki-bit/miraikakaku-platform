import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Global teardown for E2E tests
 * Handles cleanup and test result processing
 */
async function globalTeardown(config: FullConfig) {
  try {
    // Generate test summary report
    const testResultsPath = path.join(process.cwd(), 'test-results.json'
    if (fs.existsSync(testResultsPath)) {
      const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8')
      const summary = {
        timestamp: new Date().toISOString()
        totalTests: testResults.stats?.total || 0
        passed: testResults.stats?.passed || 0
        failed: testResults.stats?.failed || 0
        skipped: testResults.stats?.skipped || 0
        duration: testResults.stats?.duration || 0
        successRate: testResults.stats?.total > 0
          ? ((testResults.stats.passed / testResults.stats.total) * 100).toFixed(1)
          : '0.0'
      };

      // Save enhanced summary
      const summaryPath = path.join(process.cwd(), 'test-summary.json'
      fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2)
      }

    // Cleanup test artifacts if needed
    // Clean up temporary files, screenshots, videos from failed tests
    // (Keep them for now for debugging, but in CI you might want to clean up)

    // Optional: Archive test results for CI
    if (process.env.CI) {
      // Here you could compress and upload test results, screenshots, etc.
    }

    } catch (error) {
    // Don't throw error in teardown to avoid masking test failures
  }
}

export default globalTeardown;