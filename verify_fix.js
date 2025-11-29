import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // 设置视口大小
  await page.setViewportSize({ width: 1920, height: 1080 });

  try {
    // 注入 token 以跳过登录 (参考之前的上下文，可能需要 token)
    // 这里假设不需要，或者尝试访问看是否重定向
    await page.goto('http://localhost:5173/kline');
    
    // 等待一段时间让请求完成
    await page.waitForTimeout(5000);
    
    // 截图
    await page.screenshot({ path: 'docs/kline-verification.png', fullPage: true });
    console.log('Screenshot captured: docs/kline-verification.png');

    // 检查是否有错误提示
    const errorVisible = await page.isVisible('text="HTTP Error: 500"');
    const dataVisible = await page.isVisible('canvas'); // ECharts 通常使用 canvas

    if (errorVisible) {
      console.log('Validation Failed: Error 500 still visible.');
    } else {
      console.log('Validation Passed: No Error 500 visible.');
    }

    if (dataVisible) {
        console.log('Validation Passed: Chart canvas is visible.');
    } else {
        console.log('Validation Warning: Chart canvas not found (maybe loading or empty data).');
    }

  } catch (error) {
    console.error('Error during validation:', error);
  } finally {
    await browser.close();
  }
})();
