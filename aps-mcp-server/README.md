# Autodesk Platform Services (APS) & Inventor MCP Server (Node.js)

Official Node.js / TypeScript implementation of the **Model Context Protocol (MCP)** server for Autodesk Platform Services and Autodesk Inventor, conforming to the [Autodesk APS MCP Reference Architecture](https://autodesk-platform-services.github.io/aps-mcp-server-nodejs/).

---

## 🚀 Features & Tools

- **`inventor_create_box`**: Generates 3D solid boxes, plates, and cubes.
- **`inventor_create_cone`**: Generates 3D solid cones and frustums.
- **`inventor_create_rhombus`**: Generates 3D rhombus and diamond prisms.
- **`inventor_create_sprocket`**: Generates mechanical sprockets, gears, and cogwheels.
- **`inventor_create_compound`**: Generates multi-feature assemblies (e.g., stacked cubes).
- **`aps_create_bucket`**: Data Management API bucket provisioning.
- **`aps_translate_model`**: Model Derivative API translation (SVF2) for interactive 3D WebGL viewing.

---

## 🛠️ Installation & Build

```bash
cd aps-mcp-server
npm install
npm run build
```

---

## ⚙️ Configuration

### 1. Claude Desktop (`claude_desktop_config.json`)

On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "autodesk-aps": {
      "command": "node",
      "args": ["/Users/admin/Desktop/AutoDesk Integration/aps-mcp-server/dist/index.js"],
      "env": {
        "CAD_GATEWAY_URL": "http://192.168.11.94:8005",
        "WORKSTATION_IP": "192.168.11.150"
      }
    }
  }
}
```

### 2. Cursor IDE (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "autodesk-aps": {
      "command": "node",
      "args": ["./aps-mcp-server/dist/index.js"],
      "env": {
        "CAD_GATEWAY_URL": "http://192.168.11.94:8005",
        "WORKSTATION_IP": "192.168.11.150"
      }
    }
  }
}
```

### 3. Open WebUI (`192.168.11.86:8081`)

Use the tool connector in `openwebui-tools/autodesk_inventor_tools.py` in your Open WebUI Workspace ➔ Tools.
