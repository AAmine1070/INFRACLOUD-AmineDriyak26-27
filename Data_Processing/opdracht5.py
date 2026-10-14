import platform
import socket
import psutil
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


def get_primary_interface_info():
    """Identificeert de actieve netwerkinterface naar buiten."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        active_ip = s.getsockname()[0]
        s.close()
    except Exception:
        active_ip = "127.0.0.1"

    primary_nic = None
    addrs = psutil.net_if_addrs()
    for nic, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET and addr.address == active_ip:
                primary_nic = nic
                break
        if primary_nic:
            break

    mac = None
    ipv4 = None
    ipv6_global = None
    ipv6_link_local = None

    if primary_nic and primary_nic in addrs:
        af_link = getattr(psutil, "AF_LINK", None)
        for addr in addrs[primary_nic]:
            if af_link is not None and addr.family == af_link:
                mac = addr.address
            elif addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == socket.AF_INET6:
                clean_ip = addr.address.split("%")[0]
                if clean_ip.lower().startswith("fe80:"):
                    ipv6_link_local = clean_ip
                else:
                    ipv6_global = clean_ip

    return mac, ipv4, ipv6_global, ipv6_link_local


def filter_system_info():
    """Verzamelt en filtert de gevraagde systeeminformatie."""
    root_mount = "C:\\" if platform.system() == "Windows" else "/"
    disk_fs = "Onbekend"
    disk_total_gb = 0.0

    try:
        for part in psutil.disk_partitions(all=False):
            if part.mountpoint == root_mount:
                disk_fs = part.fstype
                break
        disk_usage = psutil.disk_usage(root_mount)
        disk_total_gb = round(disk_usage.total / (1024**3), 2)
    except PermissionError:
        pass

    mac, ipv4, ipv6_global, ipv6_ll = get_primary_interface_info()
    freq = psutil.cpu_freq()
    max_freq_mhz = round(freq.max, 2) if freq and freq.max else None
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)

    return {
        "computernaam": platform.node(),
        "computermodel": platform.machine(),
        "processor": platform.processor(),
        "aantal_fysieke_cpu_cores": psutil.cpu_count(logical=False),
        "maximale_cpu_frequentie_mhz": max_freq_mhz,
        "totale_hoeveelheid_ram_gb": ram_gb,
        "bestandssysteem_opslag": disk_fs,
        "opslagcapaciteit_gb": disk_total_gb,
        "mac_adres_primaire_nic": mac,
        "ipv4_adres_primaire_nic": ipv4,
        "ipv6_adres_primaire_nic": ipv6_global,
        "ipv6_link_local_adres_primaire_nic": ipv6_ll,
    }


if __name__ == "__main__":
    # Stap 1: Systeeminformatie ophalen
    resultaat = filter_system_info()

    # Stap 2: Excel-werkboek initialiseren
    excel_bestandsnaam = "systeeminformatie.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Systeeminformatie"

    # Stap 3: Headers toevoegen
    kolomnamen = [
        "computernaam",
        "computermodel",
        "processor",
        "aantal_fysieke_cpu_cores",
        "maximale_cpu_frequentie_mhz",
        "totale_hoeveelheid_ram_gb",
        "bestandssysteem_opslag",
        "opslagcapaciteit_gb",
        "mac_adres_primaire_nic",
        "ipv4_adres_primaire_nic",
        "ipv6_adres_primaire_nic",
        "ipv6_link_local_adres_primaire_nic",
    ]
    ws.append(kolomnamen)

    # Stap 4: Gegevensrij toevoegen
    rij_waarden = []
    for veld in kolomnamen:
        waarde = resultaat.get(veld)
        rij_waarden.append("N/A" if waarde is None else waarde)
    ws.append(rij_waarden)

    # Stap 5: Opmaak toepassen (headerkleur en automatische kolombreedte)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")

    for col_num in range(1, len(kolomnamen) + 1):
        cel = ws.cell(row=1, column=col_num)
        cel.font = header_font
        cel.fill = header_fill

        max_len = max(
            len(str(ws.cell(row=1, column=col_num).value or "")),
            len(str(ws.cell(row=2, column=col_num).value or ""))
        )
        col_letter = get_column_letter(col_num)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Stap 6: Bestand opslaan
    wb.save(excel_bestandsnaam)
    print(f"Gegevens succesvol geëxporteerd naar {excel_bestandsnaam}")