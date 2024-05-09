# Playwright Pool

A sophisticated, asynchronous browser page pool management library for Python powered by Playwright. This library streamlines the handling of multiple browser instances for web scraping, automated testing, and various other tasks that necessitate the use of multiple browser pages.

## Features

- **Asynchronous Design**: Built with a fully asynchronous architecture to cater to I/O-bound operations efficiently.
- **Support for Multiple Browsers**: Compatible with Chromium, Firefox, and WebKit browsers, providing flexibility across different web environments.
- **Customization Options**: Offers extensive options for customizing browser launch and context settings to meet specific requirements.
- **Resource Optimization**: Implements page reuse strategies to reduce resource consumption and enhance overall performance.
- **Metrics Tracking**: Includes comprehensive metrics tracking for pool size, acquisition and release counts, and page utilization time, facilitating easier monitoring and debugging.

## Installation

To install the library, use the following pip command:

```bash
pip install git+https://github.com/tgscan-dev/playwright-pool.git
```

## Quick Start

Here's a basic example to demonstrate how to use the library:

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

Example demonstrating the use of proxy settings:

```python
from playwright_pool import BrowserPagePool

async def main():
    # Define proxy settings
    context_options = {
        "proxy": {
            "server": "http://your-proxy-server:port",  # Substitute with your actual proxy server address and port
            "username": "your-username",  # Substitute with your proxy username if authentication is needed
            "password": "your-password"   # Substitute with your proxy password if authentication is needed
        }
    }

    # Initialize BrowserPagePool with proxy settings
    pool = BrowserPagePool(
        max_pages=2,
        browser_type="chromium",
        context_options=context_options
    )

    async with pool:
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

Instantiate a `BrowserPagePool` by specifying the desired maximum number of pages, browser type, and any launch or context options:

```python
pool = BrowserPagePool(max_pages=5, browser_type="chromium", launch_options={"headless": True})
```

### Acquiring and Releasing Pages

To obtain a browser page from the pool, use `acquire`, and to return it, use `release`:

```python
page = await pool.acquire()
# Use the page as needed for browsing, scraping, etc.
await pool.release(page)
```

To acquire a page with a timeout, you can use `acquire_with_timeout`:

```python
try:
    page = await pool.acquire_with_timeout(timeout=5.0)
    # Use the page for your task
    await pool.release(page)
except TimeoutError:
    print("Failed to acquire page within the specified timeout")
```

### Metrics

Retrieve metrics about the usage of the page pool:

```python
metrics = pool.get_metrics()
print(metrics)
```

## Development

Contributions to improve the library are welcome!

## License

This project is licensed under the MIT License.