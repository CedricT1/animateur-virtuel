#!/usr/bin/env python3

import asyncio
import edge_tts
import config

async def main():
    text = "Bonjour, ceci est un test de la synthèse vocale avec Edge TTS."
    communicate = edge_tts.Communicate(text, config.VOICE, rate=config.RATE, pitch=config.PITCH)
    await communicate.save("test_tts.mp3")
    print(f"Test audio généré avec la voix {config.VOICE}")
    print(f"Vitesse: {config.RATE}")
    print(f"Hauteur: {config.PITCH}")

if __name__ == "__main__":
    asyncio.run(main()) 