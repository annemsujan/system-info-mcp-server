#!/usr/bin/env python3

import asyncio
import json
import sys
import argparse
from typing import Any, Dict, List, Optional
import psutil
import platform
from datetime import datetime

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP package not found. Install with: pip install mcp")
    sys.exit(1)

class SystemInfoServer:
    """System Information MCP Server for Python"""
    
    def __init__(self):
        self.mcp = FastMCP("System Info Server")
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all MCP tools"""
        
        @self.mcp.tool()
        def get_cpu_info() -> Dict[str, Any]:
            """Get detailed CPU information including usage, cores, frequency, and temperature"""
            try:
                # CPU basic info
                cpu_count_logical = psutil.cpu_count(logical=True)
                cpu_count_physical = psutil.cpu_count(logical=False)
                cpu_freq = psutil.cpu_freq()
                cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
                cpu_times = psutil.cpu_times()
                
                # Load averages (Unix-like systems)
                load_avg = getattr(psutil, 'getloadavg', lambda: [0, 0, 0])()
                
                # Temperature (if available)
                temp = "Not available"
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Try to get CPU temperature
                        for name, entries in temps.items():
                            if 'cpu' in name.lower() or 'core' in name.lower():
                                if entries:
                                    temp = f"{entries[0].current}°C"
                                    break
                except (AttributeError, OSError):
                    pass
                
                return {
                    "brand": platform.processor() or "Unknown",
                    "architecture": platform.machine(),
                    "cores": {
                        "physical": cpu_count_physical,
                        "logical": cpu_count_logical,
                    },
                    "frequency": {
                        "current": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "Unknown",
                        "min": f"{cpu_freq.min:.2f} MHz" if cpu_freq and cpu_freq.min else "Unknown",
                        "max": f"{cpu_freq.max:.2f} MHz" if cpu_freq and cpu_freq.max else "Unknown",
                    },
                    "usage": {
                        "overall": f"{cpu_percent:.1f}%",
                        "user": f"{cpu_times.user / sum(cpu_times) * 100:.1f}%",
                        "system": f"{cpu_times.system / sum(cpu_times) * 100:.1f}%",
                        "idle": f"{cpu_times.idle / sum(cpu_times) * 100:.1f}%",
                    },
                    "temperature": temp,
                    "load_average": [f"{load:.2f}" for load in load_avg],
                }
            except Exception as e:
                return {"error": f"Failed to get CPU info: {str(e)}"}
        
        @self.mcp.tool()
        def get_memory_info() -> Dict[str, Any]:
            """Get memory usage information including RAM and swap details"""
            try:
                # Virtual memory (RAM)
                mem = psutil.virtual_memory()
                
                # Swap memory
                swap = psutil.swap_memory()
                
                return {
                    "total": f"{mem.total / 1024**3:.2f} GB",
                    "used": f"{mem.used / 1024**3:.2f} GB",
                    "available": f"{mem.available / 1024**3:.2f} GB",
                    "free": f"{mem.free / 1024**3:.2f} GB",
                    "usage_percent": f"{mem.percent:.1f}%",
                    "swap": {
                        "total": f"{swap.total / 1024**3:.2f} GB",
                        "used": f"{swap.used / 1024**3:.2f} GB",
                        "free": f"{swap.free / 1024**3:.2f} GB",
                        "usage_percent": f"{swap.percent:.1f}%",
                    },
                }
            except Exception as e:
                return {"error": f"Failed to get memory info: {str(e)}"}
        
        @self.mcp.tool()
        def get_disk_usage() -> List[Dict[str, Any]]:
            """Get disk usage information for all mounted drives and filesystems"""
            try:
                disks = []
                disk_partitions = psutil.disk_partitions()
                
                for partition in disk_partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disks.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "filesystem": partition.fstype,
                            "total": f"{usage.total / 1024**3:.2f} GB",
                            "used": f"{usage.used / 1024**3:.2f} GB",
                            "free": f"{usage.free / 1024**3:.2f} GB",
                            "usage_percent": f"{(usage.used / usage.total * 100):.1f}%",
                        })
                    except (PermissionError, OSError):
                        # Skip inaccessible drives
                        continue
                
                return disks
            except Exception as e:
                return [{"error": f"Failed to get disk usage: {str(e)}"}]
        
        @self.mcp.tool()
        def get_running_processes(limit: int = 20, sort_by: str = "cpu") -> Dict[str, Any]:
            """Get list of currently running processes with CPU and memory usage
            
            Args:
                limit: Maximum number of processes to return (default: 20)
                sort_by: Sort processes by 'cpu', 'memory', or 'name' (default: 'cpu')
            """
            try:
                processes = []
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                               'memory_info', 'status', 'create_time', 'username']):
                    try:
                        pinfo = proc.info
                        pinfo['cpu_percent'] = proc.cpu_percent()
                        pinfo['memory_mb'] = pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0
                        processes.append(pinfo)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort processes
                if sort_by == "memory":
                    processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
                elif sort_by == "name":
                    processes.sort(key=lambda x: x.get('name', '').lower())
                else:  # cpu
                    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                
                # Limit results
                limited_processes = processes[:limit]
                
                # Format for output
                formatted_processes = []
                for proc in limited_processes:
                    formatted_processes.append({
                        "pid": proc.get('pid', 'N/A'),
                        "name": proc.get('name', 'N/A'),
                        "cpu_percent": f"{proc.get('cpu_percent', 0):.1f}%",
                        "memory_percent": f"{proc.get('memory_percent', 0):.1f}%",
                        "memory_mb": f"{proc.get('memory_mb', 0):.1f} MB",
                        "status": proc.get('status', 'N/A'),
                        "username": proc.get('username', 'N/A'),
                        "started": datetime.fromtimestamp(proc.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if proc.get('create_time') else 'N/A',
                    })
                
                return {
                    "summary": {
                        "total_processes": len(processes),
                        "shown_processes": len(formatted_processes),
                        "sorted_by": sort_by,
                    },
                    "processes": formatted_processes,
                }
            except Exception as e:
                return {"error": f"Failed to get process info: {str(e)}"}
        
        @self.mcp.tool()
        def get_system_info() -> Dict[str, Any]:
            """Get general system information including OS, uptime, hardware details"""
            try:
                # System information
                uname = platform.uname()
                boot_time = psutil.boot_time()
                uptime_seconds = psutil.time.time() - boot_time
                
                # Calculate uptime
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                
                return {
                    "operating_system": {
                        "system": uname.system,
                        "release": uname.release,
                        "version": uname.version,
                        "machine": uname.machine,
                        "processor": uname.processor,
                    },
                    "hostname": uname.node,
                    "uptime": f"{days}d {hours}h {minutes}m",
                    "boot_time": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
                    "users": [
                        {
                            "name": user.name,
                            "terminal": user.terminal,
                            "host": user.host,
                            "started": datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S'),
                        }
                        for user in psutil.users()
                    ],
                    "python_version": platform.python_version(),
                }
            except Exception as e:
                return {"error": f"Failed to get system info: {str(e)}"}
        
        @self.mcp.tool()
        def get_network_info() -> Dict[str, Any]:
            """Get network interface information, connections, and statistics"""
            try:
                # Network interfaces
                interfaces = []
                net_if_addrs = psutil.net_if_addrs()
                net_if_stats = psutil.net_if_stats()
                
                for interface_name, addresses in net_if_addrs.items():
                    interface_info = {
                        "name": interface_name,
                        "addresses": [],
                        "is_up": net_if_stats[interface_name].isup if interface_name in net_if_stats else False,
                        "speed": f"{net_if_stats[interface_name].speed} Mbps" if interface_name in net_if_stats and net_if_stats[interface_name].speed > 0 else "Unknown",
                    }
                    
                    for addr in addresses:
                        interface_info["addresses"].append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        })
                    
                    interfaces.append(interface_info)
                
                # Network connections
                try:
                    connections = psutil.net_connections()
                    connection_summary = {
                        "total": len(connections),
                        "tcp": len([c for c in connections if c.type.name == 'SOCK_STREAM']),
                        "udp": len([c for c in connections if c.type.name == 'SOCK_DGRAM']),
                        "listening": len([c for c in connections if c.status == 'LISTEN']),
                        "established": len([c for c in connections if c.status == 'ESTABLISHED']),
                    }
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    connection_summary = {"error": "Access denied to connection information"}
                
                return {
                    "interfaces": interfaces,
                    "connections": connection_summary,
                }
            except Exception as e:
                return {"error": f"Failed to get network info: {str(e)}"}
        
        @self.mcp.tool()
        def get_quick_stats() -> Dict[str, Any]:
            """Get a quick overview of CPU, memory, and disk usage"""
            try:
                # Quick CPU
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Quick memory
                mem = psutil.virtual_memory()
                
                # Quick disk (primary partition)
                disk_usage = None
                try:
                    primary_disk = psutil.disk_partitions()[0]
                    usage = psutil.disk_usage(primary_disk.mountpoint)
                    disk_usage = {
                        "usage_percent": f"{(usage.used / usage.total * 100):.1f}%",
                        "used": f"{usage.used / 1024**3:.1f} GB",
                        "total": f"{usage.total / 1024**3:.1f} GB",
                        "mount": primary_disk.mountpoint,
                    }
                except (IndexError, OSError):
                    disk_usage = "N/A"
                
                # Uptime
                uptime_seconds = psutil.time.time() - psutil.boot_time()
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                
                return {
                    "cpu_usage": f"{cpu_percent:.1f}%",
                    "memory": {
                        "usage_percent": f"{mem.percent:.1f}%",
                        "used": f"{mem.used / 1024**3:.1f} GB",
                        "total": f"{mem.total / 1024**3:.1f} GB",
                    },
                    "disk": disk_usage,
                    "uptime": f"{days}d {hours}h",
                }
            except Exception as e:
                return {"error": f"Failed to get quick stats: {str(e)}"}

    def get_quick_stats(self) -> Dict[str, Any]:
        """Get a quick overview of CPU, memory, and disk usage"""
        try:
            # Quick CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Quick memory
            mem = psutil.virtual_memory()
            
            # Quick disk (primary partition)
            disk_usage = None
            try:
                primary_disk = psutil.disk_partitions()[0]
                usage = psutil.disk_usage(primary_disk.mountpoint)
                disk_usage = {
                    "usage_percent": f"{(usage.used / usage.total * 100):.1f}%",
                    "used": f"{usage.used / 1024**3:.1f} GB",
                    "total": f"{usage.total / 1024**3:.1f} GB",
                    "mount": primary_disk.mountpoint,
                }
            except (IndexError, OSError):
                disk_usage = "N/A"
            
            # Uptime
            uptime_seconds = psutil.time.time() - psutil.boot_time()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            
            return {
                "cpu_usage": f"{cpu_percent:.1f}%",
                "memory": {
                    "usage_percent": f"{mem.percent:.1f}%",
                    "used": f"{mem.used / 1024**3:.1f} GB",
                    "total": f"{mem.total / 1024**3:.1f} GB",
                },
                "disk": disk_usage,
                "uptime": f"{days}d {hours}h",
            }
        except Exception as e:
            return {"error": f"Failed to get quick stats: {str(e)}"}

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information including usage, cores, frequency, and temperature"""
        try:
            # CPU basic info
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_times = psutil.cpu_times()
            
            # Load averages (Unix-like systems)
            load_avg = getattr(psutil, 'getloadavg', lambda: [0, 0, 0])()
            
            # Temperature (if available)
            temp = "Not available"
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Try to get CPU temperature
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            if entries:
                                temp = f"{entries[0].current}°C"
                                break
            except (AttributeError, OSError):
                pass
            
            return {
                "brand": platform.processor() or "Unknown",
                "architecture": platform.machine(),
                "cores": {
                    "physical": cpu_count_physical,
                    "logical": cpu_count_logical,
                },
                "frequency": {
                    "current": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "Unknown",
                    "min": f"{cpu_freq.min:.2f} MHz" if cpu_freq and cpu_freq.min else "Unknown",
                    "max": f"{cpu_freq.max:.2f} MHz" if cpu_freq and cpu_freq.max else "Unknown",
                },
                "usage": {
                    "overall": f"{cpu_percent:.1f}%",
                    "user": f"{cpu_times.user / sum(cpu_times) * 100:.1f}%",
                    "system": f"{cpu_times.system / sum(cpu_times) * 100:.1f}%",
                    "idle": f"{cpu_times.idle / sum(cpu_times) * 100:.1f}%",
                },
                "temperature": temp,
                "load_average": [f"{load:.2f}" for load in load_avg],
            }
        except Exception as e:
            return {"error": f"Failed to get CPU info: {str(e)}"}

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information including RAM and swap details"""
        try:
            # Virtual memory (RAM)
            mem = psutil.virtual_memory()
            
            # Swap memory
            swap = psutil.swap_memory()
            
            return {
                "total": f"{mem.total / 1024**3:.2f} GB",
                "used": f"{mem.used / 1024**3:.2f} GB",
                "available": f"{mem.available / 1024**3:.2f} GB",
                "free": f"{mem.free / 1024**3:.2f} GB",
                "usage_percent": f"{mem.percent:.1f}%",
                "swap": {
                    "total": f"{swap.total / 1024**3:.2f} GB",
                    "used": f"{swap.used / 1024**3:.2f} GB",
                    "free": f"{swap.free / 1024**3:.2f} GB",
                    "usage_percent": f"{swap.percent:.1f}%",
                },
            }
        except Exception as e:
            return {"error": f"Failed to get memory info: {str(e)}"}

    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """Get disk usage information for all mounted drives and filesystems"""
        try:
            disks = []
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": f"{usage.total / 1024**3:.2f} GB",
                        "used": f"{usage.used / 1024**3:.2f} GB",
                        "free": f"{usage.free / 1024**3:.2f} GB",
                        "usage_percent": f"{(usage.used / usage.total * 100):.1f}%",
                    })
                except (PermissionError, OSError):
                    # Skip inaccessible drives
                    continue
            
            return disks
        except Exception as e:
            return [{"error": f"Failed to get disk usage: {str(e)}"}]

    def get_running_processes(self, limit: int = 20, sort_by: str = "cpu") -> Dict[str, Any]:
        """Get list of currently running processes with CPU and memory usage
        
        Args:
            limit: Maximum number of processes to return (default: 20)
            sort_by: Sort processes by 'cpu', 'memory', or 'name' (default: 'cpu')
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'username']):
                try:
                    pinfo = proc.info
                    pinfo['cpu_percent'] = proc.cpu_percent()
                    pinfo['memory_mb'] = pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == "memory":
                processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x.get('name', '').lower())
            else:  # cpu
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Limit results
            limited_processes = processes[:limit]
            
            # Format for output
            formatted_processes = []
            for proc in limited_processes:
                formatted_processes.append({
                    "pid": proc.get('pid', 'N/A'),
                    "name": proc.get('name', 'N/A'),
                    "cpu_percent": f"{proc.get('cpu_percent', 0):.1f}%",
                    "memory_percent": f"{proc.get('memory_percent', 0):.1f}%",
                    "memory_mb": f"{proc.get('memory_mb', 0):.1f} MB",
                    "status": proc.get('status', 'N/A'),
                    "username": proc.get('username', 'N/A'),
                    "started": datetime.fromtimestamp(proc.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if proc.get('create_time') else 'N/A',
                })
            
            return {
                "summary": {
                    "total_processes": len(processes),
                    "shown_processes": len(formatted_processes),
                    "sorted_by": sort_by,
                },
                "processes": formatted_processes,
            }
        except Exception as e:
            return {"error": f"Failed to get process info: {str(e)}"}

    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information including OS, uptime, hardware details"""
        try:
            # System information
            uname = platform.uname()
            boot_time = psutil.boot_time()
            uptime_seconds = psutil.time.time() - boot_time
            
            # Calculate uptime
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                "operating_system": {
                    "system": uname.system,
                    "release": uname.release,
                    "version": uname.version,
                    "machine": uname.machine,
                    "processor": uname.processor,
                },
                "hostname": uname.node,
                "uptime": f"{days}d {hours}h {minutes}m",
                "boot_time": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
                "users": [
                    {
                        "name": user.name,
                        "terminal": user.terminal,
                        "host": user.host,
                        "started": datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    for user in psutil.users()
                ],
                "python_version": platform.python_version(),
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {str(e)}"}

    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information, connections, and statistics"""
        try:
            # Network interfaces
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addresses in net_if_addrs.items():
                interface_info = {
                    "name": interface_name,
                    "addresses": [],
                    "is_up": net_if_stats[interface_name].isup if interface_name in net_if_stats else False,
                    "speed": f"{net_if_stats[interface_name].speed} Mbps" if interface_name in net_if_stats and net_if_stats[interface_name].speed > 0 else "Unknown",
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    })
                
                interfaces.append(interface_info)
            
            # Network connections
            try:
                connections = psutil.net_connections()
                connection_summary = {
                    "total": len(connections),
                    "tcp": len([c for c in connections if c.type.name == 'SOCK_STREAM']),
                    "udp": len([c for c in connections if c.type.name == 'SOCK_DGRAM']),
                    "listening": len([c for c in connections if c.status == 'LISTEN']),
                    "established": len([c for c in connections if c.status == 'ESTABLISHED']),
                }
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                connection_summary = {"error": "Access denied to connection information"}
            
            return {
                "interfaces": interfaces,
                "connections": connection_summary,
            }
        except Exception as e:
            return {"error": f"Failed to get network info: {str(e)}"}

    def run(self):
        """Run the MCP server"""
        self.mcp.run()

def test_server():
    """Test all server functions"""
    print("🧪 Testing System Info MCP Server (Python)...")
    
    server = SystemInfoServer()
    
    # Test each tool
    tools = [
        ("⚡ Quick Stats", server.get_quick_stats),
        ("📊 CPU Information", server.get_cpu_info),
        ("💾 Memory Information", server.get_memory_info),
        ("💿 Disk Usage", server.get_disk_usage),
        ("🔄 Running Processes (top 5)", lambda: server.get_running_processes(limit=5)),
        ("🖥️  System Information", server.get_system_info),
        ("🌐 Network Information", server.get_network_info),
    ]
    
    for name, func in tools:
        try:
            print(f"{name}:")
            result = func()
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            print()
    
    print("✅ All tests completed!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="System Info MCP Server")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    
    if args.test:
        test_server()
    else:
        server = SystemInfoServer()
        server.run()

if __name__ == "__main__":
    main()