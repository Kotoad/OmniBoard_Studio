# Raspberry Pi Auto-Discovery Module - IMPROVED & DEBUGGED VERSION
# Uses Paramiko for cross-platform SSH without external dependencies
# THIS VERSION HANDLES CRASHES AND PROVIDES DETAILED LOGGING

import subprocess
import socket
import threading
import time
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
from Imports import get_Utils
Utils = get_Utils()
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    print("⚠️ Paramiko not installed. Install with: pip install paramiko")


class RPiAutoDiscovery:
    """Auto-discover Raspberry Pi on local network"""
    
    DEFAULT_USERNAME = "pi"
    DEFAULT_PASSWORDS = ["raspberry", ""]  # Common defaults
    SCAN_TIMEOUT = 2.0  # Increased from 0.5
    SSH_TIMEOUT = 15  # Increased timeout
    
    @staticmethod
    def scan_network_for_rpi(network_prefix: None = None, max_ips: int = 254) -> List[Dict]:
        """Scan network for Raspberry Pi devices"""
        #print("🔍 Starting network scan for Raspberry Pi devices...")
        #print(f"Network prefix provided: '{network_prefix}'")
        if network_prefix is None:
            print("⚠️ network_prefix is None, defaulting to empty string")
            network_prefix = ""
            try:
                # Get local IP to determine network
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #print("🌐 Determining local IP address...")
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                #print(f"✓ Local IP detected: {local_ip}")
                s.close()
                # Extract first 3 octets
                network_prefix = '.'.join(local_ip.split('.')[:-1])
                #print(f"📡 Auto-detected network: {network_prefix}.0/24")
            except:
                print("⚠️ Could not determine local IP. Using default network prefix.")
                network_prefix = "192.168.1"  # Fallback
        
        found_devices = []
        threads = []
        
        #print(f"🔍 Scanning network {network_prefix}.1-{max_ips} for Raspberry Pi...")
        
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
                        #print(f"✓ Found Raspberry Pi: {hostname} ({ip_address})")
                        pass
                    else:
                        #print(f"  Found device: {hostname} ({ip_address})")
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
        # ✅ CRITICAL FIX: Wait for ALL threads to complete
        for thread in threads:
            thread.join()  # No timeout - wait until done
        
        # ✅ Clear thread references
        threads.clear()
        
        # ✅ Force garbage collection
        import gc
        gc.collect()
        
        #print(f"✓ Network scan complete. Found {len(found_devices)} devices.")
        return found_devices
    
    @staticmethod
    def find_rpi_on_network() -> Optional[str]:
        """Use mDNS to find Raspberry Pi"""
        #print("🔍 Searching for raspberrypi.local using mDNS...")
        
        try:
            ip_address = socket.gethostbyname("raspberrypi.local")
            #print(f"✓ Found Raspberry Pi at: {ip_address}")
            return ip_address
        except socket.gaierror:
            print("⚠ raspberrypi.local not found. Trying network scan...")
            return None
    
    @staticmethod
    def test_ssh_connection_paramiko(ip: str, username: str, password: str = None) -> bool:
        """Test SSH connection using Paramiko (RECOMMENDED)"""
        if not PARAMIKO_AVAILABLE:
            print("❌ Paramiko not available. Install: pip install paramiko")
            return False
        
        passwords_to_try = [password] if password else RPiAutoDiscovery.DEFAULT_PASSWORDS
        print(f"Passwords to try for SSH connection: {passwords_to_try}")
        for pwd in passwords_to_try:
            print(f"📋 Testing SSH connection to {ip} with username '{username}' and password {pwd}...")
            try:
                
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(f"📋 Attempting SSH connection to {ip} with username '{username}' and password {pwd}...")
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
                    #print(f"✓ SSH connection successful: {username}@{ip}")
                    return True
            
            except paramiko.AuthenticationException:
                print(f"⚠ Authentication failed for password: {pwd}")
                continue
            except paramiko.SSHException as e:
                print(f"⚠ SSH error: {e}")
                continue
            except socket.timeout:
                print(f"⚠ Connection timeout to {ip}")
                return False
            except Exception as e:
                print(f"⚠ Connection error: {e}")
                continue
        
        print(f"❌ All authentication attempts failed for {ip}")
        return False
    
    @staticmethod
    def get_rpi_info_paramiko(ip: str, username: str, password: str = None) -> Optional[Dict]:
        """Get Raspberry Pi info using Paramiko - CRASH SAFE VERSION"""
        if not PARAMIKO_AVAILABLE:
            print("❌ Paramiko not available. Install: pip install paramiko")
            return None
        
        if not ip or not username:
            print(f"❌ Invalid parameters: ip={ip}, username={username}")
            return None
        
        passwords_to_try = [password] if password else RPiAutoDiscovery.DEFAULT_PASSWORDS
        
        print(f"Passwords to try for SSH connection: {passwords_to_try}")
        
        for pwd in passwords_to_try:
            print(f"📋 Attempting SSH connection to {ip} with username '{username}' and password {pwd}...")
            client = None
            try:
                #print(f"📋 Connecting to {ip} to retrieve device info...")
                
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
                
                #print(f"✓ Connected successfully, fetching device info...")
                
                # Get hostname
                try:
                    stdin, stdout, stderr = client.exec_command("hostname")
                    hostname = stdout.read().decode().strip()
                    if not hostname:
                        hostname = "unknown"
                except Exception as e:
                    print(f"  ⚠ Failed to get hostname: {e}")
                    hostname = "unknown"
                
                # Get model
                try:
                    stdin, stdout, stderr = client.exec_command("cat /proc/device-tree/model 2>/dev/null || echo 'Unknown'")
                    model = stdout.read().decode().strip().replace('\x00', '')
                    if not model:
                        model = "Unknown"
                except Exception as e:
                    print(f"  ⚠ Failed to get model: {e}")
                    model = "Unknown"
                
                # Get OS info
                try:
                    stdin, stdout, stderr = client.exec_command("lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME 2>/dev/null || echo 'Unknown'")
                    os_info = stdout.read().decode().strip()
                    if not os_info:
                        os_info = "Unknown"
                except Exception as e:
                    print(f"  ⚠ Failed to get OS info: {e}")
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
                
                #print(f"✓ Successfully retrieved device info!")
                #print(f"🔍 Auto-detection result: {result}")
                
                if client:
                    client.close()
                
                return result
            
            except paramiko.AuthenticationException as e:
                print(f"⚠ Authentication failed for {username}@{ip} with password {'***' if pwd else '(none)'}")
                continue
            
            except paramiko.SSHException as e:
                print(f"⚠ SSH error: {e}")
                continue
            
            except socket.timeout as e:
                print(f"⚠ Connection timeout to {ip}: {e}")
                continue
            
            except Exception as e:
                print(f"⚠ Unexpected error with password {'***' if pwd else '(none)'}: {type(e).__name__}: {e}")
                continue
            
            finally:
                if client:
                    try:
                        client.close()
                    except:
                        pass
        
        print(f"❌ Failed to get RPI info from {ip} - all authentication attempts failed")
        return None


