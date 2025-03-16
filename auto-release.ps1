<#
    auto-release.ps1

    Usage:
      1) Right-click the SnapSolver folder background → "Open in PowerShell"
      2) Run:  .\auto-release.ps1
      It will:
         - Parse CURRENT_VERSION from SnapSolver.py
         - Increment the patch digit (e.g. 1.0.3 → 1.0.4)
         - Update SnapSolver.py with the new version
         - Update latest_version.txt
         - Update SnapSolverVersionInfo.txt (FileVersion, ProductVersion) if it exists
         - Run PyInstaller to compile
         - Commit + push changes
         - Tag the commit (v1.0.4)
         - Create a GitHub release with the new EXE attached
#>

Write-Host "=== Auto-Release Script for SnapSolver ==="

# Make sure GitHub CLI is installed and 'gh auth login' was done beforehand
# Also ensure 'pyinstaller' is installed: pip install pyinstaller requests pillow keyboard pyautogui

# 1) Read SnapSolver.py to find the current version
#    We expect a line like: CURRENT_VERSION = "1.0.3"
$code = Get-Content .\SnapSolver.py -Raw

# Regex to capture major.minor.patch
$pattern = 'CURRENT_VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
$match = [regex]::Match($code, $pattern)

if (-not $match.Success) {
    Write-Host "ERROR: Could not find CURRENT_VERSION in SnapSolver.py!"
    exit 1
}

$major = $match.Groups[1].Value
$minor = $match.Groups[2].Value
$patch = $match.Groups[3].Value

Write-Host "Current version found: $major.$minor.$patch"

# Store the old version (for reference if needed)
$oldVersion = "$major.$minor.$patch"

# 2) Increment the patch digit
$patch = [int]$patch + 1
$newVersion = "$major.$minor.$patch"
Write-Host "Bumping version to: $newVersion"

# 3) Replace CURRENT_VERSION line with the new version
$codeUpdated = $code -replace $pattern, "CURRENT_VERSION = `"$newVersion`""
Set-Content SnapSolver.py $codeUpdated

# 4) Update latest_version.txt
Set-Content latest_version.txt $newVersion

# (NEW) If SnapSolverVersionInfo.txt exists, also update FileVersion/ProductVersion automatically
if (Test-Path .\SnapSolverVersionInfo.txt) {
    Write-Host "Updating SnapSolverVersionInfo.txt to $newVersion..."
    $versionFile = Get-Content .\SnapSolverVersionInfo.txt -Raw
    # We look for lines like: StringStruct('FileVersion', '1.0.3')
    # Then replace the old version with the new one
    $versionFile = $versionFile -replace "FileVersion', '$oldVersion", "FileVersion', '$newVersion"
    $versionFile = $versionFile -replace "ProductVersion', '$oldVersion", "ProductVersion', '$newVersion"
    Set-Content .\SnapSolverVersionInfo.txt $versionFile
}

# 5) Compile with PyInstaller
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

# 6) Commit and push changes
Write-Host "Committing and pushing code changes..."
git add .
git commit -m "Auto-release version $newVersion"
git push

# 7) Tag the commit (so we can reference it in the release)
$tagName = "v$newVersion"
git tag $tagName
git push origin $tagName

# 8) Create a GitHub Release with the new EXE
Write-Host "Creating GitHub release..."
gh release create $tagName "dist\SnapSolver.exe" `
    --title "SnapSolver $newVersion" `
    --notes "Automated release of SnapSolver $newVersion."

Write-Host "=== Done! Released SnapSolver $newVersion. ==="
