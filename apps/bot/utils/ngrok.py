import os
import asyncio
import aiohttp

from apps.bot.utils.logging import logger


async def get_ngrok_url(max_retries: int = 20, delay: int = 3) -> str:
    """
    Fetch the public Ngrok HTTPS URL and save its domain to `NGROK_DOMAIN`.
    Retries several times if the Ngrok API is not yet available.

    :param max_retries: Number of retry attempts. Defaults to 20.
    :type max_retries: int
    :param delay: Delay (in seconds) between retries. Defaults to 3.
    :type delay: int
    :return: The public Ngrok HTTPS URL (e.g., "https://abcd1234.ngrok.io").
    :rtype: str
    :raises RuntimeError: If no HTTPS tunnel is found after all retries.
    """
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://ngrok:4040/api/tunnels") as resp:
                    data = await resp.json()
                    for tunnel in data.get("tunnels", []):
                        if tunnel.get("proto") == "https":
                            url = tunnel["public_url"]
                            logger.info(f"✅ Ngrok URL obtained: {url}")
                            domain = url.replace("https://", "").replace("http://", "")
                            os.environ["NGROK_DOMAIN"] = domain
                            logger.info(f"🌍 NGROK_DOMAIN set to: {domain}")

                            return url
        except Exception:
            logger.warning(f"⏳ Ngrok not ready yet ({attempt + 1}/{max_retries})...")
            await asyncio.sleep(delay)

    raise RuntimeError("Failed to obtain Ngrok URL — no tunnel found.")
