import asyncio
import nodriver as uc

async def main():
    browser = await uc.start()
    
    # Primero la página principal para establecer la sesión
    await browser.get("https://www.fotmob.com")
    await asyncio.sleep(4)
    
    # Ahora la API
    page = await browser.get("https://www.fotmob.com/api/data/matchDetails?matchId=5102020")
    content = await page.get_content()
    print(content)
    
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())