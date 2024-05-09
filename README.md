# BrowserPagePool

A simple, asynchronous browser page pool management library for Python, utilizing Playwright. This library makes it easy to manage a pool of browser pages for efficient web scraping, testing, or any other task that requires multiple browser instances.

## Features

- **Asynchronous Design**: Fully asynchronous architecture, making it suitable for I/O-bound tasks.
- **Flexible Browser Support**: Supports Chromium, Firefox, and WebKit browsers.
- **Customizable**: Allows custom launch and context options for browsers.
- **Resource Efficient**: Reuses browser pages to minimize resource consumption and improve performance.
- **Metrics Tracking**: Tracks metrics like pool size, acquired count, released count, and page use time for monitoring and debugging.

## Installation

```bash
pip install playwright-pool
```

## Quick Start

Here's a simple example to get started:

```python
from playwright_pool import BrowserPagePool

async def main():
    async with BrowserPagePool(max_pages=2) as pool:
        page = await pool.acquire()
        await page.goto("https://example.com")
        print(await page.title())
        await pool.release(page)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Usage

### Creating a Page Pool

Create an instance of `BrowserPagePool` by specifying the maximum number of pages, browser type, and any launch or context options:

```python
pool = BrowserPagePool(max_pages=5, browser_type="chromium", launch_options={"headless": True})
```

### Acquiring and Releasing Pages

Use `acquire` to get a browser page from the pool and `release` to return it:

```python
page = await pool.acquire()
# Use the page for browsing, scraping, etc.
await pool.release(page)
```

To acquire a page with a timeout, use `acquire_with_timeout`:

```python
try:
    page = await pool.acquire_with_timeout(timeout=5.0)
    # Use the page
    await pool.release(page)
except TimeoutError:
    print("Failed to acquire page within timeout")
```

### Getting Metrics

You can retrieve metrics about the page pool usage:

```python
metrics = pool.get_metrics()
print(metrics)
```

## Development

To contribute to BrowserPagePool, clone the repository, make changes, and submit a pull request. Ensure you follow the coding standards and write tests for new features.

## License

MIT

