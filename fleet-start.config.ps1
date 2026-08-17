# Per-repo fleet start config for readly-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'readly-mcp'
    BackendPort  = 10863
    FrontendPort = 10706
    HealthPath   = '/api/health'
    WebRoot      = 'D:\Dev\repos\readly-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'readly_mcp.server:app'
        Env           = @{ WEB_PORT = '10863' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
