#!/usr/bin/env python3

import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    print("Voix françaises disponibles :")
    print("-----------------------------")
    for voice in voices:
        if voice["Locale"].startswith("fr"):
            print(f"Nom exact pour config.py: {voice['Name']}")
            print(f"Genre: {voice['Gender']}")
            print(f"Locale: {voice['Locale']}")
            print("-----------------------------")

if __name__ == "__main__":
    asyncio.run(main()) 