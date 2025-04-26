import os
import asyncio
import json
from playwright.async_api import async_playwright, Error, Page, TimeoutError

SESSION_FILE = "session.json"

async def get_browser_context(playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto("https://hiring.idenhq.com/")
        await page.wait_for_selector('input#email', timeout=30000)
        await page.fill('input#email', os.getenv("IDEN_EMAIL", "harshgunjal2005@gmail.com"))
        await page.fill('input#password', os.getenv("IDEN_PASSWORD", "lnGXrtTT"))
        await page.click('button:has-text("Sign in")')
        await page.wait_for_load_state("networkidle")

        print(f"✅ Logged in at: {page.url}")
        await page.wait_for_selector('button:has-text("Launch Challenge")', timeout=60000)
        await page.click('button:has-text("Launch Challenge")')
        await page.wait_for_load_state("networkidle")

        print(f"🚀 Launched Challenge at: {page.url}")
        await context.storage_state(path=SESSION_FILE)
        return context, page

    except Exception as e:
        print(f"❌ Error during login or challenge launch: {e}")
        await context.close()
        raise

async def navigate_to_full_catalog(page: Page):
    try:
        print("⏭ Navigating through Dashboard > Inventory > Products > Full Catalog...")

        await page.wait_for_selector("button:has-text('Dashboard')", timeout=80000)
        await page.click("button:has-text('Dashboard')")
        await page.wait_for_load_state("networkidle")

        await page.wait_for_selector("text=Inventory", timeout=30000)
        await page.click("text=Inventory")
        await page.wait_for_load_state("networkidle")

        await page.wait_for_selector("text=Products", timeout=30000)
        await page.click("text=Products")
        await page.wait_for_load_state("networkidle")

        await page.wait_for_selector("text=Full Catalog", timeout=30000)
        await page.click("text=Full Catalog")
        await page.wait_for_load_state("networkidle")

        print("✅ Reached Full Catalog")
    except TimeoutError as e:
        print(f"❌ Timeout during navigation: {e}")
        raise
    except Error as e:
        print(f"❌ Playwright error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unknown error during navigation: {e}")
        raise

async def extract_product_data(card):
    try:
        print("Starting to extract product data...")
        
        # Extract title
        title_elem = card.locator("h3.font-medium").first
        title = await title_elem.inner_text() if await title_elem.count() > 0 else "N/A"
        print(f"Extracted title: {title}")
        
        # Extract ID and category
        id_and_category = card.locator("div.flex.items-center.text-sm.text-muted-foreground").first
        spans = id_and_category.locator("span")
        id_text = (await spans.nth(0).inner_text()).replace("ID:", "").strip() if await spans.count() > 0 else "N/A"
        category_text = await spans.nth(2).inner_text() if await spans.count() > 2 else "N/A"
        print(f"Extracted ID: {id_text}, Category: {category_text}")
        
        # Find all data containers
        data_containers = card.locator("div.flex.flex-wrap.gap-4.text-sm > div.flex.flex-col.items-center")
        count = await data_containers.count()
        print(f"Found {count} data containers")
        
        rating = "N/A"
        cost = "N/A"
        details = "N/A"
        last_updated = "N/A"
        
        # Iterate through each container to find the specific data
        for i in range(count):
            container = data_containers.nth(i)
            label_elem = container.locator("span.text-muted-foreground").first
            
            if await label_elem.count() > 0:
                label = (await label_elem.inner_text()).strip()
                print(f"Found label: {label}")
                
                if label == "Rating":
                    # Inside Rating, find the <span> after the SVGs
                    rating_value_elem = container.locator("span.ml-1.text-sm.text-muted-foreground")
                    if await rating_value_elem.count() > 0:
                        rating = (await rating_value_elem.inner_text()).strip()
                        print(f"Extracted rating: {rating}")
                
                elif label == "Cost":
                    value_elem = container.locator("span.font-medium").first
                    if await value_elem.count() > 0:
                        cost = (await value_elem.inner_text()).strip()
                        print(f"Extracted cost: {cost}")
                
                elif label == "Details":
                    value_elem = container.locator("span.font-medium").first
                    if await value_elem.count() > 0:
                        details = (await value_elem.inner_text()).strip()
                        print(f"Extracted details: {details}")
                
                elif label == "Updated":
                    value_elem = container.locator("span.font-medium").first
                    if await value_elem.count() > 0:
                        last_updated = (await value_elem.inner_text()).strip()
                        print(f"Extracted last updated: {last_updated}")
        
        product_data = {
            "title": title,
            "id_and_category": {
                "id": id_text,
                "category": category_text
            },
            "rating": rating,
            "cost": cost,
            "details": details,
            "last_updated": last_updated
        }
        
        print(f"Completed product data extraction: {product_data}")
        return product_data

    except Exception as e:
        print(f"⚠ Error parsing product card: {e}")
        return {}

    
async def export_to_json(data, filename="products.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 Data exported to {filename}")

async def scrape_product_data(page):
    try:
        print("Starting to scrape product data...")
        
        # Wait for the product cards to load
        await page.wait_for_selector("div.flex.flex-col.sm\\:flex-row.sm\\:items-center.justify-between.p-4.border.rounded-md", timeout=60000)
        
        # Get all product cards with a more specific selector
        product_cards = page.locator("div.flex.flex-col.sm\\:flex-row.sm\\:items-center.justify-between.p-4.border.rounded-md")
        count = await product_cards.count()
        
        print(f"🔍 Found {count} product cards")
        
        products = []
        
        for i in range(count):
            print(f"Processing product card {i+1}/{count}...")
            card = product_cards.nth(i)
            product_data = await extract_product_data(card)
            products.append(product_data)
            print(f"Added product {i+1} to results")
        
        print(f"Completed scraping {len(products)} products")
        return products
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []

async def main():
    async with async_playwright() as playwright:
        context = None
        page = None
        try:
            context, page = await get_browser_context(playwright)
            await navigate_to_full_catalog(page)
            products = await scrape_product_data(page)
            await export_to_json(products)
        except Exception as e:
            print(f"❌ Script failed: {e}")
        finally:
            if page:
                await page.close()
            if context:
                await context.close()

if __name__ == "__main__":
    asyncio.run(main())