# Valorant Presence Editor - Python Script

A Python script to modify your displayed presence in Valorant (rank, level, player card, title, etc.)

## ⚠️ Important Notes

- **Temporary Changes**: All changes are temporary and reset when you restart Valorant
- **Display Only**: This only changes what other players SEE, not your actual account data
- **No Ban Risk**: Uses official local Valorant API endpoints (same as the game client)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed
2. **Valorant running** and logged in
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the Script

```bash
python valorant_presence_editor.py
```

## 📊 What Can You Modify?

| Field | Description | Example Values |
|-------|-------------|----------------|
| `competitiveTier` | Your displayed rank | `0-27` (see Rank Tiers below) |
| `leaderboardPosition` | Leaderboard ranking | `1-500` or `0` for none |
| `accountLevel` | Account level | `1-999+` |
| `playerCardId` | Player card UUID | Valid UUID string |
| `playerTitleId` | Player title UUID | Valid UUID string |
| `queueId` | Game mode | `"competitive"`, `"unrated"`, etc. |
| `partyOwnerMatchScoreAllyTeam` | Ally team score | `0-13` |
| `partyOwnerMatchScoreEnemyTeam` | Enemy team score | `0-13` |
| `sessionLoopState` | Game state | `"MENUS"` or `"INGAME"` |

## 🎖️ Rank Tiers Reference

```
0  = Unranked
3  = Iron 1       |  4  = Iron 2       |  5  = Iron 3
6  = Bronze 1     |  7  = Bronze 2     |  8  = Bronze 3
9  = Silver 1     | 10  = Silver 2     | 11  = Silver 3
12 = Gold 1       | 13  = Gold 2       | 14  = Gold 3
15 = Platinum 1   | 16  = Platinum 2   | 17  = Platinum 3
18 = Diamond 1    | 19  = Diamond 2    | 20  = Diamond 3
21 = Ascendant 1  | 22  = Ascendant 2  | 23  = Ascendant 3
24 = Immortal 1   | 25  = Immortal 2   | 26  = Immortal 3
27 = Radiant
```

## 📝 Usage Examples

### Example 1: Change Rank to Radiant

```python
editor.update_presence({
    "competitiveTier": 27  # Radiant
})
```

### Example 2: Radiant with Leaderboard #1

```python
editor.update_presence({
    "competitiveTier": 27,  # Radiant
    "leaderboardPosition": 1  # #1 Radiant
})
```

### Example 3: Change Account Level

```python
editor.update_presence({
    "accountLevel": 500
})
```

### Example 4: Full Custom Profile

```python
editor.update_presence({
    "competitiveTier": 27,     # Radiant
    "leaderboardPosition": 50,  # Top 50
    "accountLevel": 999,        # Level 999
    "queueId": "competitive",
    "sessionLoopState": "MENUS"
})
```

### Example 5: Show In-Game with Score

```python
editor.update_presence({
    "sessionLoopState": "INGAME",
    "queueId": "competitive",
    "partyOwnerMatchScoreAllyTeam": 12,
    "partyOwnerMatchScoreEnemyTeam": 10
})
```

### Example 6: Auto-Updater (Keeps Presence Active)

```python
# Update every 25 seconds to keep presence active
while True:
    editor.update_presence({
        "competitiveTier": 27,
        "accountLevel": 500
    })
    time.sleep(25)
```

## 🔧 Technical Details

### Endpoint Information

**Primary Endpoint**: `PUT https://127.0.0.1:{port}/chat/v2/me`

**Authentication**: Basic Auth via lockfile
- Username: `riot`
- Password: From lockfile at `%LOCALAPPDATA%\Riot Games\Riot Client\Config\lockfile`

**Request Format**:
```json
{
  "state": "chat",
  "private": "<base64_encoded_config>",
  "shared": {
    "actor": "",
    "details": "",
    "location": "",
    "product": "valorant",
    "time": 1234567890000
  }
}
```

**Private Field Structure** (base64 decoded):
```json
{
  "competitiveTier": 27,
  "leaderboardPosition": 1,
  "accountLevel": 500,
  "playerCardId": "uuid-here",
  "playerTitleId": "uuid-here",
  "queueId": "competitive",
  "partyOwnerMatchScoreAllyTeam": 0,
  "partyOwnerMatchScoreEnemyTeam": 0,
  "sessionLoopState": "MENUS",
  "partyId": "727",
  "isValid": true,
  "isIdle": false,
  "partyClientVersion": "release-08.11-shipping-26-2492508"
}
```

### How It Works

1. **Reads Lockfile**: Gets port and password from Valorant lockfile
2. **Connects to Local API**: Uses HTTPS with self-signed cert (SSL verification disabled)
3. **Authenticates**: Basic auth with `riot:password`
4. **Gets Current Presence**: Retrieves current settings via `GET /chat/v2/me`
5. **Modifies Config**: Updates specified fields
6. **Sends Update**: `PUT /chat/v2/me` with base64-encoded JSON in `private` field

### Status States

The `state` field is automatically determined based on config:

- `"offline"` - When `partyId` is empty
- `"dnd"` - When `isValid` is false
- `"away"` - When in menus and idle
- `"chat"` - Default active state

## 🛡️ Safety & Limitations

### ✅ Safe Because:
- Uses **official Riot local API** (same endpoints the game uses)
- Only modifies **display data**, not account data
- Changes are **temporary** and client-side
- No external server communication

### ⚠️ Limitations:
- Changes **reset** when you restart Valorant
- Must keep updating every ~30 seconds or game overwrites it
- Does **NOT** change your actual rank, level, or unlocks
- Does **NOT** work in competitive matches (server validates real rank)

## 🐛 Troubleshooting

### "Lockfile not found"
- Make sure Valorant is running and you're logged in
- Check that Riot Client is active

### "Chat session not ready"
- Wait a few seconds after launching Valorant
- Make sure you're past the login screen

### "Error updating presence"
- Valorant might have updated and changed the API
- Check if the lockfile port/password are correct
- Restart Valorant and try again

### Changes not showing
- Update more frequently (every 20-25 seconds)
- Make sure you're not in a match (changes work in lobby/menus)
- Check if friends can see the changes (may not update immediately)

## 📚 Additional Resources

- **Original Repo**: Check the main Vulx-Local repository for more features
- **Player Card IDs**: Find card UUIDs at Valorant community resources
- **Player Title IDs**: Find title UUIDs at Valorant community resources

## ⚖️ Legal & Ethical Notice

This script is for **educational purposes** and uses only local APIs. It:
- Does NOT modify game files
- Does NOT inject code into the game
- Does NOT communicate with Riot servers directly
- Does NOT provide competitive advantages

Use responsibly and respect other players.

## 🤝 Contributing

Found a bug or want to add features? Contributions welcome!

---

**Made for the Valorant community** 🎮
