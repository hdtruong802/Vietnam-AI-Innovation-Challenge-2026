<#
.SYNOPSIS
Synchronize the local repository policy to GitHub only after explicit approval.

.DESCRIPTION
Without -Apply, this script is a local-only plan printer and never loads or
invokes GitHub CLI. With -Apply, it creates or updates only the labels and
branch protection described in .github/repository-settings.json. It never
deletes labels and it does not create issues, pull requests, commits, or pushes.

Use -Apply -WhatIf to preview the externally visible changes without calling
GitHub. Use -RequireRepositoryGuard only after the repository-guard workflow
has passed on the branch that will require it.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$SettingsPath = (Join-Path $PSScriptRoot '..\..\.github\repository-settings.json'),
    [switch]$Apply,
    [switch]$RequireRepositoryGuard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-RepositorySettings {
    param([string]$Path)

    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    if (-not (Test-Path -LiteralPath $resolvedPath)) {
        throw "Settings file not found: $resolvedPath"
    }

    $settings = Get-Content -LiteralPath $resolvedPath -Raw -Encoding utf8 | ConvertFrom-Json
    if ($settings.schemaVersion -ne 1 -or [string]::IsNullOrWhiteSpace($settings.repository)) {
        throw 'repository-settings.json is missing a supported schemaVersion or repository.'
    }

    foreach ($branch in @('main', 'dev')) {
        if ($null -eq $settings.branchProtection.$branch) {
            throw "repository-settings.json is missing branchProtection.$branch."
        }
    }

    return $settings
}

function Write-Plan {
    param($Settings)

    Write-Output "Repository: $($Settings.repository)"
    Write-Output "Labels to create or update: $(@($Settings.labels).Count)"
    foreach ($branch in @('main', 'dev')) {
        $policy = $Settings.branchProtection.$branch
        $checkMessage = if ($RequireRepositoryGuard) { "require '$($Settings.ci.checkName)'" } else { 'do not require a CI check yet' }
        Write-Output "Branch '$branch': PR-only, no force-push/delete, $($policy.requiredApprovingReviewCount) required approval(s), $checkMessage."
    }
}

function Invoke-Gh {
    param([string[]]$Arguments)

    & gh @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "gh $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

function Get-ExistingLabels {
    param([string]$Repository)

    $json = (& gh api "repos/$Repository/labels?per_page=100" | Out-String)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to list labels for $Repository."
    }

    $labels = @($json | ConvertFrom-Json)
    $byName = @{}
    foreach ($label in $labels) {
        $byName[$label.name] = $label
    }
    return $byName
}

function Sync-Labels {
    param($Settings)

    $existing = Get-ExistingLabels -Repository $Settings.repository
    foreach ($label in @($Settings.labels)) {
        $arguments = @(
            'api',
            '--method',
            $(if ($existing.ContainsKey($label.name)) { 'PATCH' } else { 'POST' }),
            $(if ($existing.ContainsKey($label.name)) {
                "repos/$($Settings.repository)/labels/$([System.Uri]::EscapeDataString($label.name))"
            } else {
                "repos/$($Settings.repository)/labels"
            }),
            '-f', "name=$($label.name)",
            '-f', "color=$($label.color)",
            '-f', "description=$($label.description)"
        )
        Invoke-Gh -Arguments $arguments
    }
}

function Set-BranchProtection {
    param(
        [string]$Repository,
        [string]$Branch,
        $Policy,
        [string]$CheckName,
        [bool]$RequireCheck
    )

    $requiredStatusChecks = if ($RequireCheck) {
        @{ strict = $true; contexts = @($CheckName) }
    } else {
        $null
    }

    $payload = @{
        required_status_checks = $requiredStatusChecks
        enforce_admins = $true
        required_pull_request_reviews = @{
            dismissal_restrictions = @{}
            dismiss_stale_reviews = $true
            require_code_owner_reviews = $false
            required_approving_review_count = [int]$Policy.requiredApprovingReviewCount
            require_last_push_approval = [bool]$Policy.requireLastPushApproval
        }
        restrictions = $null
        required_linear_history = $false
        allow_force_pushes = $false
        allow_deletions = $false
        block_creations = $false
        required_conversation_resolution = $true
        lock_branch = $false
        allow_fork_syncing = $false
    }

    $temporaryPayload = New-TemporaryFile
    try {
        $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporaryPayload -Encoding utf8
        Invoke-Gh -Arguments @(
            'api',
            '--method', 'PUT',
            "repos/$Repository/branches/$Branch/protection",
            '--input', $temporaryPayload,
            '--silent'
        )
    }
    finally {
        Remove-Item -LiteralPath $temporaryPayload -Force -ErrorAction SilentlyContinue
    }
}

$settings = Read-RepositorySettings -Path $SettingsPath

if (-not $Apply) {
    Write-Output 'Local-only mode: no GitHub CLI or remote API calls will be made.'
    Write-Plan -Settings $settings
    Write-Output 'Use -Apply -WhatIf to preview an authorized sync, or -Apply only after explicit publish approval.'
    return
}

if (-not $PSCmdlet.ShouldProcess($settings.repository, 'synchronize labels and branch protection')) {
    Write-Plan -Settings $settings
    return
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI (gh) is required for -Apply. Install and authenticate it before retrying.'
}

& gh auth status
if ($LASTEXITCODE -ne 0) {
    throw 'GitHub CLI is not authenticated. Run gh auth login with an Admin-capable account first.'
}

Sync-Labels -Settings $settings
foreach ($branch in @('main', 'dev')) {
    Set-BranchProtection `
        -Repository $settings.repository `
        -Branch $branch `
        -Policy $settings.branchProtection.$branch `
        -CheckName $settings.ci.checkName `
        -RequireCheck $RequireRepositoryGuard
}

Write-Output "Synchronized labels and branch protection for $($settings.repository)."
