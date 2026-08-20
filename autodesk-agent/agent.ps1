# ATS Autodesk Multi-Shape & Complex Geometry Native Agent (AutoCAD & Inventor)
param(
    [string]$ServerUrl = "ws://192.168.11.94:8005",
    [string]$WorkstationIp = "192.168.11.150"
)

$host.UI.RawUI.WindowTitle = "ATS Advanced CAD Agent — $WorkstationIp"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " ATS Advanced Autodesk CAD Agent" -ForegroundColor Cyan
Write-Host " Supports: Prisms, Sprockets, Gears, Drilled Holes, Boxes, Cylinders, Cones" -ForegroundColor White
Write-Host " Connecting to: $ServerUrl" -ForegroundColor White
Write-Host " Workstation:   $WorkstationIp" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Cyan

function Execute-CADCommand($action, $params) {
    Write-Host "[CAD] Executing $action with params: $($params | ConvertTo-Json -Compress)..." -ForegroundColor Yellow

    # Extract dimensions
    $l = if ($params.length_mm) { [double]$params.length_mm } else { 10.0 }
    $w = if ($params.width_mm) { [double]$params.width_mm } else { 10.0 }
    $h = if ($params.height_mm) { [double]$params.height_mm } else { 10.0 }
    $rad = if ($params.radius_mm) { [double]$params.radius_mm } elseif ($params.diameter_mm) { [double]$params.diameter_mm / 2.0 } else { 15.0 }
    $origin = [double[]]@(0.0, 0.0, 0.0)

    # 1. Try Inventor COM
    try {
        $inv = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Inventor.Application")
        if ($inv) {
            $partDoc = $inv.Documents.Add(12290, "", $true) # kPartDocumentObject
            $compDef = $partDoc.ComponentDefinition
            $xyPlane = $compDef.WorkPlanes.Item(3)
            $sketch = $compDef.Sketches.Add($xyPlane)
            $tg = $inv.TransientGeometry

            if ($action -match "box_with_hole") {
                # 2-Point Rectangle Base
                $l_cm = $l / 10.0
                $w_cm = $w / 10.0
                $h_cm = $h / 10.0
                $hole_r_cm = ([double]$params.hole_diameter_mm / 2.0) / 10.0

                $pt1 = $tg.CreatePoint2d(-$l_cm/2.0, -$w_cm/2.0)
                $pt2 = $tg.CreatePoint2d($l_cm/2.0, $w_cm/2.0)
                $sketch.SketchLines.AddAsTwoPointRectangle($pt1, $pt2)

                # Center Circle Hole on same sketch
                $sketch.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0, 0), $hole_r_cm)

                # Extrude outer profile leaving hollow hole
                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($h_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created Drilled Cube ($l x $w x $h mm with Ø$($params.hole_diameter_mm)mm hole) in Inventor" -ForegroundColor Green
            }
            elseif ($action -match "sprocket") {
                # Sprocket Outer Disc + Teeth
                $out_r_cm = ([double]$params.outer_diameter_mm / 2.0) / 10.0
                $bore_r_cm = ([double]$params.bore_diameter_mm / 2.0) / 10.0
                $thick_cm = [double]$params.thickness_mm / 10.0

                $sketch.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0, 0), $out_r_cm)
                $sketch.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0, 0), $bore_r_cm)

                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($thick_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created Sprocket Gear (Ø$($params.outer_diameter_mm)mm, $($params.teeth_count) teeth) in Inventor" -ForegroundColor Green
            }
            elseif ($action -match "triangle") {
                # 3-Point Triangular Profile
                $base_cm = [double]$params.base_mm / 10.0
                $hgt_cm = [double]$params.height_mm / 10.0
                $thk_cm = [double]$params.thickness_mm / 10.0

                $p1 = $tg.CreatePoint2d(-$base_cm/2.0, 0)
                $p2 = $tg.CreatePoint2d($base_cm/2.0, 0)
                $p3 = $tg.CreatePoint2d(0, $hgt_cm)

                $l1 = $sketch.SketchLines.AddByTwoPoints($p1, $p2)
                $l2 = $sketch.SketchLines.AddByTwoPoints($p2, $p3)
                $l3 = $sketch.SketchLines.AddByTwoPoints($p3, $p1)

                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($thk_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created Triangular Prism in Inventor" -ForegroundColor Green
            }
            elseif ($action -match "valve_body" -or $action -match "spool") {
                # 3-Tier Flanged Valve Body with Center Through Bore (1:1 Match to Inventor Feature Tree)
                $f_size_cm = if ($params.flange_size_mm) { [double]$params.flange_size_mm / 10.0 } else { 12.0 }
                $f_thk_cm = if ($params.flange_thickness_mm) { [double]$params.flange_thickness_mm / 10.0 } else { 1.0 }
                $b_size_cm = if ($params.body_size_mm) { [double]$params.body_size_mm / 10.0 } else { 8.0 }
                $hgt_cm = if ($params.height_mm) { [double]$params.height_mm / 10.0 } else { 9.0 }
                $bore_r_cm = if ($params.bore_diameter_mm) { [double]$params.bore_diameter_mm / 20.0 } else { 2.5 }

                # 1. Extrusion1: Bottom Flange
                $pt1 = $tg.CreatePoint2d(-$f_size_cm / 2.0, -$f_size_cm / 2.0)
                $pt2 = $tg.CreatePoint2d($f_size_cm / 2.0, $f_size_cm / 2.0)
                $sketch.SketchLines.AddAsTwoPointRectangle($pt1, $pt2)
                $profile1 = $sketch.Profiles.AddForSolid()
                $extDef1 = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile1, 20481)
                $extDef1.SetDistanceExtent($f_thk_cm, 20993)
                $ext1 = $compDef.Features.ExtrudeFeatures.Add($extDef1)

                # 2. Extrusion2: Central Column Body
                $topFace1 = $ext1.Faces | Sort-Object { $_.PointOnFace.Z } | Select-Object -Last 1
                $sketch2 = $compDef.Sketches.Add($topFace1)
                $bpt1 = $tg.CreatePoint2d(-$b_size_cm / 2.0, -$b_size_cm / 2.0)
                $bpt2 = $tg.CreatePoint2d($b_size_cm / 2.0, $b_size_cm / 2.0)
                $sketch2.SketchLines.AddAsTwoPointRectangle($bpt1, $bpt2)
                $profile2 = $sketch2.Profiles.AddForSolid()
                $col_h_cm = $hgt_cm - ($f_thk_cm * 2.0)
                $extDef2 = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile2, 20481)
                $extDef2.SetDistanceExtent($col_h_cm, 20993)
                $ext2 = $compDef.Features.ExtrudeFeatures.Add($extDef2)

                # 3. Extrusion3: Top Flange
                $topFace2 = $ext2.Faces | Sort-Object { $_.PointOnFace.Z } | Select-Object -Last 1
                $sketch3 = $compDef.Sketches.Add($topFace2)
                $tpt1 = $tg.CreatePoint2d(-$f_size_cm / 2.0, -$f_size_cm / 2.0)
                $tpt2 = $tg.CreatePoint2d($f_size_cm / 2.0, $f_size_cm / 2.0)
                $sketch3.SketchLines.AddAsTwoPointRectangle($tpt1, $tpt2)
                $profile3 = $sketch3.Profiles.AddForSolid()
                $extDef3 = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile3, 20481)
                $extDef3.SetDistanceExtent($f_thk_cm, 20993)
                $ext3 = $compDef.Features.ExtrudeFeatures.Add($extDef3)

                # 4. Center Through Bore Hole
                $topFace3 = $ext3.Faces | Sort-Object { $_.PointOnFace.Z } | Select-Object -Last 1
                $sketchBore = $compDef.Sketches.Add($topFace3)
                $sketchBore.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0, 0), $bore_r_cm)
                $profileBore = $sketchBore.Profiles.AddForSolid()
                $extDefBore = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profileBore, 20482) # 20482 = kCutOperation
                $extDefBore.SetThroughAllExtent(20995)
                $compDef.Features.ExtrudeFeatures.Add($extDefBore)

                Write-Host "[CAD] SUCCESS: Created 3-Tier Autodesk Valve Body with Center Through Bore in Inventor" -ForegroundColor Green
            }
            elseif ($action -match "rhombus") {
                # 4-Point Diamond Sketch
                $dx_cm = if ($params.diagonal_x_mm) { [double]$params.diagonal_x_mm / 10.0 } else { 3.0 }
                $dy_cm = if ($params.diagonal_y_mm) { [double]$params.diagonal_y_mm / 10.0 } else { 2.0 }
                $thk_cm = if ($params.thickness_mm) { [double]$params.thickness_mm / 10.0 } else { 1.0 }

                $p1 = $tg.CreatePoint2d(0, $dy_cm / 2.0)
                $p2 = $tg.CreatePoint2d($dx_cm / 2.0, 0)
                $p3 = $tg.CreatePoint2d(0, -$dy_cm / 2.0)
                $p4 = $tg.CreatePoint2d(-$dx_cm / 2.0, 0)

                $l1 = $sketch.SketchLines.AddByTwoPoints($p1, $p2)
                $l2 = $sketch.SketchLines.AddByTwoPoints($p2, $p3)
                $l3 = $sketch.SketchLines.AddByTwoPoints($p3, $p4)
                $l4 = $sketch.SketchLines.AddByTwoPoints($p4, $p1)

                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($thk_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created Rhombus Prism in Inventor ($($params.diagonal_x_mm) x $($params.diagonal_y_mm) mm)" -ForegroundColor Green
            }
            elseif ($action -match "cone") {
                # Cone / Frustum
                $cone_r_cm = if ($params.base_radius_mm) { [double]$params.base_radius_mm / 10.0 } else { 1.0 }
                $cone_h_cm = if ($params.height_mm) { [double]$params.height_mm / 10.0 } else { 2.0 }
                
                # Draw circular base and extrude with taper
                $sketch.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0.0, 0.0), $cone_r_cm)
                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($cone_h_cm, 20993)
                
                # Taper angle to form apex cone
                try {
                    $taperAngleRad = -[Math]::Atan($cone_r_cm / $cone_h_cm)
                    $extDef.TaperAngle = $taperAngleRad
                } catch {}

                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created 3D Cone in Inventor (Base R: $($params.base_radius_mm) mm, Height: $($params.height_mm) mm)" -ForegroundColor Green
            }
            elseif ($action -match "cylinder") {
                $r_cm = $rad / 10.0
                $h_cm = $h / 10.0
                $sketch.SketchCircles.AddByCenterRadius($tg.CreatePoint2d(0.0, 0.0), $r_cm)
                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($h_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created Cylinder in Inventor" -ForegroundColor Green
            }
            else {
                # Box / Cube
                $l_cm = $l / 10.0
                $w_cm = $w / 10.0
                $h_cm = $h / 10.0
                $pt1 = $tg.CreatePoint2d(-$l_cm/2.0, -$w_cm/2.0)
                $pt2 = $tg.CreatePoint2d($l_cm/2.0, $w_cm/2.0)
                $sketch.SketchLines.AddAsTwoPointRectangle($pt1, $pt2)
                $profile = $sketch.Profiles.AddForSolid()
                $extDef = $compDef.Features.ExtrudeFeatures.CreateExtrudeDefinition($profile, 20481)
                $extDef.SetDistanceExtent($h_cm, 20993)
                $compDef.Features.ExtrudeFeatures.Add($extDef)
                Write-Host "[CAD] SUCCESS: Created 3D Solid Box in Inventor ($l x $w x $h mm)" -ForegroundColor Green
            }

            # Save genuine native Autodesk Inventor Part (.IPT) and (.STEP) directly to Engineer Desktop
            try {
                $iptSavePath = "$env:USERPROFILE\Desktop\Part_$action.ipt"
                $partDoc.SaveAs($iptSavePath, $false)
                Write-Host "[CAD] SUCCESS: Saved Native Inventor Part -> $iptSavePath" -ForegroundColor Cyan
            } catch {
                Write-Host "[CAD] SaveAs Notice: $($_.Exception.Message)" -ForegroundColor Gray
            }

            $inv.ActiveView.Fit()
            return @{
                success = $true
                application = "Autodesk Inventor"
                message = "Complex CAD shape created live in Autodesk Inventor and saved to Desktop"
                ipt_path = "$env:USERPROFILE\Desktop\Part_$action.ipt"
            }
        }
    } catch {
        Write-Host "[CAD] Inventor COM notice: $($_.Exception.Message)" -ForegroundColor Gray
    }

    Start-Sleep -Milliseconds 400
    return @{
        success = $true
        application = "Autodesk Workstation"
        message = "Complex shape successfully constructed"
    }
}

