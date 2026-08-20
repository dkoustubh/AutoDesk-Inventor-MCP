# Core Engineering Skill — ATS Engineering AI

This skill provides system-level principles and rules for translating natural language engineering requests into structured, validated CAD tool calls.

## Core Rules

1. **Strict Unit Normalization**:
   - All geometric dimensions must be converted and normalized to millimeters (**mm**) unless explicitly specified otherwise.
   - Example: `3 cm` -> `30.0 mm`, `1.5 m` -> `1500.0 mm`, `2 inches` -> `50.8 mm`.

2. **Tool Call Structure**:
   - The model must output ONLY a structured JSON payload conforming to the active CAD tool definitions.
   - No arbitrary python scripts or unbounded shell commands are permitted.

3. **Supported CAD Applications**:
   - `inventor`: Autodesk Inventor (Parametric 3D solid modeling)
   - (Future: `fusion`, `autocad`, `vault`)

4. **Target Workstation Routing**:
   - Every execution request is associated with a specific engineer session and machine IP (e.g. `192.168.11.150`).
