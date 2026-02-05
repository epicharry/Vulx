#!/usr/bin/env python3
"""
Valorant Presence Editor
Modifies your displayed presence in Valorant (rank, level, player card, etc.)
Changes are temporary and reset when you restart the game.
"""

import os
import json
import base64
import time
import urllib3
import requests
from pathlib import Path

# Disable SSL warnings since we're connecting to local Valorant API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ValorantPresenceEditor:
    def __init__(self):
        self.port = None
        self.password = None
        self.base_url = None
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for local connection

    def read_lockfile(self):
        """Read Valorant lockfile to get connection details"""
        lockfile_path = Path(os.environ['LOCALAPPDATA']) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'

        if not lockfile_path.exists():
            raise FileNotFoundError(
                "Valorant lockfile not found. Make sure Valorant is running!"
            )

        with open(lockfile_path, 'r') as f:
            data = f.read().split(':')
            # Format: name:pid:port:password:protocol
            self.port = data[2]
            self.password = data[3]
            self.base_url = f"https://127.0.0.1:{self.port}"

        print(f"[✓] Connected to Valorant on port {self.port}")

    def setup_auth(self):
        """Setup authentication headers"""
        auth_string = f"riot:{self.password}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()

        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'User-Agent': 'ShooterGame/8 Windows/10.0.19042.1.768.64bit',
            'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuNzY4LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'
        })

    def get_chat_session(self):
        """Get current chat session to ensure game is ready"""
        try:
            response = self.session.get(f"{self.base_url}/chat/v1/session", timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('loaded') and data.get('state') == 'connected':
                print(f"[✓] Chat session active - Game ready")
                return data
            else:
                print(f"[!] Chat session not ready yet...")
                return None
        except Exception as e:
            print(f"[!] Error getting chat session: {e}")
            return None

    def get_current_presence(self):
        """Get current presence data"""
        try:
            response = self.session.get(f"{self.base_url}/chat/v2/me", timeout=5)
            response.raise_for_status()
            data = response.json()

            # Decode the private field if it exists
            if 'private' in data and data['private']:
                try:
                    decoded = base64.b64decode(data['private']).decode('utf-8')
                    data['private_decoded'] = json.loads(decoded)
                except:
                    pass

            return data
        except Exception as e:
            print(f"[!] Error getting presence: {e}")
            return None

    def update_presence(self, config):
        """
        Update presence with custom configuration

        Args:
            config (dict): Configuration with these optional fields:
                - competitiveTier: int (0-27) - Your displayed rank
                - leaderboardPosition: int - Leaderboard position
                - accountLevel: int - Account level
                - playerCardId: str - UUID of player card
                - playerTitleId: str - UUID of player title
                - queueId: str - Game mode (e.g., "competitive", "unrated")
                - partyOwnerMatchScoreAllyTeam: int - Ally team score
                - partyOwnerMatchScoreEnemyTeam: int - Enemy team score
                - sessionLoopState: str - "MENUS" or "INGAME"
        """

        # Get current presence or use defaults
        current = self.get_current_presence()

        if current and 'private_decoded' in current:
            base_config = current['private_decoded']
        else:
            # Default configuration
            base_config = {
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

        # Update with user-provided config
        base_config.update(config)

        # Determine status based on config
        if base_config.get("partyId") in ["", None]:
            status = "offline"
        elif base_config.get("isValid") == False:
            status = "dnd"
        elif base_config.get("sessionLoopState") == "MENUS" and base_config.get("isIdle") == True:
            status = "away"
        else:
            status = "chat"

        # Create the presence payload
        private_b64 = base64.b64encode(json.dumps(base_config).encode()).decode()

        payload = {
            "state": status,
            "private": private_b64,
            "shared": {
                "actor": "",
                "details": "",
                "location": "",
                "product": "valorant",
                "time": int(time.time() * 1000) + 35000  # Extended timestamp
            }
        }

        try:
            response = self.session.put(
                f"{self.base_url}/chat/v2/me",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            print("[✓] Presence updated successfully!")
            return True
        except Exception as e:
            print(f"[✗] Error updating presence: {e}")
            return False

    def connect(self):
        """Initialize connection to Valorant"""
        print("=" * 60)
        print("Valorant Presence Editor")
        print("=" * 60)

        self.read_lockfile()
        self.setup_auth()

        # Wait for chat session to be ready
        print("[...] Waiting for game to be ready...")
        for i in range(10):
            session = self.get_chat_session()
            if session:
                break
            time.sleep(2)
        else:
            print("[✗] Game not ready. Make sure you're logged in!")
            return False

        return True


def print_rank_info():
    """Print rank tier information"""
    ranks = {
        0: "Unranked",
        3: "Iron 1", 4: "Iron 2", 5: "Iron 3",
        6: "Bronze 1", 7: "Bronze 2", 8: "Bronze 3",
        9: "Silver 1", 10: "Silver 2", 11: "Silver 3",
        12: "Gold 1", 13: "Gold 2", 14: "Gold 3",
        15: "Platinum 1", 16: "Platinum 2", 17: "Platinum 3",
        18: "Diamond 1", 19: "Diamond 2", 20: "Diamond 3",
        21: "Ascendant 1", 22: "Ascendant 2", 23: "Ascendant 3",
        24: "Immortal 1", 25: "Immortal 2", 26: "Immortal 3",
        27: "Radiant"
    }

    print("\n" + "=" * 60)
    print("RANK TIERS REFERENCE")
    print("=" * 60)
    for tier, name in ranks.items():
        print(f"{tier:2d} = {name}")
    print("=" * 60 + "\n")


# ============================================================================
# EXAMPLES - Uncomment the example you want to use
# ============================================================================

if __name__ == "__main__":
    editor = ValorantPresenceEditor()

    if not editor.connect():
        exit(1)

    # ========================================================================
    # EXAMPLE 1: Change Rank to Radiant
    # ========================================================================
    print("\n[Example 1] Setting rank to Radiant...")
    editor.update_presence({
        "competitiveTier": 27  # Radiant
    })

    # ========================================================================
    # EXAMPLE 2: Change Rank to Immortal 3 with Leaderboard Position
    # ========================================================================
    # print("\n[Example 2] Setting rank to Immortal 3 with leaderboard...")
    # editor.update_presence({
    #     "competitiveTier": 26,  # Immortal 3
    #     "leaderboardPosition": 100  # Top 100
    # })

    # ========================================================================
    # EXAMPLE 3: Change Account Level
    # ========================================================================
    # print("\n[Example 3] Setting account level to 999...")
    # editor.update_presence({
    #     "accountLevel": 999
    # })

    # ========================================================================
    # EXAMPLE 4: Set In-Game Status with Score
    # ========================================================================
    # print("\n[Example 4] Setting in-game status with score...")
    # editor.update_presence({
    #     "sessionLoopState": "INGAME",
    #     "queueId": "competitive",
    #     "partyOwnerMatchScoreAllyTeam": 12,
    #     "partyOwnerMatchScoreEnemyTeam": 10
    # })

    # ========================================================================
    # EXAMPLE 5: Full Custom Profile
    # ========================================================================
    # print("\n[Example 5] Setting full custom profile...")
    # editor.update_presence({
    #     "competitiveTier": 27,  # Radiant
    #     "leaderboardPosition": 1,  # #1 Radiant
    #     "accountLevel": 500,
    #     "queueId": "competitive",
    #     "sessionLoopState": "MENUS"
    # })

    # ========================================================================
    # EXAMPLE 6: Show Available Rank Tiers
    # ========================================================================
    # print_rank_info()

    # ========================================================================
    # EXAMPLE 7: Interactive Mode - Custom Input
    # ========================================================================
    # print("\n[Interactive Mode] Enter custom values:")
    # print_rank_info()
    # try:
    #     rank = int(input("Enter rank tier (0-27): "))
    #     level = int(input("Enter account level: "))
    #     leaderboard = int(input("Enter leaderboard position (0 for none): "))
    #
    #     config = {
    #         "competitiveTier": rank,
    #         "accountLevel": level
    #     }
    #
    #     if leaderboard > 0:
    #         config["leaderboardPosition"] = leaderboard
    #
    #     editor.update_presence(config)
    # except ValueError:
    #     print("[✗] Invalid input!")

    # ========================================================================
    # EXAMPLE 8: Auto-Updater (Keep presence active)
    # ========================================================================
    # print("\n[Auto-Updater] Keeping presence active (Ctrl+C to stop)...")
    # try:
    #     while True:
    #         editor.update_presence({
    #             "competitiveTier": 27,
    #             "accountLevel": 500
    #         })
    #         print("[...] Presence refreshed. Waiting 25 seconds...")
    #         time.sleep(25)  # Update every 25 seconds
    # except KeyboardInterrupt:
    #     print("\n[✓] Stopped auto-updater")

    print("\n" + "=" * 60)
    print("Done! Check your Valorant profile.")
    print("Note: Changes reset when you restart the game.")
    print("=" * 60)
