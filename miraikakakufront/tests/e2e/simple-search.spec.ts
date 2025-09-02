import { test, expect } from '@playwright/test';

test.describe('Simple Search Test', () => {
  test('should click search button and show console logs', async ({ page }) => {
    // Listen for console messages
    const consoleMessages: string[] = [];
    page.on('console', msg => {
      consoleMessages.push(`${msg.type()}: ${msg.text()}`);
    });
    
    // Listen for alerts
    let alertMessage = '';
    page.on('dialog', async dialog => {
      alertMessage = dialog.message();
      await dialog.accept();
    });
    
    await page.goto('/');
    
    // Fill search input
    const searchInput = page.locator('input[placeholder*="検索"]');
    await searchInput.fill('AAPL');
    
    // Click search button
    const searchButton = page.locator('button[type="submit"]');
    await searchButton.click();
    
    // Wait for any navigation or console logs
    await page.waitForTimeout(2000);
    
    // Print console messages for debugging
    console.log('Console messages:', consoleMessages);
    console.log('Alert message:', alertMessage);
    
    // Check if alert was shown or navigation occurred
    const currentUrl = page.url();
    expect(alertMessage.includes('Navigating to: /details/AAPL') || currentUrl.includes('/details/AAPL')).toBeTruthy();
    
    // Or check if navigation occurred
    if (!alertMessage) {
      await expect(page).toHaveURL(/\/details\/AAPL/);
    }
  });
  
  test('should test form submission directly', async ({ page }) => {
    const consoleMessages: string[] = [];
    page.on('console', msg => {
      consoleMessages.push(`${msg.type()}: ${msg.text()}`);
    });
    
    await page.goto('/');
    
    const searchInput = page.locator('input[placeholder*="検索"]');
    await searchInput.fill('TSLA');
    
    // Press Enter instead of clicking button
    await searchInput.press('Enter');
    
    await page.waitForTimeout(1000);
    
    console.log('Form submission console messages:', consoleMessages);
    
    // Should either show alert or navigate
    const currentUrl = page.url();
    console.log('Current URL after Enter:', currentUrl);
    
    expect(currentUrl.includes('/details/TSLA') || consoleMessages.some(msg => msg.includes('handleSelectStock'))).toBeTruthy();
  });
});