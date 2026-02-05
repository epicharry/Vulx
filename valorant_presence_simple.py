#!/usr/bin/env python3
"""
Simple Valorant Presence Editor - Minimal Version
Just run and follow the prompts!
"""

import os
import json
import base64
import time
import urllib3
import requests
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ValorantPresence:
    def __init__(self):
        lockfile_path = Path(os.environ['LOCALAPPDATA']) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'

        if not lockfile_path.exists():
            raise Exception("Valorant not running! Launch the game first.")

        data = lockfile_path.read_text().split(':')
        self.port = data[2]
        password = data[3]

        auth = base64.b64encode(f"riot:{password}".encode()).decode()

        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json'
        })
        self.base_url = f"https://127.0.0.1:{self.port}"

        print(f"✓ Connected to Valorant (port {self.port})")

    def update(self, **kwargs):
        config = {
            "competitiveTier": 0,
            "leaderboardPosition": 0,
            "accountLevel": 1,
            "playerCardId": "9fb348bc-41a0-91ad-8a3e-818035c4e561",
            "playerTitleId": "00000000-0000-0000-0000-000000000000",
            "queueId": "",
            "partyOwnerMatchScoreAllyTeam": 0,
            "partyOwnerMatchScoreEnemyTeam": 0,
            "sessionLoopState": "MENUS",
            "partyId": "727",
            "isValid": True,
            "isIdle": False,
            "partyClientVersion": "release-08.11-shipping-26-2492508"
        }

        config.update(kwargs)

        payload = {
            "state": "chat",
            "private": base64.b64encode(json.dumps(config).encode()).decode(),
            "shared": {
                "actor": "",
                "details": "",
                "location": "",
                "product": "valorant",
                "time": int(time.time() * 1000) + 35000
            }
        }

        self.session.put(f"{self.base_url}/chat/v2/me", json=payload, timeout=5)
        print("✓ Presence updated!")


RANKS = {
    0: "Unranked", 3: "Iron 1", 4: "Iron 2", 5: "Iron 3",
    6: "Bronze 1", 7: "Bronze 2", 8: "Bronze 3",
    9: "Silver 1", 10: "Silver 2", 11: "Silver 3",
    12: "Gold 1", 13: "Gold 2", 14: "Gold 3",
    15: "Platinum 1", 16: "Platinum 2", 17: "Platinum 3",
    18: "Diamond 1", 19: "Diamond 2", 20: "Diamond 3",
    21: "Ascendant 1", 22: "Ascendant 2", 23: "Ascendant 3",
    24: "Immortal 1", 25: "Immortal 2", 26: "Immortal 3",
    27: "Radiant"
}


if __name__ == "__main__":
    print("=" * 60)
    print("Valorant Presence Editor (Simple)")
    print("=" * 60)

    try:
        val = ValorantPresence()
        time.sleep(1)

        print("\nRank Tiers:")
        for tier, name in RANKS.items():
            print(f"  {tier:2d} = {name}")

        print("\n" + "-" * 60)
        rank = int(input("\nEnter rank tier (0-27): "))
        level = int(input("Enter account level: "))
        leaderboard = int(input("Enter leaderboard position (0 for none): "))

        config = {
            "competitiveTier": rank,
            "accountLevel": level
        }

        if leaderboard > 0:
            config["leaderboardPosition"] = leaderboard

        print("\nUpdating presence...")
        val.update(**config)

        print("\n" + "=" * 60)
        print("Done! Check your Valorant profile.")
        print("Note: Changes reset when you restart the game.")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. Valorant is running")
        print("  2. You're logged in")
        print("  3. Python packages are installed (pip install requests)")
