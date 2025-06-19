#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import si from 'systeminformation';
import os from 'os';
import process from 'process';

/**
 * System Information MCP Server
 * Provides real-time system information tools for Claude Desktop
 */

class SystemInfoServer {
  constructor() {
    this.server = new Server(
      {
        name: 'system-info-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_cpu_info',
            description: 'Get detailed CPU information including usage, cores, frequency, and temperature',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_memory_info',
            description: 'Get memory usage information including RAM and swap details',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_disk_usage',
            description: 'Get disk usage information for all mounted drives and filesystems',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_running_processes',
            description: 'Get list of currently running processes with CPU and memory usage',
            inputSchema: {
              type: 'object',
              properties: {
                limit: {
                  type: 'number',
                  description: 'Maximum number of processes to return (default: 20)',
                  default: 20,
                },
                sort_by: {
                  type: 'string',
                  description: 'Sort processes by: cpu, memory, name (default: cpu)',
                  enum: ['cpu', 'memory', 'name'],
                  default: 'cpu',
                },
              },
              required: [],
            },
          },
          {
            name: 'get_system_info',
            description: 'Get general system information including OS, uptime, hardware details',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_network_info',
            description: 'Get network interface information, connections, and statistics',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_quick_stats',
            description: 'Get a quick overview of CPU, memory, and disk usage',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result;
        switch (name) {
          case 'get_cpu_info':
            result = await this.getCpuInfo();
            break;
          case 'get_memory_info':
            result = await this.getMemoryInfo();
            break;
          case 'get_disk_usage':
            result = await this.getDiskUsage();
            break;
          case 'get_running_processes':
            result = await this.getRunningProcesses(args?.limit, args?.sort_by);
            break;
          case 'get_system_info':
            result = await this.getSystemInfo();
            break;
          case 'get_network_info':
            result = await this.getNetworkInfo();
            break;
          case 'get_quick_stats':
            result = await this.getQuickStats();
            break;
          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: typeof result === 'string' ? result : JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async getCpuInfo() {
    const [cpu, currentLoad, temp] = await Promise.all([
      si.cpu(),
      si.currentLoad(),
      si.cpuTemperature().catch(() => ({ main: null })),
    ]);

    return {
      brand: cpu.brand,
      manufacturer: cpu.manufacturer,
      family: cpu.family,
      model: cpu.model,
      speed: `${cpu.speed} GHz`,
      cores: {
        physical: cpu.physicalCores,
        logical: cpu.cores,
      },
      architecture: cpu.arch || process.arch,
      usage: {
        overall: `${currentLoad.avgLoad.toFixed(1)}%`,
        user: `${currentLoad.currentLoadUser.toFixed(1)}%`,
        system: `${currentLoad.currentLoadSystem.toFixed(1)}%`,
        idle: `${currentLoad.currentLoadIdle.toFixed(1)}%`,
      },
      temperature: temp.main ? `${temp.main}°C` : 'Not available',
      load_average: os.loadavg().map(load => load.toFixed(2)),
    };
  }

  async getMemoryInfo() {
    const mem = await si.mem();
    const totalGB = (mem.total / 1024 / 1024 / 1024).toFixed(2);
    const usedGB = (mem.used / 1024 / 1024 / 1024).toFixed(2);
    const freeGB = (mem.free / 1024 / 1024 / 1024).toFixed(2);
    const availableGB = (mem.available / 1024 / 1024 / 1024).toFixed(2);

    return {
      total: `${totalGB} GB`,
      used: `${usedGB} GB`,
      free: `${freeGB} GB`,
      available: `${availableGB} GB`,
      usage_percent: `${((mem.used / mem.total) * 100).toFixed(1)}%`,
      swap: {
        total: `${(mem.swaptotal / 1024 / 1024 / 1024).toFixed(2)} GB`,
        used: `${(mem.swapused / 1024 / 1024 / 1024).toFixed(2)} GB`,
        free: `${(mem.swapfree / 1024 / 1024 / 1024).toFixed(2)} GB`,
      },
    };
  }

  async getDiskUsage() {
    const disks = await si.fsSize();
    
    return disks.map(disk => ({
      filesystem: disk.fs,
      mount_point: disk.mount,
      total: `${(disk.size / 1024 / 1024 / 1024).toFixed(2)} GB`,
      used: `${(disk.used / 1024 / 1024 / 1024).toFixed(2)} GB`,
      available: `${(disk.available / 1024 / 1024 / 1024).toFixed(2)} GB`,
      usage_percent: `${disk.use.toFixed(1)}%`,
      type: disk.type,
    }));
  }

  async getRunningProcesses(limit = 20, sortBy = 'cpu') {
    const processes = await si.processes();
    
    let sortedProcs = processes.list;
    
    // Sort processes
    switch (sortBy) {
      case 'memory':
        sortedProcs.sort((a, b) => b.memRss - a.memRss);
        break;
      case 'name':
        sortedProcs.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'cpu':
      default:
        sortedProcs.sort((a, b) => b.cpu - a.cpu);
        break;
    }

    return {
      summary: {
        total_processes: processes.all,
        running: processes.running,
        sleeping: processes.sleeping,
        blocked: processes.blocked || 0,
      },
      processes: sortedProcs.slice(0, limit).map(proc => ({
        pid: proc.pid,
        name: proc.name,
        cpu_percent: `${proc.cpu.toFixed(1)}%`,
        memory_mb: `${(proc.memRss / 1024 / 1024).toFixed(1)} MB`,
        memory_percent: `${proc.memVss ? ((proc.memVss / os.totalmem()) * 100).toFixed(1) : '0.0'}%`,
        status: proc.state,
        started: proc.started,
        user: proc.user || 'N/A',
      })),
    };
  }

  async getSystemInfo() {
    const [osInfo, system, uuid, versions] = await Promise.all([
      si.osInfo(),
      si.system(),
      si.uuid().catch(() => ({ hardware: 'N/A' })),
      si.versions(),
    ]);

    const uptimeSeconds = os.uptime();
    const uptimeDays = Math.floor(uptimeSeconds / 86400);
    const uptimeHours = Math.floor((uptimeSeconds % 86400) / 3600);
    const uptimeMinutes = Math.floor((uptimeSeconds % 3600) / 60);

    return {
      operating_system: {
        platform: osInfo.platform,
        distro: osInfo.distro,
        release: osInfo.release,
        codename: osInfo.codename || 'N/A',
        kernel: osInfo.kernel,
        arch: osInfo.arch,
      },
      hardware: {
        manufacturer: system.manufacturer || 'N/A',
        model: system.model || 'N/A',
        version: system.version || 'N/A',
        serial: system.serial || 'N/A',
        uuid: uuid.hardware || 'N/A',
      },
      uptime: `${uptimeDays}d ${uptimeHours}h ${uptimeMinutes}m`,
      hostname: os.hostname(),
      user: os.userInfo().username,
      node_version: process.version,
      versions: {
        node: versions.node || process.version,
        npm: versions.npm || 'N/A',
        v8: process.versions.v8 || 'N/A',
      },
    };
  }

  async getNetworkInfo() {
    const [interfaces, connections] = await Promise.all([
      si.networkInterfaces(),
      si.networkConnections().catch(() => []),
    ]);

    return {
      interfaces: interfaces.map(iface => ({
        name: iface.iface,
        type: iface.type,
        ip4: iface.ip4 || 'N/A',
        ip6: iface.ip6 || 'N/A',
        mac: iface.mac,
        internal: iface.internal,
        virtual: iface.virtual,
        speed: iface.speed ? `${iface.speed} Mbps` : 'Unknown',
      })),
      connections: {
        total: connections.length,
        tcp: connections.filter(c => c.protocol === 'tcp').length,
        udp: connections.filter(c => c.protocol === 'udp').length,
        listening: connections.filter(c => c.state === 'listen').length,
        established: connections.filter(c => c.state === 'established').length,
      },
    };
  }

  async getQuickStats() {
    const [cpu, mem, disks] = await Promise.all([
      si.currentLoad(),
      si.mem(),
      si.fsSize(),
    ]);

    const mainDisk = disks.find(d => d.mount === '/') || disks[0];

    return {
      cpu_usage: `${cpu.avgLoad.toFixed(1)}%`,
      memory: {
        usage: `${((mem.used / mem.total) * 100).toFixed(1)}%`,
        used: `${(mem.used / 1024 / 1024 / 1024).toFixed(1)} GB`,
        total: `${(mem.total / 1024 / 1024 / 1024).toFixed(1)} GB`,
      },
      disk: mainDisk ? {
        usage: `${mainDisk.use.toFixed(1)}%`,
        used: `${(mainDisk.used / 1024 / 1024 / 1024).toFixed(1)} GB`,
        total: `${(mainDisk.size / 1024 / 1024 / 1024).toFixed(1)} GB`,
        mount: mainDisk.mount,
      } : 'N/A',
      uptime: `${Math.floor(os.uptime() / 86400)}d ${Math.floor((os.uptime() % 86400) / 3600)}h`,
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('System Info MCP Server running on stdio');
  }
}

// Test mode for development
async function runTest() {
  console.log('🧪 Testing System Info MCP Server...');
  
  const server = new SystemInfoServer();
  
  try {
    console.log('⚡ Quick Stats:');
    console.log(JSON.stringify(await server.getQuickStats(), null, 2));
    
    console.log('📊 CPU Information:');
    console.log(JSON.stringify(await server.getCpuInfo(), null, 2));
    
    console.log('💾 Memory Information:');
    console.log(JSON.stringify(await server.getMemoryInfo(), null, 2));
    
    console.log('💿 Disk Usage:');
    console.log(JSON.stringify(await server.getDiskUsage(), null, 2));
    
    console.log('🔄 Running Processes (top 5):');
    console.log(JSON.stringify(await server.getRunningProcesses(5), null, 2));
    
    console.log('🖥️  System Information:');
    console.log(JSON.stringify(await server.getSystemInfo(), null, 2));
    
    console.log('🌐 Network Information:');
    console.log(JSON.stringify(await server.getNetworkInfo(), null, 2));
    
    console.log('✅ All tests completed successfully!');
  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }
}

// Main execution
if (process.argv.includes('--test')) {
  runTest();
} else {
  const server = new SystemInfoServer();
  server.run().catch(console.error);
}