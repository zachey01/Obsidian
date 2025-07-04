import requests

class Offsets:
    m_pBoneArray = 496
    dwViewMatrix = None
    dwEntityList = None
    dwLocalPlayerController = None
    dwLocalPlayerPawn = None
    m_iIDEntIndex = None
    m_hPlayerPawn = None
    m_fFlags = None
    m_iszPlayerName = None
    m_iHealth = None
    m_iTeamNum = None
    m_vOldOrigin = None
    m_pGameSceneNode = None
    m_bDormant = None

    @staticmethod
    def fetch_offsets():
        try:
            offsets_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json"
            client_dll_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json"
            
            offsets = requests.get(offsets_url).json()
            client_dll = requests.get(client_dll_url).json()
            
            offsets_name = ["dwViewMatrix", "dwEntityList", "dwLocalPlayerController", "dwLocalPlayerPawn"]
            for k in offsets_name:
                setattr(Offsets, k, offsets["client.dll"][k])
            
            client_dll_name = {
                "m_iIDEntIndex": "C_CSPlayerPawnBase",
                "m_hPlayerPawn": "CCSPlayerController",
                "m_fFlags": "C_BaseEntity",
                "m_iszPlayerName": "CBasePlayerController",
                "m_iHealth": "C_BaseEntity",
                "m_iTeamNum": "C_BaseEntity",
                "m_vOldOrigin": "C_BasePlayerPawn",
                "m_pGameSceneNode": "C_BaseEntity",
                "m_bDormant": "CGameSceneNode",
            }
            
            for k, v in client_dll_name.items():
                setattr(Offsets, k, client_dll["client.dll"]["classes"][v]["fields"][k])
        except Exception as e:
            raise Exception(f"Failed to fetch offsets: {e}")
