# Per-repo fleet start config for readly-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'readly-mcp'
    BackendPort  = 11201
    FrontendPort = 11200
    HealthPath   = '/api/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'readly_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '11201' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
