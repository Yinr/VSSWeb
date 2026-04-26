$ip = "192.168.0.5"
$outDir = ".\VSSWebBackup"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Invoke-WebRequest "http://$ip/" -OutFile "$outDir\index.html"
Invoke-WebRequest "http://$ip/favicon.ico" -OutFile "$outDir\favicon.ico"
Invoke-WebRequest "http://$ip/IVSWeb.cab" -OutFile "$outDir\IVSWeb.cab"
Invoke-WebRequest "http://$ip/olp.js" -OutFile "$outDir\olp.js"
Invoke-WebRequest "http://$ip/oem_t.js" -OutFile "$outDir\oem_t.js"
Invoke-WebRequest "http://$ip/m.js" -OutFile "$outDir\m.js"
Invoke-WebRequest "http://$ip/m.css" -OutFile "$outDir\m.css"

# expand.exe "$outDir\IVSWeb.cab" -F:* "$outDir\IVSWeb"