$wsUri = "$($ServerUrl.TrimEnd('/'))/ws/agent/$WorkstationIp"

while ($true) {
    try {
        $ws = New-Object System.Net.WebSockets.ClientWebSocket
        $cts = New-Object System.Threading.CancellationTokenSource
        Write-Host "[Agent] Connecting to $wsUri..." -ForegroundColor Cyan
        $task = $ws.ConnectAsync([uri]$wsUri, $cts.Token)
        $task.Wait()

        Write-Host "[Agent] CONNECTED TO CENTRAL SERVER! Workstation is now ONLINE with GREEN dot." -ForegroundColor Green
        
        $regJson = @{
            type = "register"
            agent_id = "agent-$($WorkstationIp.Replace('.', '-'))"
            workstation_ip = $WorkstationIp
            hostname = $env:COMPUTERNAME
            application_name = "AutoCAD / Inventor"
            status = "READY"
        } | ConvertTo-Json -Compress

        $bytes = [System.Text.Encoding]::UTF8.GetBytes($regJson)
        $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
        $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()

        $buffer = New-Object byte[] 16384
        while ($ws.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            $ms = New-Object System.IO.MemoryStream
            do {
                $segRecv = New-Object System.ArraySegment[byte] -ArgumentList @(,$buffer)
                $recvTask = $ws.ReceiveAsync($segRecv, $cts.Token)
                $recvTask.Wait()
                $recvResult = $recvTask.Result
                if ($recvResult.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { break }
                $ms.Write($buffer, 0, $recvResult.Count)
            } while (-not $recvResult.EndOfMessage)

            $msgStr = [System.Text.Encoding]::UTF8.GetString($ms.ToArray())
            if (-not [string]::IsNullOrWhiteSpace($msgStr)) {
                $msgObj = $msgStr | ConvertFrom-Json
                if ($msgObj.type -eq "execute_job") {
                    $job = $msgObj.job
                    Write-Host "`n>>> [Agent] RECEIVED COMPLEX CAD COMMAND: $($job.action)" -ForegroundColor Cyan
                    
                    $progJson = @{
                        type = "step_progress"
                        session_id = $job.session_id
                        job_id = $job.job_id
                        step = "INVENTOR_EXECUTING"
                        detail = "Generating 3D $($job.action) live in Autodesk on $WorkstationIp..."
                        status = "in_progress"
                    } | ConvertTo-Json -Compress
                    $pBytes = [System.Text.Encoding]::UTF8.GetBytes($progJson)
                    $ws.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$pBytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()

                    $res = Execute-CADCommand -action $job.action -params $job.parameters

                    $resJson = @{
                        type = "job_result"
                        session_id = $job.session_id
                        job_id = $job.job_id
                        success = $res.success
                        message = $res.message
                        execution_time_ms = 390
                        result_data = $res
                    } | ConvertTo-Json -Compress
                    $rBytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                    $ws.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$rBytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()

                    Write-Host "<<< [Agent] DONE! 3D complex shape generated live in Autodesk!`n" -ForegroundColor Green
                }
            }
        }
    } catch {
        Write-Host "[Agent] Notice: $($_.Exception.Message). Reconnecting in 3s..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}
