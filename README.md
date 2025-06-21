# System Info MCP Server

[![npm version](https://badge.fury.io/js/%40system-info%2Fmcp-server.svg)](https://badge.fury.io/js/%40system-info%2Fmcp-server)
[![PyPI version](https://badge.fury.io/py/system-info-mcp-server.svg)](https://badge.fury.io/py/system-info-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides real-time system information. Available in both **Node.js** and **Python** with identical functionality.

## 🚀 Quick Start

Choose your preferred implementation:

### Option 1: Node.js with npx (Recommended)

```bash
# Test instantly
npx @system-info/mcp-server@latest --test
```

### Option 2: Python with pipx

```bash
# Test instantly  
pipx run system-info-mcp-server --test
```

Both work identically! Choose based on your preference.

## 🔧 Claude Desktop Configuration

### Node.js Implementation
```json
{
  "mcpServers": {
    "system-info": {
      "command": "npx",
      "args": ["@system-info/mcp-server@latest"]
    }
  }
}
```

### Python Implementation
```json
{
  "mcpServers": {
    "system-info": {
      "command": "pipx",
      "args": ["run", "system-info-mcp-server"]
    }
  }
}
```

### Config file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## ✨ Features (Both Implementations)

- **📊 CPU Information**: Usage, cores, frequency, temperature
- **💾 Memory Status**: RAM usage, swap, availability  
- **💿 Disk Usage**: Storage space across all drives
- **🔄 Process Management**: Running processes with sorting
- **🖥️ System Overview**: OS details, uptime, hardware
- **🌐 Network Information**: Interfaces, connections
- **🖥️ Monitor Detection**: Connected displays with resolution, refresh rate, and DPI
- **⚡ Quick Stats**: Instant system health overview

## 🎯 Which Should You Choose?

### Choose **Node.js** if:
- ✅ You want the fastest performance
- ✅ You prefer JavaScript/TypeScript
- ✅ You want minimal memory usage
- ✅ You work with npm ecosystem

### Choose **Python** if:
- ✅ You prefer Python
- ✅ You work with PyPI ecosystem  
- ✅ You want to extend with Python libraries
- ✅ You're comfortable with Python tooling

Both implementations are **functionally identical** and maintained in parallel.

## 📋 Usage Examples

Ask Claude any of these questions:

```
"What's my system status?"
"Show me CPU and memory usage"  
"What processes are using the most resources?"
"How much disk space is available?"
"What are my computer's specs?"
"List all network interfaces"
"What monitors are connected to my computer?"
"Show me my display setup and resolution"
"What's my monitor refresh rate?"
```

## 🖥️ Monitor Detection Features

The enhanced Python version now includes comprehensive monitor detection:

### Cross-Platform Support
- **Windows**: Uses WMI and PowerShell for detailed monitor information
- **macOS**: Uses system_profiler for display detection with Retina support
- **Linux**: Uses xrandr (X11) and sway (Wayland) for comprehensive coverage

### Detection Methods
- **Primary**: screeninfo library for cross-platform compatibility
- **Fallback**: Platform-specific commands for additional details
- **Hybrid**: Combines multiple sources for complete information

### Information Provided
- **Resolution**: Width and height in pixels
- **Position**: X, Y coordinates for multi-monitor setups
- **Refresh Rate**: Display refresh rate when available
- **DPI**: Calculated dots per inch (when physical dimensions available)
- **Manufacturer**: Monitor brand and model information
- **Connection Type**: HDMI, DisplayPort, VGA, etc.
- **Primary Display**: Identifies main monitor
- **Retina Detection**: macOS Retina display identification

## 🔧 Requirements

### Node.js Implementation
- **Node.js**: 18.0.0+
- **npx**: Included with npm

### Python Implementation  
- **Python**: 3.8+
- **pipx**: `pip install pipx`

### Claude
- **Claude Desktop**: 0.7.0+ (for MCP support)

## 🤝 Contributing

Contributions welcome for both implementations! Please:

1. Fork the repository
2. Choose your implementation (Node.js or Python)
3. Make changes in the appropriate directory
4. Ensure both implementations stay in sync
5. Add tests and update documentation
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file.