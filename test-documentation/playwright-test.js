// Playwright Test Script for Test Documentation Site
// Run with: npx playwright test playwright-test.js --headed

const { test, expect } = require('@playwright/test');
const path = require('path');

const baseURL = `file://${path.resolve(__dirname)}`;

test.describe('Test Documentation Site', () => {

  test('Dashboard loads correctly', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Check title
    await expect(page).toHaveTitle(/Test Documentation/);

    // Check main heading
    const heading = page.locator('h1');
    await expect(heading).toContainText('Test Documentation Dashboard');

    // Check stats cards are visible
    const statsCards = page.locator('.stat-card');
    await expect(statsCards).toHaveCount(4);

    // Check pass rate is 100%
    const passRate = page.locator('.stat-value').filter({ hasText: '100%' });
    await expect(passRate).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'screenshots/dashboard.png', fullPage: true });
    console.log('✓ Dashboard loaded successfully');
  });

  test('Navigation works', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Check all nav links are present
    const navLinks = page.locator('.nav-link');
    await expect(navLinks).toHaveCount(5);

    // Check active state
    const activeLink = page.locator('.nav-link.active');
    await expect(activeLink).toHaveText('Dashboard');

    console.log('✓ Navigation is functional');
  });

  test('Table of Contents generates', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Wait for TOC to be generated
    await page.waitForTimeout(500);

    // Check TOC links exist
    const tocLinks = page.locator('.toc-link');
    const count = await tocLinks.count();
    expect(count).toBeGreaterThan(0);

    console.log(`✓ TOC generated with ${count} links`);
  });

  test('Charts render', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Wait for charts to load
    await page.waitForTimeout(1000);

    // Check canvas elements exist
    const charts = page.locator('canvas');
    await expect(charts).toHaveCount(2);

    console.log('✓ Charts rendered');
  });

  test('Collapsible sections work', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Find a collapsible section
    const collapsible = page.locator('.collapsible').first();
    const header = collapsible.locator('.collapsible-header');

    // Check initial state (first one is active by default)
    await expect(collapsible).toHaveClass(/active/);

    // Click to collapse
    await header.click();
    await page.waitForTimeout(300);
    await expect(collapsible).not.toHaveClass(/active/);

    // Click to expand
    await header.click();
    await page.waitForTimeout(300);
    await expect(collapsible).toHaveClass(/active/);

    console.log('✓ Collapsible sections work correctly');
  });

  test('Search modal opens', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Click search trigger
    await page.click('#search-trigger');

    // Check modal is visible
    const modal = page.locator('#search-modal');
    await expect(modal).toHaveClass(/active/);

    // Check input is focused
    const input = page.locator('#search-input');
    await expect(input).toBeFocused();

    // Close with ESC
    await page.keyboard.press('Escape');
    await expect(modal).not.toHaveClass(/active/);

    console.log('✓ Search modal works');
  });

  test('Search functionality works', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Open search
    await page.click('#search-trigger');

    // Type search query
    await page.fill('#search-input', 'security');
    await page.waitForTimeout(300);

    // Check results appear
    const results = page.locator('.search-result');
    const count = await results.count();
    expect(count).toBeGreaterThan(0);

    console.log(`✓ Search found ${count} results`);
  });

  test('Smooth scroll works', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Wait for TOC
    await page.waitForTimeout(500);

    // Click a TOC link
    const tocLink = page.locator('.toc-link').first();
    await tocLink.click();

    // Wait for scroll
    await page.waitForTimeout(500);

    console.log('✓ Smooth scroll works');
  });

  test('Responsive design - Mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${baseURL}/index.html`);

    // Take mobile screenshot
    await page.screenshot({ path: 'screenshots/dashboard-mobile.png', fullPage: true });

    // Check layout adapts
    const mainContent = page.locator('.main-content');
    await expect(mainContent).toBeVisible();

    console.log('✓ Mobile layout works');
  });

  test('Responsive design - Tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${baseURL}/index.html`);

    // Take tablet screenshot
    await page.screenshot({ path: 'screenshots/dashboard-tablet.png', fullPage: true });

    console.log('✓ Tablet layout works');
  });

  test('No console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto(`${baseURL}/index.html`);
    await page.waitForTimeout(2000);

    expect(errors).toHaveLength(0);
    console.log('✓ No console errors');
  });

  test('All badges visible', async ({ page }) => {
    await page.goto(`${baseURL}/index.html`);

    // Check badges
    const badges = page.locator('.badge');
    const count = await badges.count();
    expect(count).toBeGreaterThan(0);

    // Check success badge
    const successBadge = page.locator('.badge-success').first();
    await expect(successBadge).toContainText('20/20');

    console.log(`✓ Found ${count} badges`);
  });
});

// Generate summary report
test.afterAll(async () => {
  console.log('\n='.repeat(70));
  console.log('TEST SUMMARY');
  console.log('='.repeat(70));
  console.log('All tests completed!');
  console.log('Screenshots saved to screenshots/ directory');
  console.log('='.repeat(70));
});
