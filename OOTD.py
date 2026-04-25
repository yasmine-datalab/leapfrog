import time
import sys

def run_grwm_protocol():
    # Le point d'entrée dont on a parlé
    print("\nGet Ready With Me")
    time.sleep(0.8)
    
    print("\n[SYSTEM] : Initializing WOOHP server...")
    time.sleep(1)
    
    logs = [
        "[INFO]  : Loading fashion_core_v5.dll...",
        "[INFO]  : Syncing Totally Spies soundtrack...",
        "[DEBUG] : Checking elegance_level... [CRITICAL_HIGH]",
        "[DEBUG] : Scanning wardrobe database...",
        "[INFO]  : Optimizing skincare_routine.sh",
        "[SYSTEM] : Beauty and brain",
        "[WARN]  : High levels of charisma detected."
    ]

    for log in logs:
        print(log)
        time.sleep(0.3) # Vitesse de défilement des logs

    print("\n[EXECUTING CODE] : Compiling final look...")
    time.sleep(1.2)
    
    print("\n" + "="*40)
    print("      [SUCCESS] : REDIRECTION")
    print("="*30)
    print("\n>>> STARTING GRWM SEQUENCE NOW...")

if __name__ == "__main__":
    run_grwm_protocol()