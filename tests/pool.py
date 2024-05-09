import pytest

from playwright_pool.pool import BrowserPagePool


@pytest.mark.asyncio
async def test_create_pool():
    async with BrowserPagePool(max_pages=2) as pool:
        assert pool.max_pages == 2
        assert pool.browser_type == "chromium"
        assert pool.browser is not None
        assert pool.playwright is not None


@pytest.mark.asyncio
async def test_acquire_release_page():
    async with BrowserPagePool(max_pages=2) as pool:
        page1 = await pool.acquire()
        assert len(pool.pages) == 1
        assert pool.metrics["acquired_count"] == 1

        page2 = await pool.acquire()
        assert len(pool.pages) == 2
        assert pool.metrics["acquired_count"] == 2

        await pool.release(page1)
        assert len(pool.pages) == 1
        assert pool.metrics["released_count"] == 1

        await pool.release(page2)
        assert len(pool.pages) == 0
        assert pool.metrics["released_count"] == 2


@pytest.mark.asyncio
async def test_acquire_with_timeout():
    async with BrowserPagePool(max_pages=1) as pool:
        page = await pool.acquire()
        assert len(pool.pages) == 1

        with pytest.raises(TimeoutError):
            await pool.acquire_with_timeout(timeout=0.1)

        await pool.release(page)
        assert len(pool.pages) == 0


@pytest.mark.asyncio
async def test_async_iteration():
    async with BrowserPagePool(max_pages=2) as pool:
        async for page in pool:
            assert page is not None


@pytest.mark.asyncio
async def test_metrics():
    async with BrowserPagePool(max_pages=2) as pool:
        page1 = await pool.acquire()
        page2 = await pool.acquire()

        metrics = pool.get_metrics()
        assert metrics["pool_size"] == 2
        assert metrics["acquired_count"] == 2
        assert metrics["released_count"] == 0

        await pool.release(page1)
        await pool.release(page2)

        metrics = pool.get_metrics()
        assert metrics["pool_size"] == 0
        assert metrics["acquired_count"] == 2
        assert metrics["released_count"] == 2


@pytest.mark.asyncio
async def test_headless_mode():
    async with BrowserPagePool(
        max_pages=2,
        launch_options={"headless": True},
    ) as pool:
        metrics = pool.get_metrics()
        assert metrics["pool_size"] == 0
        assert metrics["acquired_count"] == 0
        assert metrics["released_count"] == 0

        page1 = await pool.acquire()
        assert pool.metrics["pool_size"] == 1
        assert pool.metrics["acquired_count"] == 1

        await page1.goto("https://www.example.com")
        assert page1.url == "https://www.example.com/"

        page2 = await pool.acquire()
        assert pool.metrics["pool_size"] == 2
        assert pool.metrics["acquired_count"] == 2

        await page2.goto("https://www.example.org")
        assert page2.url == "https://www.example.org/"

        await pool.release(page1)
        assert pool.metrics["pool_size"] == 1
        assert pool.metrics["released_count"] == 1

        await pool.release(page2)
        assert pool.metrics["pool_size"] == 0
        assert pool.metrics["released_count"] == 2


@pytest.mark.asyncio
async def test_acquire_over_max_pages_with_timeout():
    # Initialize a BrowserPagePool with a maximum of 2 pages and headless mode enabled
    async with BrowserPagePool(max_pages=2, launch_options={"headless": True}) as pool:
        # Acquire the first two pages, which should be successful since it does not exceed the max_pages
        page1 = await pool.acquire()
        page2 = await pool.acquire()

        # Ensure that the number of acquired pages matches the max_pages limit
        assert len(pool.pages) == 2

        # Attempt to acquire a third page but set a very short timeout.
        # Expect a TimeoutError because there won't be any available page within the timeout period.
        with pytest.raises(TimeoutError):
            await pool.acquire_with_timeout(timeout=0.1)

        # Release the previously acquired pages
        await pool.release(page1)
        await pool.release(page2)

        # Confirm that all pages have been released back to the pool
        assert len(pool.pages) == 0
