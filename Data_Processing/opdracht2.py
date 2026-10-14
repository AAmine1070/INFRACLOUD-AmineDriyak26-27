import platform
import socket
from pprint import pprint
import psutil

def get_primary_interface_info():
    """Détecte la carte réseau active menant vers l'extérieur."""
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
        for addr in addrs[primary_nic]:
            # Détection MAC compatible Windows, Linux et macOS
            af_link = getattr(psutil, "AF_LINK", None)
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
    # 1. Opslag: partition C:\ sous Windows ou / sous Linux
    root_mount = "C:\\" if platform.system() == "Windows" else "/"
    disk_fs = "Onbekend"
    try:
        for part in psutil.disk_partitions(all=False):
            if part.mountpoint == root_mount:
                disk_fs = part.fstype
                break
        disk_usage = psutil.disk_usage(root_mount)
        disk_total_gb = round(disk_usage.total / (1024**3), 2)
    except PermissionError:
        disk_total_gb = 0.0

    # 2. Netwerk
    mac, ipv4, ipv6_global, ipv6_ll = get_primary_interface_info()

    # 3. CPU & RAM
    freq = psutil.cpu_freq()
    max_freq_mhz = round(freq.max, 2) if freq and freq.max else None
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)

    # 4. Le dictionnaire final demandé
    systeeminformatie = {
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

    return systeeminformatie

if __name__ == "__main__":
    resultaat = filter_system_info()
    print("\n--- GEFILTERDE SYSTEEMINFORMATIE ---")
    pprint(resultaat)