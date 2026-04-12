const { chromium } = require('playwright');

async function fetchPage(url, maxChars = 5000) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Get page content
    const content = await page.content();
    const text = await page.evaluate(() => document.body.innerText);
    
    // Truncate
    const result = text.substring(0, maxChars);
    
    console.log(JSON.stringify({
      url: page.url(),
      title: await page.title(),
      content: result,
      success: true
    }, null, 2));
  } catch (err) {
    console.log(JSON.stringify({
      success: false,
      error: err.message
    }));
  } finally {
    await browser.close();
  }
}

fetchPage(process.argv[2] || 'https://example.com');
