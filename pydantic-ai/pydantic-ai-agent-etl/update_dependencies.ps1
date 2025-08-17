# Install PowerShell-Yaml module if not already installed
if (-not (Get-Module -ListAvailable -Name PowerShell-Yaml)) {
    Install-Module -Name PowerShell-Yaml -Force -Scope CurrentUser
}

# Import the module
Import-Module PowerShell-Yaml

# Read .env file
$envVars = @{}
Get-Content .env | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $key, $value = $line.Split("=", 2)
        $envVars[$key] = $value
    }
}

# Read dependencies.yaml file
$yaml = Get-Content dependencies.yaml -Raw
$dependencies = ConvertFrom-Yaml $yaml

# Create a dictionary of dependency URLs
$dependencyUrls = @{}
if ($dependencies.dependencies) {
    foreach ($dependencyName in $dependencies.dependencies.Keys) {
        $dependency = $dependencies.dependencies[$dependencyName]
        if ($dependency.url) {
            $dependencyUrls[$dependency.url] = '${dependencies.' + $dependencyName + '.url}'
        }
    }
}

# Update app.env section with .env variables, replacing with tokens if applicable
if ($dependencies.app -and $dependencies.app.env) {
    foreach ($key in $envVars.Keys) {
        $value = $envVars[$key]
        if ($dependencyUrls.ContainsKey($value)) {
            $dependencies.app.env[$key] = $dependencyUrls[$value]
        } else {
            $dependencies.app.env[$key] = $value
        }
    }
} else {
    $dependencies.app = @{ env = $envVars }
}

# Write updated dependencies back to dependencies.yaml
$dependencies | ConvertTo-Yaml | Out-File dependencies.yaml -Encoding UTF8