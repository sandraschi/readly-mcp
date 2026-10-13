# Per-repo fleet start config for readly-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'readly-mcp'
    BackendPort  = 10737
    FrontendPort = 10736
    HealthPath   = '/api/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'readly_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10737' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
