# Autodesk Inventor — Part Design Skill

This skill defines the parameter structure, validation constraints, and execution requirements for Autodesk Inventor part operations.

## Supported Operations (Phase 1)

### `inventor.create_box`
Creates a parametric 3D rectangular box/cube feature in Autodesk Inventor.

#### Parameters:
- `length_mm` (float, required): Dimension along X axis (e.g. 30.0)
- `width_mm` (float, required): Dimension along Y axis (e.g. 30.0)
- `height_mm` (float, required): Dimension along Z axis (extrusion distance, e.g. 30.0)
- `centered` (boolean, optional): Whether to center the sketch on the coordinate origin. Default `true`.

#### Validation Rules:
- All dimensions must be strictly positive (> 0.001 mm and < 50000.0 mm).
- Normalization from other units (cm, m, inch, ft) must be computed precisely.

#### Example Structured Output:
```json
{
  "tool": "inventor.create_box",
  "parameters": {
    "length_mm": 30.0,
    "width_mm": 30.0,
    "height_mm": 30.0,
    "centered": true
  }
}
```
