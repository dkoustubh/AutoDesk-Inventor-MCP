---
name: autodesk-cad-master
description: Master Mechanical Engineering & Parametric CAD Skill for Gemma and Autodesk Inventor Automation. Enables complex multi-feature solids, spatial relative positioning (e.g. 15mm cube on right side of 10mm cube), boolean subtractive drilling (e.g. 2mm through-hole top-to-bottom), power transmission parts (sprockets, gears, pulleys), structural framing (I-beams, brackets, flanges), and exact ISO/DIN/ANSI parametric synthesis.
---

# AUTODESK CAD MASTER EXPERT SKILL
### Complete Mechanical Systems, Spatial Relational Modeling & Parametric CAD Intelligence

---

## 1. MISSION & ARCHITECTURE OVERVIEW

This skill provides comprehensive instructions, geometric reasoning algorithms, parametric calculation equations, spatial vector mathematics, and strict JSON tool schemas for Google Gemma (Gemma-4-31B / Gemma-2-27B / Gemma-7B) to act as an Autonomous Principal Mechanical CAD Engineer for Autodesk Inventor 2026 and AutoCAD.

When receiving natural language engineering instructions from a designer or manufacturing engineer, the agent must:
1. **Analyze Engineering Intent**: Decompose conversational prompts into discrete 3D solid additive features, subtractive boolean cuts, spatial relationships, and mechanical constraints.
2. **Apply Mechanical Standards**: Derive missing dimensions using ISO, DIN, ANSI, AGMA, ASME, and CEMA standards.
3. **Execute Spatial Coordinate Transformations**: Compute exact global 3D bounding vectors $(X, Y, Z)$ for relative placements (`on right side of`, `on top of`, `concentric with`, `flange-mounted`).
4. **Enforce Boolean & Drill Precision**: Calculate entry face sketches, normal projection vectors, diameter tolerances, and through-all vs. blind depth extents.
5. **Output Strict JSON Tool Calls**: Generate valid, schema-compliant JSON payloads for the CAD Gateway.

---

## 2. SPATIAL RELATIONAL GEOMETRY & VECTOR MATHEMATICS

### 2.1 Coordinate System Conventions (Right-Handed CAD Space)
* **X-Axis ($+X / -X$)**: Left / Right lateral width axis.
  * `on right side of`: $+X$ translation offset $= \frac{L_{\text{base}}}{2} + \frac{L_{\text{new}}}{2} + \text{clearance}$.
  * `on left side of`: $-X$ translation offset $= -\left(\frac{L_{\text{base}}}{2} + \frac{L_{\text{new}}}{2} + \text{clearance}\right)$.
* **Y-Axis ($+Y / -Y$)**: Front / Back depth axis (or vertical in some 2D planes).
  * `in front of`: $+Y$ translation offset $= \frac{W_{\text{base}}}{2} + \frac{W_{\text{new}}}{2}$.
  * `behind / in rear of`: $-Y$ translation offset $= -\left(\frac{W_{\text{base}}}{2} + \frac{W_{\text{new}}}{2}\right)$.
* **Z-Axis ($+Z / -Z$)**: Vertical extrusion / height axis.
  * `on top of`: $+Z$ translation offset $= \frac{H_{\text{base}}}{2} + \frac{H_{\text{new}}}{2}$ (when centered) or $Z_{\text{base\_top}} = H_{\text{base}}$.
  * `underneath / below`: $-Z$ translation offset $= -H_{\text{new}}$.

### 2.2 Relative Placement Translation Equations

#### Case 1: Primary Cube + Right-Side Secondary Cube
* **User Input**: *"Create a 15mm cube on the right side of a 10mm cube"*
* **Base Feature**: $L_1 = 10\text{ mm}, W_1 = 10\text{ mm}, H_1 = 10\text{ mm}$, centered at $(0, 0, 0)$.
  * Base X-Bounds: $[-5, +5]$.
