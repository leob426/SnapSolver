<#
    auto-release.ps1

    Usage:
      1) Right-click the SnapSolver folder background → "Open in PowerShell"
      2) Run:  .\auto-release.ps1
         - The script will:
             1. Parse CURRENT_VERSION from SnapSolver.py (e.g. "1.0.4")
             2. Increment the patch digit → "1.0.5"
             3. Update SnapSolver.py, latest_version.txt, and optionally SnapSolverVersionInfo.txt
             4. Compile with PyInstaller
             5. Commit + push changes to GitHub
             6. Tag the commit (v1.0.5)
             7. Create a GitHub release with the new EXE
#>

Write-Host "=== Auto-Release Script for SnapSolver ==="

# Make sure:
#   - Git is installed & your local folder is a Git repo
#   - GitHub CLI (gh) is installed & you've run: gh auth login
#   - PyInstaller + dependencies installed: pip install pyinstaller requests pillow keyboard pyautogui

# 1) Read SnapSolver.py to find CURRENT_VERSION = "X.Y.Z"
$code = Get-Content .\SnapSolver.py -Raw

# Regex capturing something like: CURRENT_VERSION = "1.0.4"
$pattern = 'CURRENT_VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
$match = [regex]::Match($code, $pattern)

if (-not $match.Success) {
    Write-Host "ERROR: Could not find CURRENT_VERSION in SnapSolver.py!"
    exit 1
}

$major = $match.Groups[1].Value
$minor = $match.Groups[2].Value
$patch = $match.Groups[3].Value

Write-Host "Current version found in SnapSolver.py: $major.$minor.$patch"

# 2) Increment the patch digit
$patch = [int]$patch + 1
$newVersion = "$major.$minor.$patch"
Write-Host "Bumping version to: $newVersion"

# 3) Update CURRENT_VERSION in SnapSolver.py
$codeUpdated = $code -replace $pattern, "CURRENT_VERSION = `"$newVersion`""
Set-Content SnapSolver.py $codeUpdated

# 4) Update latest_version.txt with the same newVersion
Set-Content latest_version.txt $newVersion

# 5) (Optional) If SnapSolverVersionInfo.txt exists, update the file version there too
#    so the EXE's file properties match the new version.
if (Test-Path .\SnapSolverVersionInfo.txt) {
    Write-Host "Updating SnapSolverVersionInfo.txt to version $newVersion..."
    $versionFile = Get-Content .\SnapSolverVersionInfo.txt -Raw

    # We assume lines like: StringStruct('FileVersion', '1.0.4'), etc.
    # Replace the old version with $newVersion in both FileVersion and ProductVersion
    $oldVersionPattern = '(\d+)\.(\d+)\.(\d+)'
    # We'll do a broad replace for lines referencing 'FileVersion', 'X.Y.Z' or 'ProductVersion', 'X.Y.Z'
    # But we do need to find the old version from the file, or just do a general pattern replace if you want.

    # For simplicity, let's do a general pattern for lines with 'FileVersion' or 'ProductVersion'
    # This approach will update any number we see, though. So if you prefer only the old version, you'd parse it out.
    $versionFile = $versionFile -replace "(StringStruct\('FileVersion', ')\d+\.\d+\.\d+(')", "`$1$newVersion`$2"
    $versionFile = $versionFile -replace "(StringStruct\('ProductVersion', ')\d+\.\d+\.\d+(')", "`$1$newVersion`$2"

    Set-Content .\SnapSolverVersionInfo.txt $versionFile
}

# 6) Compile with PyInstaller
Write-Host "Compiling SnapSolver with PyInstaller..."
pyinstaller --onefile --windowed --icon=SnapSolverIcon.ico `
    --add-data "SnapSolverLogo.png;." `
    --version-file SnapSolverVersionInfo.txt `
    SnapSolver.py

if (!(Test-Path "dist\SnapSolver.exe")) {
    Write-Host "ERROR: No EXE found in dist folder. Compilation failed?"
    exit 1
}

Write-Host "Compilation successful! dist\SnapSolver.exe created."

# 7) Commit & push changes
Write-Host "Committing and pushing code changes..."
git add .
git commit -m "Auto-release version $newVersion"
git push

# 8) Tag the commit
$tagName = "v$newVersion"
git tag $tagName
git push origin $tagName

# 9) Create a GitHub Release with the new EXE
Write-Host "Creating GitHub release..."
gh release create $tagName "dist\SnapSolver.exe" `
    --title "SnapSolver $newVersion" `
    --notes "Automated release of SnapSolver $newVersion."

Write-Host "=== Done! Released SnapSolver $newVersion. ==="
