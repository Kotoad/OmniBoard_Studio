# Raspberry Pi Auto-Discovery Module - IMPROVED & DEBUGGED VERSION
# Uses Paramiko for cross-platform SSH without external dependencies
# THIS VERSION HANDLES CRASHES AND PROVIDES DETAILED LOGGING

import subprocess
import socket
import threading
import time
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
from Imports import get_Utils, logging
Utils = get_Utils()
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    logging.error("Paramiko not installed. Install with: pip install paramiko")


class RPiAutoDiscovery:
    """Auto-discover Raspberry Pi on local network"""
    
    DEFAULT_USERNAME = "pi"
    DEFAULT_PASSWORDS = ["raspberry", ""]  # Common defaults
    SCAN_TIMEOUT = 2.0  # Increased from 0.5
    SSH_TIMEOUT = 15  # Increased timeout
    
    @staticmethod
    def scan_network_for_rpi(network_prefix: None = None, max_ips: int = 254) -> List[Dict]:
        """Scan network for Raspberry Pi devices"""
        #logging.info("Starting network scan for Raspberry Pi devices...")
        #logging.debug(f"Network prefix provided: '{network_prefix}'")
        if network_prefix is None:
            logging.warning("network_prefix is None, defaulting to empty string")
            network_prefix = ""
            try:
                # Get local IP to determine network
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #logging.info("Determining local IP address...")
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                #logging.info(f"Local IP detected: {local_ip}")
                s.close()
                # Extract first 3 octets
                network_prefix = '.'.join(local_ip.split('.')[:-1])
                #logging.info(f"Auto-detected network: {network_prefix}.0/24")
            except:
                logging.warning("Could not determine local IP. Using default network prefix.")
                network_prefix = "192.168.1"  # Fallback
        
        found_devices = []
        threads = []
        
        #logging.info(f"Scanning network {network_prefix}.1-{max_ips} for Raspberry Pi...")
        
        def check_ip(ip_address):
            """Check single IP for Raspberry Pi"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(RPiAutoDiscovery.SCAN_TIMEOUT)
                result = sock.connect_ex((ip_address, 22))
                sock.close()
                
                if result == 0:
                    try:
                        hostname = socket.gethostbyaddr(ip_address)[0]
                    except:
                        hostname = "Unknown"
                    
                    is_rpi = "raspberrypi" in hostname.lower()
                    
                    found_devices.append({
                        'ip': ip_address,
                        'hostname': hostname,
                        'is_rpi': is_rpi
                    })
                    
                    if is_rpi:
                        #logging.info(f"Found Raspberry Pi: {hostname} ({ip_address})")
                        pass
                    else:
                        #logging.debug(f"Found device: {hostname} ({ip_address})")
                        pass
            
            except Exception:
                pass
        
        # Scan IPs in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(1, min(max_ips + 1, 255)):
                ip = f"{network_prefix}.{i}"
                futures.append(executor.submit(check_ip, ip))
        
        # Wait for completion
        # CRITICAL FIX: Wait for ALL threads to complete
        for thread in threads:
            thread.join()  # No timeout - wait until done
        
        # Clear thread references
        threads.clear()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        #logging.info(f"Network scan complete. Found {len(found_devices)} devices.")
        return found_devices
    
    @staticmethod
    def find_rpi_on_network() -> Optional[str]:
        """Use mDNS to find Raspberry Pi"""
        #logging.info("Searching for raspberrypi.local using mDNS...")
        
        try:
            ip_address = socket.gethostbyname("raspberrypi.local")
            #logging.info(f"Found Raspberry Pi at: {ip_address}")
            return ip_address
        except socket.gaierror:
            #logging.warninig("raspberrypi.local not found. Trying network scan...")
            return None
    
    @staticmethod
    def test_ssh_connection_paramiko(ip: str, username: str, password: str = None) -> bool:
        """Test SSH connection using Paramiko (RECOMMENDED)"""
        if not PARAMIKO_AVAILABLE:
            logging.error("Paramiko not available. Install: pip install paramiko")
            return False
        
        passwords_to_try = [password] if password else RPiAutoDiscovery.DEFAULT_PASSWORDS
        #logging.info(f"Passwords to try for SSH connection: {passwords_to_try}")
        for pwd in passwords_to_try:
            #logging.info(f"Testing SSH connection to {ip} with username '{username}' and password {pwd}...")
            try:
                
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #logging.debug(f"Attempting SSH connection to {ip} with username '{username}' and password {pwd}...")
                # Try to connect
                client.connect(
                    hostname=ip,
                    username=username,
                    password=pwd if pwd else None,
                    timeout=RPiAutoDiscovery.SSH_TIMEOUT,
                    look_for_keys=True if not pwd else False,
                    allow_agent=True if not pwd else False
                )
                
                # Test command execution
                stdin, stdout, stderr = client.exec_command("echo 'Connected'")
                output = stdout.read().decode().strip()
                
                client.close()
                
                if output == "Connected":
                    #logging.info(f"SSH connection successful: {username}@{ip}")
                    return True
            
            except paramiko.AuthenticationException:
                logging.warning(f"Authentication failed for password: {pwd}")
                continue
            except paramiko.SSHException as e:
                logging.error(f"SSH error: {e}")
                continue
            except socket.timeout:
                logging.warning(f"Connection timeout to {ip}")
                return False
            except Exception as e:
                logging.error(f"Connection error: {e}")
                continue
        
        logging.error(f"All authentication attempts failed for {ip}")
        return False
    
    @staticmethod
    def get_rpi_info_paramiko(ip: str, username: str, password: str = None) -> Optional[Dict]:
        """Get Raspberry Pi info using Paramiko - CRASH SAFE VERSION"""
        if not PARAMIKO_AVAILABLE:
            logging.error("Paramiko not available. Install: pip install paramiko")
            return None
        
        if not ip or not username:
            logging.error(f"Invalid parameters: ip={ip}, username={username}")
            return None
        
        passwords_to_try = [password] if password else RPiAutoDiscovery.DEFAULT_PASSWORDS
        
        #logging.info(f"Passwords to try for SSH connection: {passwords_to_try}")
        
        for pwd in passwords_to_try:
            #logging.debug(f"Attempting SSH connection to {ip} with username '{username}' and password {pwd}...")
            client = None
            try:
                #logging.debug(f"Connecting to {ip} to retrieve device info...")
                
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Connect with timeout
                client.connect(
                    hostname=ip,
                    username=username,
                    password=pwd if pwd else None,
                    timeout=RPiAutoDiscovery.SSH_TIMEOUT,
                    look_for_keys=True if not pwd else False,
                    allow_agent=True if not pwd else False
                )
                
                #logging.info(f"Connected successfully, fetching device info...")
                
                # Get hostname
                try:
                    stdin, stdout, stderr = client.exec_command("hostname")
                    hostname = stdout.read().decode().strip()
                    if not hostname:
                        hostname = "unknown"
                except Exception as e:
                    logging.warning(f"Failed to get hostname: {e}")
                    hostname = "unknown"
                
                # Get model
                try:
                    stdin, stdout, stderr = client.exec_command("cat /proc/device-tree/model 2>/dev/null || echo 'Unknown'")
                    model = stdout.read().decode().strip().replace('\x00', '')
                    if not model:
                        model = "Unknown"
                except Exception as e:
                    logging.warning(f"Failed to get model: {e}")
                    model = "Unknown"
                
                # Get OS info
                try:
                    stdin, stdout, stderr = client.exec_command("lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME 2>/dev/null || echo 'Unknown'")
                    os_info = stdout.read().decode().strip()
                    if not os_info:
                        os_info = "Unknown"
                except Exception as e:
                    logging.warning(f"Failed to get OS info: {e}")
                    os_info = "Unknown"
                
                # Build result SAFELY - ensure all fields are strings
                result = {
                    'ip': str(ip),
                    'hostname': str(hostname) if hostname else 'unknown',
                    'username': str(username),
                    'password': str(pwd) if pwd else '',
                    'model': str(model) if model else 'Unknown',
                    'os': str(os_info) if os_info else 'Unknown'
                }
                
                #logging.info(f"Successfully retrieved device info!")
                #logging.info(f"Auto-detection result: {result}")
                
                if client:
                    client.close()
                
                return result
            
            except paramiko.AuthenticationException as e:
                logging.warning(f"Authentication failed for {username}@{ip} with password {'***' if pwd else '(none)'}")
                continue
            
            except paramiko.SSHException as e:
                logging.error(f"SSH error: {e}")
                continue
            
            except socket.timeout as e:
                logging.warning(f"Connection timeout to {ip}: {e}")
                continue
            
            except Exception as e:
                logging.error(f"Unexpected error with password {'***' if pwd else '(none)'}: {type(e).__name__}: {e}")
                continue
            
            finally:
                if client:
                    try:
                        client.close()
                    except:
                        pass
        
        logging.error(f"Failed to get RPI info from {ip} - all authentication attempts failed")
        return None


class RPiConnectionWizard:
    """Interactive wizard to connect to Raspberry Pi"""
    
    @staticmethod
    def auto_detect_rpi() -> Optional[Dict]:
        """Automatically detect and connect to Raspberry Pi - CRASH SAFE"""
        #logging.info("\n" + "="*60)
        #logging.info("RASPBERRY PI AUTO-DETECTION WIZARD")
        #logging.info("="*60 + "\n")
        
        # Check Paramiko availability
        if not PARAMIKO_AVAILABLE:
            logging.error("Paramiko not installed!")
            #logging.info("Install with: pip install paramiko")
            return None
        
        # Step 1: Try mDNS
        #logging.info("Step 1: Trying mDNS (raspberrypi.local)...")
        ip = RPiAutoDiscovery.find_rpi_on_network()
        
        if not ip:
            # Step 2: Network scan
            #logging.info("\nStep 2: Scanning network for devices...")
            devices = RPiAutoDiscovery.scan_network_for_rpi()
            
            if not devices:
                logging.error("No devices found on network")
                return None
            
            # Prefer RPI devices
            rpi_devices = [d for d in devices if d.get('is_rpi', False)]
            
            if rpi_devices:
                ip = rpi_devices[0]['ip']
                #logging.info(f"Selected: {rpi_devices[0]['hostname']} ({ip})")
            else:
                ip = devices[0]['ip']
                #logging.info(f"Using first device: {devices[0]['hostname']} ({ip})")
        
        if not ip:
            logging.error("Could not determine IP address")
            return None
        
        # Step 3: Get RPI info
        #logging.info(f"\nStep 3: Getting Raspberry Pi information...")
        
        # Use stored username/password if available, otherwise try defaults
        try:
            #logging.info("Retrieving stored credentials from app settings...")
            username = Utils.app_settings.rpi_user or RPiAutoDiscovery.DEFAULT_USERNAME
            password = Utils.app_settings.rpi_password or None
            #logging.info(f"Using stored credentials: {username}@{ip}")
        except:
            username = RPiAutoDiscovery.DEFAULT_USERNAME
            password = None
            #logging.info(f"Using default credentials: {username}@{ip}")
        
        rpi_info = RPiAutoDiscovery.get_rpi_info_paramiko(ip, username=username, password=password)
        
        if rpi_info and isinstance(rpi_info, dict) and 'ip' in rpi_info:
            #logging.info(f"\nSuccessfully connected!")
            #logging.info(f"  Hostname: {rpi_info.get('hostname', 'unknown')}")
            #logging.info(f"  IP: {rpi_info.get('ip', 'unknown')}")
            #logging.info(f"  Model: {rpi_info.get('model', 'Unknown')}")
            #logging.info(f"  OS: {rpi_info.get('os', 'Unknown')}")
            return rpi_info
        else:
            logging.error("❌ Could not establish connection - rpi_info is invalid")
            #logging.info(f"   rpi_info type: {type(rpi_info)}")
            #logging.info(f"   rpi_info value: {rpi_info}")
            return None


if __name__ == "__main__":
    result = RPiConnectionWizard.auto_detect_rpi()
    if result:
        #logging.info("\nConnection info ready:")
        #logging.info(result)
        pass
    else:
        logging.error("\nAuto-detection failed")