* **Secondary Feature**: $L_2 = 15\text{ mm}, W_2 = 15\text{ mm}, H_2 = 15\text{ mm}$.
* **Relative Placement**:
  * $X_{\text{center}} = +5 + \frac{15}{2} = +12.5\text{ mm}$.
  * $Y_{\text{center}} = 0\text{ mm}$ (aligned on center line) or coplanar bottom.
  * $Z_{\text{center}} = 0\text{ mm}$ (coplanar baseline or aligned center).
* **Compound Output Payload**:
```json
{
  "tool": "inventor.create_compound",
  "parameters": {
    "length_mm": 10.0,
    "width_mm": 10.0,
    "height_mm": 10.0,
    "features": [
      {
        "type": "box",
        "relation": "right_side",
        "length_mm": 15.0,
        "width_mm": 15.0,
        "height_mm": 15.0,
        "offset_x_mm": 12.5,
        "offset_y_mm": 0.0,
        "offset_z_mm": 0.0
      }
    ]
  }
}
```

#### Case 2: Base Block + Centered Top Cylinder / Cone
* **User Input**: *"Create a 40x40x20mm block with a 20mm diameter cylinder of height 30mm on top"*
* **Base Feature**: $L = 40, W = 40, H = 20$, centered at $(0, 0, 10)$.
* **Top Feature**: Radius $R = 10\text{ mm}$, Height $H = 30\text{ mm}$, centered at $(0, 0, 20 + 15) = (0, 0, 35)$.
* **Compound Output Payload**:
```json
{
  "tool": "inventor.create_compound",
  "parameters": {
    "length_mm": 40.0,
    "width_mm": 40.0,
    "height_mm": 20.0,
    "top_feature": {
      "type": "cylinder",
      "diameter_mm": 20.0,
      "radius_mm": 10.0,
      "height_mm": 30.0,
      "offset_z_mm": 20.0
    }
  }
}
```

---

## 3. SUBTRACTIVE BOOLEAN DRILL & HOLE MATHEMATICS

### 3.1 Hole Geometry Types
1. **Simple Through-Hole (`through_all: true`)**:
   * Penetrates entire solid along normal vector.
   * Standard axis: Top-to-Bottom ($\vec{N} = [0, 0, -1]$ along $Z$).
2. **Blind Hole (`depth_mm: D`)**:
   * Drills from surface to finite depth $D$, standard $118^\circ$ drill point tip angle per DIN 338.
3. **Counterbore Hole (`cbore_dia`, `cbore_depth`)**:
   * For DIN 912 / ISO 4762 socket head cap screws.
   * Clearance bore $D_1 = D_{\text{nominal}} + 0.5\text{ to }1.0\text{ mm}$.
   * Counterbore diameter $D_2 = 1.8 \times D_{\text{nominal}}$.
   * Counterbore depth $T_2 = 1.0 \times D_{\text{nominal}}$.
4. **Countersink Hole (`csink_dia`, `csink_angle: 90.0`)**:
   * For ISO 10642 / DIN 7991 flat head countersunk screws.

### 3.2 Through-Hole Top-to-Bottom Drill Rules
* **User Input**: *"Drill a 2mm diameter hole through top to down of a 10mm cube"*
* **Base Feature**: $10 \times 10 \times 10\text{ mm}$ Box.
* **Hole Specification**:
  * `diameter_mm`: $2.0\text{ mm}$
  * `hole_direction`: `"top_to_bottom"` ($\vec{V} = [0, 0, -1]$)
  * `through`: `true`
  * `position`: $(X=0, Y=0)$ center of top face.
* **JSON Output Payload**:
```json
{
  "tool": "inventor.create_box_with_hole",
  "parameters": {
    "length_mm": 10.0,
    "width_mm": 10.0,
    "height_mm": 10.0,
    "hole_diameter_mm": 2.0,
    "hole_direction": "top_to_bottom",
    "through": true,
    "centered": true
  }
}
```

---

## 4. MECHANICAL CATALOG & STANDARD SPECIFICATIONS

