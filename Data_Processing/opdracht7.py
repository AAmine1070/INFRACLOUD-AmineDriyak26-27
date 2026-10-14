import csv
import ipaddress
import re

csv_bestand = "alle_systeeminformatie.csv"
mac_patroon = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

with open(csv_bestand, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for idx, rij in enumerate(reader, start=1):
        pc = rij.get("computernaam", f"Rij {idx}")
        print(f"\n--- Valideren van computer: {pc} ---")

        # 1. Controle IPv4
        ipv4 = rij.get("ipv4_adres_primaire_nic")
        try:
            ipaddress.IPv4Address(ipv4)
            print(f"  [OK] IPv4 is geldig: {ipv4}")
        except ValueError:
            print(f"  [FOUT] Ongeldig IPv4-adres: {ipv4}")

        # 2. Controle MAC-adres
        mac = rij.get("mac_adres_primaire_nic")
        if mac and mac_patroon.match(mac):
            print(f"  [OK] MAC-formaat is correct: {mac}")
        else:
            print(f"  [FOUT] Ongeldig MAC-adres: {mac}")

        # 3. Controle RAM-waarde
        try:
            ram = float(rij.get("totale_hoeveelheid_ram_gb", 0))
            if 2.0 <= ram <= 128.0:
                print(f"  [OK] RAM-waarde is realistisch: {ram} GB")
            else:
                print(f"  [WAARSCHUWING] Ongebruikelijke RAM-waarde: {ram} GB")
        except ValueError:
            print(f"  [FOUT] RAM kon niet naar getal worden omgezet.")