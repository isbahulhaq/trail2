import asyncio
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()

# 🔴 REQUIRED FUNCTION
async def start(user, wait_time, meetingcode, passcode):
    print(f"[JOINING] {user}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            slow_mo=150,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream"
            ]
        )

        context = await browser.new_context()
        await context.grant_permissions(["microphone"])
        page = await context.new_page()

        try:
            # Open join page
            await page.goto(
                f"https://app.zoom.us/wc/join/{meetingcode}",
                wait_until="domcontentloaded",
                timeout=45000
            )

            # Wait until network is stable
            await page.wait_for_load_state("networkidle")

            # Cookies / agreement
            for btn in ["#onetrust-accept-btn-handler", "#wc_agree1"]:
                try:
                    await page.click(btn, timeout=3000)
                except:
                    pass

            # Wait for name input (LONGER timeout)
            await page.wait_for_selector('input[type="text"]', timeout=60000)

            await page.fill('input[type="text"]', user)
            await page.fill('input[type="password"]', passcode)

            await asyncio.sleep(2)
            await page.click("button.preview-join-button", timeout=20000)

            print(f"[JOINED] {user}")

            # Try to join audio
            try:
                await page.wait_for_selector(
                    'button[class*="join-audio"]',
                    timeout=20000
                )
                await page.click('button[class*="join-audio"]')
                print(f"[MIC OK] {user}")
            except:
                print(f"[MIC SKIPPED] {user}")

            print(f"[ACTIVE] {user}")
            await asyncio.sleep(wait_time)

        except Exception as e:
            print(f"[FAILED] {user} → {e}")

        await browser.close()
        print(f"[END] {user}")