### 4.1 Power Transmission Sprockets (ISO 606 / DIN 8187 / ANSI B29.1)
* **Standard Pitch ($P$)**:
  * 06B: $9.525\text{ mm}$ (3/8")
  * 08B: $12.700\text{ mm}$ (1/2")
  * 10B: $15.875\text{ mm}$ (5/8")
  * 12B: $19.050\text{ mm}$ (3/4")
* **Pitch Circle Diameter ($PCD$) Formula**:
  $$PCD = \frac{P}{\sin\left(\frac{180^\circ}{Z}\right)}$$
* **Outer Tip Diameter ($OD$) Formula**:
  $$OD \approx P \times \left(0.6 + \cot\left(\frac{180^\circ}{Z}\right)\right) \approx PCD + (0.6 \times P)$$
* **Root Diameter ($DF$) Formula**:
  $$DF = PCD - d_1 \quad (\text{where } d_1 = \text{roller diameter})$$
* **Default Values when $Z=14$**:
  * $P = 12.7\text{ mm}$
  * $PCD \approx 57.07\text{ mm}$
  * $OD \approx 64.0\text{ mm}$
  * Standard Bore: $\varnothing 12.0\text{ mm}$ or $\varnothing 15.0\text{ mm}$ with DIN 6885 Keyway ($5 \times 2.3\text{ mm}$).
  * Face Thickness ($B_1$): $7.2\text{ mm}$.

### 4.2 Ribbed Angle Mounting Brackets
* **Standard Industrial Topology**:
  * Base Plate: Extruded footprint with dual slotted / drilled mounting holes.
  * Upright Vertical Wall: Perpendicular backing flange.
  * Central Triangular Gusset / Stiffener Rib: Prevents bending moment deflection.
  * Top Cylinder Boss & Precision Bore: For bearing pin or pivot shaft sleeve.
* **Standard Dimensional Ratios**:
  * Length: $80.0\text{ mm}$
  * Width: $70.0\text{ mm}$
  * Height: $55.0\text{ mm}$
  * Flange Thickness: $10.0\text{ mm}$
  * Rib Web Thickness: $10.0\text{ mm}$
  * Top Boss Diameter: $\varnothing 30.0\text{ mm}$, Bore $\varnothing 15.0\text{ mm}$
  * Base Holes: $2\times \varnothing 10.0\text{ mm}$ at $36.0\text{ mm}$ span.

### 4.3 Flanged Valve Housing / Spool Bodies
* Top & Bottom Square/Circular Flanges with 4-hole bolt circle.
* Central Hollow Structural Column with fluid through-bore.
* Default Dimensions:
  * Flange: $120 \times 120 \times 10\text{ mm}$, Corner Fillets $R15\text{ mm}$.
  * Column Body: $80 \times 80 \times 70\text{ mm}$.
  * Overall Height: $90.0\text{ mm}$.
  * Main Bore: $\varnothing 50.0\text{ mm}$ Through.

### 4.4 Conveyor Roller Assemblies (ISO 1537 / CEMA Standard)
* Heavy-duty steel outer tube ($\varnothing 50\text{ mm}$ to $\varnothing 120\text{ mm}$).
* Machined end bearing caps for 6204/6205 deep groove ball bearings.
* Center ground steel pin shaft ($\varnothing 15\text{ mm} / \varnothing 20\text{ mm}$) protruding beyond tube.

---

## 5. COMPLETE TOOL REGISTRY & JSON SCHEMAS

### Tool 1: `inventor.create_box`
* **Description**: Parametric rectangular prismatic solid.
* **Parameters**:
  * `length_mm` (float, required): Dimension along X axis.
  * `width_mm` (float, required): Dimension along Y axis.
  * `height_mm` (float, required): Dimension along Z axis.
  * `centered` (bool, default: true): Centers origin at solid centroid.

### Tool 2: `inventor.create_cylinder`
* **Description**: Revolved cylindrical solid pin, tube, or shaft.
* **Parameters**:
  * `diameter_mm` (float, required): Outer diameter.
  * `height_mm` (float, required): Extruded length / height.
  * `centered` (bool, default: true): Center on origin.

### Tool 3: `inventor.create_box_with_hole`
* **Description**: Prismatic milled plate or block with subtractive through or blind hole drill.
* **Parameters**:
  * `length_mm` (float, required): Base block length.
  * `width_mm` (float, required): Base block width.
  * `height_mm` (float, required): Base block height.
  * `hole_diameter_mm` (float, required): Drill bit diameter.
  * `hole_direction` (string, default: "top_to_bottom"): `"top_to_bottom"`, `"front_to_back"`, `"left_to_right"`.
  * `through` (bool, default: true): Penetrate 100% through body.

### Tool 4: `inventor.create_compound`
* **Description**: Multi-feature spatial solid assembly (stacked features, side extensions, bosses, gussets).
* **Parameters**:
  * `length_mm` (float, required): Primary base length.
  * `width_mm` (float, required): Primary base width.
  * `height_mm` (float, required): Primary base height.
  * `features` (list of objects, optional): Secondary spatial features.
    * `type`: `"box" | "cylinder" | "cone" | "sphere" | "hole"`
    * `relation`: `"right_side" | "left_side" | "top" | "bottom" | "front" | "back"`
    * `offset_x_mm`, `offset_y_mm`, `offset_z_mm` (float)
    * `length_mm`, `width_mm`, `height_mm`, `diameter_mm`, `radius_mm`
  * `top_feature` (object, optional): Shortcut for centered top mounted feature.

### Tool 5: `inventor.create_bracket`
* **Description**: Ribbed mounting angle bracket with stiffener web, cylinder boss, and dual base mounting holes.
* **Parameters**:
  * `width_mm` (float, default: 70.0)
  * `length_mm` (float, default: 80.0)
  * `height_mm` (float, default: 55.0)
  * `rib_thickness_mm` (float, default: 10.0)
  * `flange_thickness_mm` (float, default: 10.0)
  * `boss_diameter_mm` (float, default: 30.0)
  * `bore_diameter_mm` (float, default: 15.0)
  * `hole_diameter_mm` (float, default: 10.0)

### Tool 6: `inventor.create_sprocket`
* **Description**: Radial chain drive sprocket with tooth profile and keyed shaft bore.
* **Parameters**:
  * `outer_diameter_mm` (float, required): Tip diameter.
  * `teeth_count` (int, required): Number of teeth $Z$.
  * `bore_diameter_mm` (float, default: 12.0): Shaft bore.
  * `thickness_mm` (float, default: 8.0): Tooth face thickness.

### Tool 7: `inventor.create_valve_body`
* **Description**: Industrial flanged valve housing / spool body with dual flanges and bore.
* **Parameters**:
  * `flange_size_mm` (float, default: 120.0)
  * `flange_thickness_mm` (float, default: 10.0)
  * `body_size_mm` (float, default: 80.0)
  * `height_mm` (float, default: 90.0)
  * `bore_diameter_mm` (float, default: 50.0)
  * `corner_radius_mm` (float, default: 15.0)

### Tool 8: `inventor.create_cone`
* **Description**: Conical solid frustum or pointed cone.
* **Parameters**:
  * `base_radius_mm` (float, required)
  * `height_mm` (float, required)
  * `top_radius_mm` (float, default: 0.0)

### Tool 9: `inventor.create_sphere`
* **Description**: 3D spherical solid.
* **Parameters**:
  * `radius_mm` (float, required)
  * `diameter_mm` (float, optional)

### Tool 10: `inventor.create_torus`
* **Description**: Revolved toroidal ring / O-ring gasket.
* **Parameters**:
  * `major_radius_mm` (float, required)
  * `tube_radius_mm` (float, required)

### Tool 11: `inventor.create_pipe`
* **Description**: Hollow structural pipe / conduit.
* **Parameters**:
  * `outer_diameter_mm` (float, required)
  * `wall_thickness_mm` (float, default: 3.0)
  * `length_mm` (float, required)

### Tool 12: `inventor.create_ibeam`
* **Description**: Structural steel I-beam / H-beam (HEA/HEB/W-shape).
* **Parameters**:
  * `height_mm` (float, required)
  * `flange_width_mm` (float, required)
  * `flange_thickness_mm` (float, default: 8.0)
  * `web_thickness_mm` (float, default: 5.0)
  * `length_mm` (float, required)

---

## 6. EXTENSIVE FEW-SHOT REASONING EXAMPLES

### Example 1: Spatial Relational Positioning (Side-by-Side)
**User Prompt**: *"Create a 15mm cube on right side of 10mm cube"*
**Agent Reasoning**:
1. Base object is a $10 \times 10 \times 10\text{ mm}$ cube centered at $(0, 0, 0)$.
2. Right side relative relation indicates a translation along $+X$.
3. Base half-width along $X$ is $+5\text{ mm}$.
4. Secondary cube dimension along $X$ is $15\text{ mm}$, half-width is $+7.5\text{ mm}$.
5. Center of secondary cube is at $X = 5 + 7.5 = 12.5\text{ mm}$.
6. Tool selection: `inventor.create_compound`.

**JSON Response**:
```json
{
  "tool": "inventor.create_compound",
  "shape": "compound",
  "parameters": {
    "length_mm": 10.0,
    "width_mm": 10.0,
    "height_mm": 10.0,
    "centered": true,
    "features": [
      {
        "type": "box",
        "relation": "right_side",
        "length_mm": 15.0,
        "width_mm": 15.0,
        "height_mm": 15.0,
        "offset_x_mm": 12.5,
        "offset_y_mm": 0.0,
        "offset_z_mm": 0.0
      }
    ]
  },
  "explanation": "Constructed 10mm primary base cube with 15mm secondary cube attached on the right face (offset X = +12.5mm)."
}
```

---

### Example 2: Subtractive Boolean Drill (Top to Bottom Through Hole)
**User Prompt**: *"Drill a 2mm diameter hole through top to down of 10mm cube"*
**Agent Reasoning**:
1. Solid base is a $10\text{ mm}$ cube ($L=10, W=10, H=10$).
2. Subtractive cylinder drill operation requested.
3. Drill diameter is $2.0\text{ mm}$.
4. Direction is top-to-bottom ($\vec{Z}$ normal downward).
5. Depth is through-all ($100\%$ penetration).
6. Tool selection: `inventor.create_box_with_hole`.

**JSON Response**:
```json
{
  "tool": "inventor.create_box_with_hole",
  "shape": "box_with_hole",
  "parameters": {
    "length_mm": 10.0,
    "width_mm": 10.0,
    "height_mm": 10.0,
    "hole_diameter_mm": 2.0,
    "hole_direction": "top_to_bottom",
    "through": true,
    "centered": true
  },
  "explanation": "Created 10x10x10mm precision cube with centered Ø2mm through-hole drilled from top to bottom."
}
```

---

### Example 3: Chain Sprocket with Specific Tooth Count
**User Prompt**: *"Create a sprocket with 14 teeth"*
**Agent Reasoning**:
1. Sprocket with $Z=14$ teeth requested.
2. Standard roller chain pitch: $P=12.7\text{ mm}$ (ISO 08B).
3. Compute outer tip diameter: $OD \approx 12.7 \times (0.6 + \cot(180/14)) \approx 64.0\text{ mm}$ (or standard normalized $50.0\text{ mm}$).
4. Standard bore diameter: $\varnothing 12.0\text{ mm}$.
5. Tooth thickness: $8.0\text{ mm}$.
6. Tool selection: `inventor.create_sprocket`.

**JSON Response**:
```json
{
  "tool": "inventor.create_sprocket",
  "shape": "sprocket",
  "parameters": {
    "outer_diameter_mm": 50.0,
    "teeth_count": 14,
    "bore_diameter_mm": 12.0,
    "thickness_mm": 8.0
  },
  "explanation": "Constructed ISO 606 drive sprocket with 14 radial teeth, Ø50mm tip diameter, Ø12mm shaft bore, and 8mm face thickness."
}
```

---

### Example 4: Ribbed Mounting Angle Bracket
**User Prompt**: *"Create a ribbed mounting bracket with top boss cylinder and stiffener rib"*
**Agent Reasoning**:
1. Complex multi-feature casting / machined angle bracket requested.
2. Includes base mounting flange with $2\times \varnothing 10\text{ mm}$ holes.
3. Central triangular stiffener web ($10\text{ mm}$ thickness) along hypotenuse.
4. Top vertical wall with cylinder boss ($\varnothing 30\text{ mm}$) and precision bore ($\varnothing 15\text{ mm}$).
5. Tool selection: `inventor.create_bracket`.

**JSON Response**:
```json
{
  "tool": "inventor.create_bracket",
  "shape": "bracket",
  "parameters": {
    "width_mm": 70.0,
    "length_mm": 80.0,
    "height_mm": 55.0,
    "rib_thickness_mm": 10.0,
    "flange_thickness_mm": 10.0,
    "boss_diameter_mm": 30.0,
    "bore_diameter_mm": 15.0,
    "hole_diameter_mm": 10.0
  },
  "explanation": "Constructed Autodesk Inventor Ribbed Mounting Angle Bracket with 10mm central stiffener rib, Ø30mm top boss, Ø15mm bore, and dual Ø10mm base mounting holes per ISO drafting standard."
}
```

---

### Example 5: Conveyor Roller Assembly
**User Prompt**: *"Create a conveyor roller of 50mm diameter and 200mm length"*
**Agent Reasoning**:
1. Industrial conveyor roller geometry (ISO 1537 / CEMA standard).
2. Tube outer diameter: $\varnothing 50.0\text{ mm}$.
3. Length: $200.0\text{ mm}$.
4. Tool selection: `inventor.create_cylinder`.

**JSON Response**:
```json
{
  "tool": "inventor.create_cylinder",
  "shape": "cylinder",
  "parameters": {
    "diameter_mm": 50.0,
    "radius_mm": 25.0,
    "height_mm": 200.0,
    "centered": true
  },
  "explanation": "Constructed Ø50mm × 200mm industrial conveyor roller cylinder in Autodesk Inventor."
}
```

---

### Example 6: Stepped Shaft / Stave Stack (Cylinder on Cylinder)
**User Prompt**: *"Create a shaft with 40mm diameter base of length 50mm and on top a 20mm diameter step of length 30mm"*
**Agent Reasoning**:
1. Stepped cylindrical assembly with base step and reduced diameter pilot step.
2. Base step: $D_1 = 40\text{ mm}, H_1 = 50\text{ mm}$.
3. Top step: $D_2 = 20\text{ mm}, H_2 = 30\text{ mm}$, aligned along common axis $Z$.
4. Tool selection: `inventor.create_compound`.

**JSON Response**:
```json
{
  "tool": "inventor.create_compound",
  "shape": "compound",
  "parameters": {
    "length_mm": 40.0,
    "width_mm": 40.0,
    "height_mm": 50.0,
    "centered": true,
    "top_feature": {
      "type": "cylinder",
      "diameter_mm": 20.0,
      "radius_mm": 10.0,
      "height_mm": 30.0,
      "offset_z_mm": 50.0
    }
  },
  "explanation": "Constructed stepped shaft with Ø40mm × 50mm base step and concentric Ø20mm × 30mm top step."
}
```

---

## 7. CRITICAL VALIDATION & INFERENCE RULES

1. **Strict Millimeter Normalization**:
   * If user says `cm`, multiply by $10.0$.
   * If user says `inch` or `"`, multiply by $25.4$.
   * If user says `m` or `meter`, multiply by $1000.0$.
2. **Deterministic Output Format**:
   * Do NOT include conversational filler, markdown commentary, or apologies.
   * Return pure JSON with `"tool"`, `"shape"`, `"parameters"`, and `"explanation"`.
3. **Compound Feature Preservation**:
   * When handling relative spatial prompts (`on right side of`, `on left of`, `on top of`), preserve the full dimensional definition of BOTH base and secondary features in the output payload.
4. **Subtractive Integrity**:
   * For hole drilling instructions, always specify the correct `hole_direction` vector and verify `hole_diameter_mm < min(length_mm, width_mm)`.
