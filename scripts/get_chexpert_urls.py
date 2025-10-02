#!/usr/bin/env python3
"""
Automated script to login to Stanford CheXpert and retrieve download URLs.
Uses Playwright to automate browser interaction.
"""

import asyncio
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("\nInstall with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


async def get_chexpert_urls(email: str, password: str, headless: bool = False):
    """
    Automate login to Stanford CheXpert and retrieve download URLs.

    Args:
        email: Stanford/CheXpert account email
        password: Account password
        headless: Run browser in headless mode (default: False for visibility)

    Returns:
        Dictionary of download URLs
    """

    print("🚀 Starting CheXpert URL retrieval...")
    print(f"   Email: {email}")
    print(f"   Headless mode: {headless}")
    print()

    urls = {}

    async with async_playwright() as p:
        # Launch browser
        print("🌐 Launching Chrome...")
        browser = await p.chromium.launch(
            headless=headless,
            channel='chrome',  # Use installed Chrome
            args=['--start-maximized']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        try:
            # Navigate to CheXpert page
            print("📄 Navigating to CheXpert competition page...")
            await page.goto('https://stanfordmlgroup.github.io/competitions/chexpert/',
                          wait_until='networkidle')

            # Wait a bit for page to fully load
            await page.wait_for_timeout(2000)

            # Take screenshot of initial page
            await page.screenshot(path='logs/chexpert_01_initial.png')
            print("   📸 Screenshot saved: logs/chexpert_01_initial.png")

            # Look for download button/link
            print("\n🔍 Looking for download section...")

            # Try to find download button
            download_selectors = [
                'text=Download',
                'text=download',
                'a:has-text("Download")',
                'button:has-text("Download")',
                '[href*="download"]',
                '[href*="aimi"]',
            ]

            download_element = None
            for selector in download_selectors:
                try:
                    download_element = await page.wait_for_selector(selector, timeout=5000)
                    if download_element:
                        print(f"   ✓ Found download element: {selector}")
                        break
                except:
                    continue

            if not download_element:
                print("   ⚠️  No obvious download button found")
                print("   📸 Taking screenshot for manual inspection...")
                await page.screenshot(path='logs/chexpert_02_no_download.png')

                # Print page content for debugging
                content = await page.content()
                with open('logs/chexpert_page_content.html', 'w') as f:
                    f.write(content)
                print("   📄 Page HTML saved to logs/chexpert_page_content.html")

                # Look for any links
                links = await page.query_selector_all('a')
                print(f"\n   Found {len(links)} links on page:")
                for i, link in enumerate(links[:20]):  # First 20 links
                    try:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()
                        if text and href:
                            print(f"      {i+1}. {text.strip()[:50]} -> {href}")
                    except:
                        pass

            # Click download if found
            if download_element:
                await download_element.click()
                print("   🖱️  Clicked download button")
                await page.wait_for_timeout(2000)
                await page.screenshot(path='logs/chexpert_03_after_click.png')

            # Check if we're redirected to AIMI or login page
            current_url = page.url
            print(f"\n📍 Current URL: {current_url}")

            # If redirected to AIMI
            if 'aimi.stanford.edu' in current_url or 'stanfordaimi' in current_url:
                print("\n🔐 Detected AIMI login page...")
                await page.screenshot(path='logs/chexpert_04_aimi_login.png')

                # Wait for login form
                await page.wait_for_timeout(2000)

                # Look for email input
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[placeholder*="email" i]',
                    'input[id*="email" i]',
                ]

                email_input = None
                for selector in email_selectors:
                    try:
                        email_input = await page.wait_for_selector(selector, timeout=3000)
                        if email_input:
                            print(f"   ✓ Found email input: {selector}")
                            break
                    except:
                        continue

                if email_input:
                    # Fill in email
                    await email_input.fill(email)
                    print(f"   ✓ Entered email: {email}")
                    await page.wait_for_timeout(500)

                    # Look for password input
                    password_selectors = [
                        'input[type="password"]',
                        'input[name="password"]',
                        'input[placeholder*="password" i]',
                    ]

                    password_input = None
                    for selector in password_selectors:
                        try:
                            password_input = await page.wait_for_selector(selector, timeout=3000)
                            if password_input:
                                print(f"   ✓ Found password input: {selector}")
                                break
                        except:
                            continue

                    if password_input:
                        # Fill in password
                        await password_input.fill(password)
                        print("   ✓ Entered password")
                        await page.wait_for_timeout(500)

                        # Look for submit button
                        submit_selectors = [
                            'button[type="submit"]',
                            'button:has-text("Sign in")',
                            'button:has-text("Login")',
                            'button:has-text("Log in")',
                            'input[type="submit"]',
                        ]

                        submit_button = None
                        for selector in submit_selectors:
                            try:
                                submit_button = await page.wait_for_selector(selector, timeout=3000)
                                if submit_button:
                                    print(f"   ✓ Found submit button: {selector}")
                                    break
                            except:
                                continue

                        if submit_button:
                            await page.screenshot(path='logs/chexpert_05_before_submit.png')
                            await submit_button.click()
                            print("   🖱️  Clicked login button")

                            # Wait for navigation after login
                            await page.wait_for_timeout(3000)
                            await page.screenshot(path='logs/chexpert_06_after_login.png')

                            print(f"\n📍 After login URL: {page.url}")
                        else:
                            print("   ❌ Could not find submit button")
                    else:
                        print("   ❌ Could not find password input")
                else:
                    print("   ❌ Could not find email input")

            # Look for download links on current page
            print("\n🔍 Searching for Azure/download URLs...")

            # Get all text content
            content = await page.content()

            # Search for Azure blob URLs
            azure_pattern = r'https://[^"\'>\s]+\.blob\.core\.windows\.net[^"\'>\s]+'
            azure_urls = re.findall(azure_pattern, content)

            if azure_urls:
                print(f"\n✅ Found {len(azure_urls)} Azure URLs!")
                for i, url in enumerate(azure_urls[:5]):  # Show first 5
                    print(f"   {i+1}. {url[:100]}...")

                # Try to categorize by batch
                for url in azure_urls:
                    if 'batch' in url.lower():
                        # Extract batch number
                        batch_match = re.search(r'batch[%20\s]+(\d+)', url, re.IGNORECASE)
                        if batch_match:
                            batch_num = batch_match.group(1)
                            urls[f"batch{batch_num}"] = url
                    elif 'validate' in url.lower() or 'csv' in url.lower():
                        urls["batch1"] = url
            else:
                print("   ⚠️  No Azure URLs found in page content")

            # Search for any download links
            download_links = await page.query_selector_all('a[href*="blob.core.windows.net"], a[href*="download"]')
            print(f"\n🔗 Found {len(download_links)} download-related links")

            for i, link in enumerate(download_links[:10]):
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    print(f"   {i+1}. {text[:50]} -> {href[:80]}...")
                except:
                    pass

            # Take final screenshot
            await page.screenshot(path='logs/chexpert_07_final.png', full_page=True)
            print("\n📸 Final screenshot saved: logs/chexpert_07_final.png")

            # Save page HTML
            final_content = await page.content()
            with open('logs/chexpert_final_page.html', 'w') as f:
                f.write(final_content)
            print("📄 Final page HTML saved: logs/chexpert_final_page.html")

        except Exception as e:
            print(f"\n❌ Error during automation: {e}")
            import traceback
            traceback.print_exc()

            # Take error screenshot
            try:
                await page.screenshot(path='logs/chexpert_error.png')
                print("📸 Error screenshot saved: logs/chexpert_error.png")
            except:
                pass

        finally:
            # Keep browser open for manual inspection if not headless
            if not headless:
                print("\n⏸️  Browser kept open for manual inspection...")
                print("   Press Enter to close browser and continue...")
                input()

            await browser.close()

    return urls


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Get CheXpert download URLs via browser automation')
    parser.add_argument('--email', help='Stanford/CheXpert account email')
    parser.add_argument('--password', help='Account password (or use CHEXPERT_PASSWORD env var)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--save', help='Save URLs to file (JSON format)')

    args = parser.parse_args()

    # Get credentials
    email = args.email or os.getenv('CHEXPERT_EMAIL')
    password = args.password or os.getenv('CHEXPERT_PASSWORD')

    if not email:
        email = input("Enter your Stanford/CheXpert email: ")

    if not password:
        import getpass
        password = getpass.getpass("Enter your password: ")

    if not email or not password:
        print("❌ Email and password are required!")
        sys.exit(1)

    # Run automation
    urls = await get_chexpert_urls(email, password, args.headless)

    # Display results
    print("\n" + "=" * 80)
    print("Results Summary")
    print("=" * 80)

    if urls:
        print(f"\n✅ Found {len(urls)} download URLs:")
        for batch, url in urls.items():
            print(f"\n{batch}:")
            print(f"  {url[:150]}...")

        # Save to file if requested
        if args.save:
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'email': email,
                'urls': urls
            }

            with open(args.save, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"\n💾 URLs saved to: {args.save}")
            print("\nNext step: Update scripts/download_chexpert_training.py with these URLs")
    else:
        print("\n⚠️  No URLs found automatically")
        print("\nPlease check the screenshots in logs/ directory:")
        print("  - logs/chexpert_*.png")
        print("  - logs/chexpert_final_page.html")
        print("\nYou may need to:")
        print("  1. Manually navigate to the download page")
        print("  2. Complete any required forms or agreements")
        print("  3. Copy the Azure URLs manually")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
