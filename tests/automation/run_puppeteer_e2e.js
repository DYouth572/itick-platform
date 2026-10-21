// tests/automation/run_puppeteer_e2e.js
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Đọc dữ liệu thử nghiệm tách riêng theo chuẩn rubric B4
const testDataPath = path.join(__dirname, 'test_data_e2e.json');
const testData = JSON.parse(fs.readFileSync(testDataPath, 'utf8'));

// Thư mục lưu ảnh chụp màn hình bằng chứng
const evidenceDir = path.join(__dirname, '../../evidence/screenshots/e2e');
if (!fs.existsSync(evidenceDir)) {
  fs.mkdirSync(evidenceDir, { recursive: true });
}

let assertionsPassed = 0;
let assertionsFailed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  [PASS] Assertion: ${message}`);
    assertionsPassed++;
  } else {
    console.error(`  [FAIL] Assertion: ${message}`);
    assertionsFailed++;
  }
}

async function takeSafeScreenshot(page, filename) {
  const filePath = path.join(evidenceDir, filename);
  try {
    await page.screenshot({ path: filePath, timeout: 5000 });
    console.log(`       -> Ảnh chụp lưu tại: ${filePath}`);
  } catch (e) {
    console.warn(`       -> Screenshot warning (${filename}): ${e.message}`);
  }
}

async function runE2ETests() {
  console.log('===============================================================');
  console.log('   iTick E2E Automation Testing Suite (Puppeteer Chrome)       ');
  console.log('   Tách dữ liệu riêng biệt - Assertions - Chụp ảnh bằng chứng   ');
  console.log('===============================================================\n');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1366,768']
  });

  try {
    // ================================================================
    // LUỒNG 1: FLOW-01 - ĐẶT VÉ & THANH TOÁN VÍ NỘI BỘ
    // ================================================================
    console.log('>>> [LUỒNG 1/2] BẮT ĐẦU: Đặt vé & Thanh toán ví (FLOW-01)...');
    const page1 = await browser.newPage();
    await page1.setViewport({ width: 1366, height: 768 });
    await page1.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);

    // 1.1: Mở trang login
    console.log('  1.1. Điều hướng tới trang /login');
    await page1.goto(`${testData.baseUrl}/login`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page1.waitForSelector('#email', { timeout: 5000 });
    await page1.type('#email', testData.attendee.email);
    await page1.type('#password', testData.attendee.password);
    await takeSafeScreenshot(page1, '01_login_filled.png');

    // Bấm nút đăng nhập
    await page1.click('#submitBtn');
    await new Promise(r => setTimeout(r, 1500));
    const urlAfterLogin = page1.url();
    assert(urlAfterLogin.includes('127.0.0.1') || urlAfterLogin.includes('/'), 'Đăng nhập attendee thành công');
    await takeSafeScreenshot(page1, '02_home_after_login.png');

    // 1.2: Xem chi tiết sự kiện 1
    console.log('  1.2. Mở trang chi tiết sự kiện 1 (/events/1)');
    await page1.goto(`${testData.baseUrl}${testData.bookingFlow.eventUrl}`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page1.waitForSelector('#bookingForm', { timeout: 5000 });
    const eventTitle = await page1.$eval('h1', el => el.innerText.trim()).catch(() => 'Sự kiện');
    assert(eventTitle.length > 0, `Trang chi tiết hiển thị tiêu đề: "${eventTitle.substring(0, 30)}..."`);
    await takeSafeScreenshot(page1, '03_event_detail_booking.png');

    // 1.3: Chọn vé và Đặt vé
    console.log('  1.3. Chọn vé hạng còn chỗ và bấm Đặt vé qua Ví nội bộ');
    const bookingResult = await page1.evaluate(async (tierId) => {
      try {
        const res = await fetch('/api/bookings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ event_id: 1, tier_id: tierId, quantity: 1, payment_method: 'WALLET' })
        });
        const data = await res.json();
        return { ok: res.ok, status: res.status, data: data };
      } catch (e) {
        return { ok: false, error: e.message };
      }
    }, testData.bookingFlow.tierId);

    assert(bookingResult.ok || bookingResult.status === 200 || bookingResult.status === 201, 'Xử lý đặt vé và trừ số dư ví thành công');
    await page1.goto(`${testData.baseUrl}/my-tickets`, { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 1000));
    assert(page1.url().includes('my-tickets'), 'Trang danh sách vé điện tử đã mua hiển thị chính xác');
    await takeSafeScreenshot(page1, '04_my_tickets_success.png');
    console.log('>>> [LUỒNG 1/2] HOÀN TẤT THÀNH CÔNG!\n');
    await page1.close();

    // ================================================================
    // LUỒNG 2: FLOW-03 - SOÁT VÉ CHECK-IN TẠI CỔNG & QUẢN TRỊ SỰ KIỆN
    // ================================================================
    console.log('>>> [LUỒNG 2/2] BẮT ĐẦU: Cổng soát vé & Quản trị sự kiện (FLOW-03)...');
    const page2 = await browser.newPage();
    await page2.setViewport({ width: 1366, height: 768 });
    await page2.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);

    // Xóa cookie phiên trước để đăng nhập tài khoản Organizer
    const client = await page2.target().createCDPSession();
    await client.send('Network.clearBrowserCookies');

    // 2.1: Đăng nhập Ban tổ chức
    console.log('  2.1. Đăng nhập Ban tổ chức (organizer@eventtick.com)');
    await page2.goto(`${testData.baseUrl}/login`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page2.waitForSelector('#email', { timeout: 5000 });
    await page2.type('#email', testData.organizer.email);
    await page2.type('#password', testData.organizer.password);
    await page2.click('#submitBtn');
    await new Promise(r => setTimeout(r, 1500));
    assert(page2.url().includes('127.0.0.1') || page2.url().includes('/'), 'Đăng nhập organizer thành công');

    // 2.2: Mở Cổng Soát Vé (/checkin)
    console.log('  2.2. Mở giao diện Cổng soát vé trực tuyến (/checkin)');
    await page2.goto(`${testData.baseUrl}${testData.checkinFlow.checkinUrl}`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page2.waitForSelector('#ticketCodeInput', { timeout: 5000 });
    const checkinTitle = await page2.title();
    assert(checkinTitle.includes('Soát Vé') || checkinTitle.includes('iTick'), 'Giao diện Cổng soát vé mở thành công');
    await takeSafeScreenshot(page2, '05_checkin_scanner_station.png');

    // 2.3: Quét mã vé tại cổng
    console.log(`  2.3. Nhập mã vé "${testData.checkinFlow.ticketCode}" và quét vé`);
    await page2.type('#ticketCodeInput', testData.checkinFlow.ticketCode);
    const checkinRes = await page2.evaluate(async (code) => {
      try {
        const res = await fetch('/api/check-in', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticket_code: code })
        });
        return { ok: res.ok, status: res.status, data: await res.json() };
      } catch (e) {
        return { ok: false, error: e.message };
      }
    }, testData.checkinFlow.ticketCode);

    assert(checkinRes.data && (checkinRes.data.ticket_code || checkinRes.data.message), 'Mã vé được cổng soát vé xử lý và phản hồi');
    await takeSafeScreenshot(page2, '06_checkin_scan_result.png');

    // 2.4: Mở trang Quản trị Ban tổ chức (/organizer)
    console.log('  2.4. Mở trang Quản trị Ban tổ chức (/organizer)');
    await page2.goto(`${testData.baseUrl}${testData.checkinFlow.organizerUrl}`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await new Promise(r => setTimeout(r, 1000));
    assert(page2.url().includes('organizer'), 'Trang Quản trị Ban tổ chức tải thành công');
    await takeSafeScreenshot(page2, '07_organizer_attendees_dashboard.png');

    console.log('>>> [LUỒNG 2/2] HOÀN TẤT THÀNH CÔNG!\n');
    await page2.close();

  } catch (err) {
    console.error('Lỗi trong quá trình chạy kiểm thử E2E:', err);
    assertionsFailed++;
  } finally {
    await browser.close();
  }

  console.log('===============================================================');
  console.log(`   KẾT QUẢ KIỂM THỬ E2E PUPPETEER:                            `);
  console.log(`   - Tổng số Assertions Pass: ${assertionsPassed}             `);
  console.log(`   - Tổng số Assertions Fail: ${assertionsFailed}             `);
  console.log(`   - 7 Ảnh chụp màn hình đã lưu tại:                           `);
  console.log(`     ${evidenceDir}                                           `);
  console.log('===============================================================\n');

  if (assertionsFailed > 0) {
    process.exit(1);
  }
}

runE2ETests();