class RPiConnectionWizard:
    """Interactive wizard to connect to Raspberry Pi"""
    
    @staticmethod
    def auto_detect_rpi() -> Optional[Dict]:
        """Automatically detect and connect to Raspberry Pi - CRASH SAFE"""
        #print("\n" + "="*60)
        #print("🚀 RASPBERRY PI AUTO-DETECTION WIZARD")
        #print("="*60 + "\n")
        
        # Check Paramiko availability
        if not PARAMIKO_AVAILABLE:
            print("❌ Paramiko not installed!")
            print("Install with: pip install paramiko")
            return None
        
        # Step 1: Try mDNS
        #print("Step 1: Trying mDNS (raspberrypi.local)...")
        ip = RPiAutoDiscovery.find_rpi_on_network()
        
        if not ip:
            # Step 2: Network scan
            #print("\nStep 2: Scanning network for devices...")
            devices = RPiAutoDiscovery.scan_network_for_rpi()
            
            if not devices:
                print("❌ No devices found on network")
                return None
            
            # Prefer RPI devices
            rpi_devices = [d for d in devices if d.get('is_rpi', False)]
            
            if rpi_devices:
                ip = rpi_devices[0]['ip']
                #print(f"✓ Selected: {rpi_devices[0]['hostname']} ({ip})")
            else:
                ip = devices[0]['ip']
                #print(f"✓ Using first device: {devices[0]['hostname']} ({ip})")
        
        if not ip:
            print("❌ Could not determine IP address")
            return None
        
        # Step 3: Get RPI info
        print(f"\nStep 3: Getting Raspberry Pi information...")
        
        # Use stored username/password if available, otherwise try defaults
        try:
            print("📋 Retrieving stored credentials from app settings...")
            username = Utils.app_settings.rpi_user or RPiAutoDiscovery.DEFAULT_USERNAME
            password = Utils.app_settings.rpi_password or None
            #print(f"Using stored credentials: {username}@{ip}")
        except:
            username = RPiAutoDiscovery.DEFAULT_USERNAME
            password = None
            print(f"Using default credentials: {username}@{ip}")
        
        rpi_info = RPiAutoDiscovery.get_rpi_info_paramiko(ip, username=username, password=password)
        
        if rpi_info and isinstance(rpi_info, dict) and 'ip' in rpi_info:
            #print(f"\n✅ Successfully connected!")
            #print(f"  Hostname: {rpi_info.get('hostname', 'unknown')}")
            #print(f"  IP: {rpi_info.get('ip', 'unknown')}")
            #print(f"  Model: {rpi_info.get('model', 'Unknown')}")
            #print(f"  OS: {rpi_info.get('os', 'Unknown')}")
            return rpi_info
        else:
            print("❌ Could not establish connection - rpi_info is invalid")
            #print(f"   rpi_info type: {type(rpi_info)}")
            #print(f"   rpi_info value: {rpi_info}")
            return None


if __name__ == "__main__":
    result = RPiConnectionWizard.auto_detect_rpi()
    if result:
        #print("\n✅ Connection info ready:")
        #print(result)
        pass
    else:
        print("\n❌ Auto-detection failed")