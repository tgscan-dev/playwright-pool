from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Literal, List, AsyncIterator

from playwright.async_api import async_playwright, Browser, Page


@dataclass
class BrowserPagePool:
    max_pages: int
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    launch_options: Dict = field(default_factory=dict)
    context_options: Dict = field(default_factory=dict)
    pages: List[Page] = field(default_factory=list, init=False)
    browser: Optional[Browser] = None
    lock: asyncio.Lock = field(default=asyncio.Lock(), init=False)
    page_available: asyncio.Condition = field(init=False)
    metrics: Dict[str, int] = field(
        default_factory=lambda: {
            "pool_size": 0,
            "acquired_count": 0,
            "released_count": 0,
            "page_use_time": 0,
        },
        init=False,
    )

    def __post_init__(self):
        self.page_available = asyncio.Condition(lock=self.lock)

    async def __aenter__(self) -> BrowserPagePool:
        self.playwright = await async_playwright().__aenter__()
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = await browser_launcher.launch(**self.launch_options)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

    async def __aiter__(self) -> AsyncIterator[Page]:
        acquired_pages = 0
        while acquired_pages < self.max_pages:
            page = await self.acquire()
            yield page
            await self.release(page)
            acquired_pages += 1

    async def acquire(self) -> Page:
        return await self._acquire_page()

    async def acquire_with_timeout(self, timeout: float) -> Page:
        return await self._acquire_page(timeout)

    async def _acquire_page(self, timeout: Optional[float] = None) -> Page:
        async with self.lock:
            while len(self.pages) >= self.max_pages:
                if timeout is None:
                    await self.page_available.wait()
                else:
                    try:
                        await asyncio.wait_for(
                            self.page_available.wait(), timeout=timeout
                        )
                    except asyncio.TimeoutError:
                        raise TimeoutError("wait for page timeout")

            context = await self.browser.new_context(**self.context_options)
            page = await context.new_page()
            self.pages.append(page)
            self._update_metrics("acquire")
            return page

    async def release(self, page: Page):
        async with self.lock:
            self.pages.remove(page)
            await page.close()
            self.page_available.notify()
            self._update_metrics("release")

    def _update_metrics(self, action: str):
        if action == "acquire":
            self.metrics["pool_size"] = len(self.pages)
            self.metrics["acquired_count"] += 1
        elif action == "release":
            self.metrics["pool_size"] = len(self.pages)
            self.metrics["released_count"] += 1

    def get_metrics(self) -> Dict:
        return self.metrics


if __name__ == "__main__":
    BrowserPagePool()
