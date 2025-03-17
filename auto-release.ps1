<#
    auto-release.ps1

    Automates:
      1. Parsing CURRENT_VERSION from SnapSolver.py.
      2. Incrementing the patch version.
      3. Updating SnapSolver.py, latest_version.txt, and SnapSolverVersionInfo.txt.
      4. Compiling with the correct PyInstaller command.
      5. Committing + pushing changes to GitHub.
      6. Tagging the commit.
      7. Creating a GitHub release with the new EXE.
#>

Write-Host "`n=== 🚀 Auto-Release Script for SnapSolver ===`n"

# Ensure dependencies are installed and configured
Write-Host "🔍 Checking dependencies..."
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: Git is not installed! Install Git and try again."
    exit 1
}
if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: GitHub CLI (gh) is not installed! Run `gh auth login` first."
    exit 1
}
if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: PyInstaller is not installed! Run `pip install pyinstaller`."
    exit 1
}

# 1) Read CURRENT_VERSION from SnapSolver.py
$code = Get-Content .\SnapSolver.py -Raw
$pattern = 'CURRENT_VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
$match = [regex]::Match($code, $pattern)

if (-not $match.Success) {
    Write-Host "❌ ERROR: Could not find CURRENT_VERSION in SnapSolver.py!"
    exit 1
}

$major = $match.Groups[1].Value
$minor = $match.Groups[2].Value
$patch = $match.Groups[3].Value

Write-Host "🔍 Current version found: $major.$minor.$patch"

# 2) Increment patch version
$patch = [int]$patch + 1
$newVersion = "$major.$minor.$patch"
Write-Host "🚀 Bumping version to: $newVersion"

# 3) Update CURRENT_VERSION in SnapSolver.py
$codeUpdated = $code -replace $pattern, "CURRENT_VERSION = `"$newVersion`""
Set-Content SnapSolver.py $codeUpdated

# 4) Update latest_version.txt
Set-Content latest_version.txt $newVersion

# 5) Update SnapSolverVersionInfo.txt (if exists)
if (Test-Path .\SnapSolverVersionInfo.txt) {
    Write-Host "📌 Updating SnapSolverVersionInfo.txt..."
    $versionFile = Get-Content .\SnapSolverVersionInfo.txt -Raw
    $versionFile = $versionFile -replace "(\d+)\.(\d+)\.(\d+)", "$newVersion"
    Set-Content .\SnapSolverVersionInfo.txt $versionFile
}

# 6) Compile with PyInstaller (Your requested command)
Write-Host "⚙️ Compiling SnapSolver..."
pyinstaller --onefile --noconsole --icon="SnapSolverIcon.ico" --add-data "SnapSolverLogo.png;." --name "SnapSolver" SnapSolver.py

if (!(Test-Path "dist\SnapSolver.exe")) {
    Write-Host "❌ ERROR: Compilation failed! No EXE found."
    exit 1
}

Write-Host "✅ Compilation successful! dist\SnapSolver.exe created."

# 7) Commit & push changes
Write-Host "📤 Committing changes..."
git add .
git commit -m "Auto-release version $newVersion"
git push

# 8) Tag the commit
$tagName = "v$newVersion"
git tag $tagName
git push origin $tagName

# 9) Create GitHub Release with new EXE
Write-Host "📢 Creating GitHub release..."
gh release create $tagName "dist\SnapSolver.exe" `
    --title "SnapSolver $newVersion" `
    --notes "🚀 Automated release of SnapSolver $newVersion."

Write-Host "`n🎉 DONE! SnapSolver $newVersion released successfully. 🎉`n"
