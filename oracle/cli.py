"""
Oracle CLI & Web API
====================

Command-line interface and FastAPI server for Oracle.

CLI Commands:
  oracle analyze <path>     - Analyze a project
  oracle watch <path>       - Watch directory for new projects
  oracle report <id>        - Get report by ID
  oracle serve              - Start API server

API Endpoints:
  POST /api/analyze         - Analyze a project
  GET  /api/report/{id}     - Get report
  GET  /api/reports         - List all reports
  GET  /api/status          - System status
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oracle.cli")


def print_banner():
    """Print Oracle banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔮 ORACLE - Financial Intelligence System              ║
    ║                                                           ║
    ║   BlackRock Aladdin-inspired Analysis Engine             ║
    ║   for Crypto Projects & DeFi Protocols                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


async def cmd_analyze(args):
    """Analyze a project"""
    from oracle.core import Oracle
    from oracle.report_generator import ReportGenerator, ReportConfig
    
    print_banner()
    
    project_path = args.path
    if not Path(project_path).exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)
    
    print(f"\n📂 Analyzing: {project_path}")
    print("=" * 60)
    
    # Initialize Oracle
    oracle = Oracle()
    
    # Run analysis
    report = await oracle.analyze_project(project_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n  Project: {report.project_name}")
    print(f"  Type: {report.project_type}")
    print(f"  Duration: {report.analysis_duration_seconds:.2f}s")
    print(f"\n  🎯 Overall Score: {report.risk.overall_score:.0f}/100")
    print(f"  ⚠️ Risk Level: {report.risk.risk_level.upper()}")
    print(f"  📋 Recommendation: {report.risk.investment_recommendation.upper()}")
    
    if report.risk.red_flags:
        print(f"\n  🚨 Red Flags ({len(report.risk.red_flags)}):")
        for flag in report.risk.red_flags[:5]:
            print(f"     • {flag}")
    
    print(f"\n  📈 Score Breakdown:")
    print(f"     Tokenomics: {report.risk.tokenomics_score:.0f}/100")
    print(f"     Market:     {report.risk.market_score:.0f}/100")
    print(f"     Security:   {report.risk.security_score:.0f}/100")
    print(f"     Team:       {report.risk.team_score:.0f}/100")
    print(f"     Liquidity:  {report.risk.liquidity_score:.0f}/100")
    
    # Generate report if requested
    if args.output:
        config = ReportConfig(output_dir=str(Path(args.output).parent))
        generator = ReportGenerator(config)
        
        fmt = args.format or "html"
        report_path = generator.generate(report, format=fmt)
        print(f"\n  📄 Report saved: {report_path}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print("=" * 60 + "\n")


async def cmd_watch(args):
    """Watch directory for new projects"""
    from oracle.core import Oracle
    
    print_banner()
    
    watch_path = args.path
    if not Path(watch_path).exists():
        print(f"❌ Path not found: {watch_path}")
        sys.exit(1)
    
    print(f"\n👁️ Watching directory: {watch_path}")
    print("Press Ctrl+C to stop...")
    print("=" * 60)
    
    oracle = Oracle()
    await oracle.watch_directory(watch_path)


async def cmd_serve(args):
    """Start API server"""
    import os
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException, BackgroundTasks
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        print("❌ FastAPI and uvicorn required. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    from oracle.core import Oracle
    from oracle.report_generator import ReportGenerator, ReportConfig
    
    print_banner()
    
    # Create FastAPI app
    app = FastAPI(
        title="Oracle API",
        description="Financial Intelligence System API",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Storage
    reports_cache = {}
    oracle = Oracle()
    generator = ReportGenerator()
    
    # Models
    class AnalyzeRequest(BaseModel):
        path: str
        generate_report: bool = True
        report_format: str = "json"
    
    class AnalyzeResponse(BaseModel):
        success: bool
        report_id: str = None
        error: str = None
    
    @app.get("/")
    async def root():
        return {"message": "🔮 Oracle API", "version": "1.0.0"}
    
    @app.get("/api/status")
    async def status():
        return {
            "status": "running",
            "reports_count": len(reports_cache),
            "version": "1.0.0"
        }
    
    # Security: Allowed base directories for analysis
    ALLOWED_ANALYSIS_DIRS = [
        Path("/home/ubuntu/projects"),
        Path("/tmp/oracle_analysis"),
        Path.cwd(),  # Current working directory
    ]
    
    def is_safe_path(path: str) -> bool:
        """Validate path is within allowed directories (prevent path traversal)"""
        try:
            resolved = Path(path).resolve()
            # Check if path is within any allowed directory
            for allowed in ALLOWED_ANALYSIS_DIRS:
                try:
                    allowed_resolved = allowed.resolve()
                    if resolved.is_relative_to(allowed_resolved):
                        return True
                except (ValueError, OSError):
                    continue
            return False
        except (ValueError, OSError):
            return False
    
    @app.post("/api/analyze")
    async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
        """Analyze a project"""
        # Security: Validate path to prevent traversal attacks
        if not is_safe_path(request.path):
            raise HTTPException(status_code=403, detail="Access denied: path outside allowed directories")
        
        if not Path(request.path).exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        try:
            report = await oracle.analyze_project(request.path)
            reports_cache[report.report_id] = report
            
            if request.generate_report:
                report_path = generator.generate(report, format=request.report_format)
            
            return {
                "success": True,
                "report_id": report.report_id,
                "project_name": report.project_name,
                "overall_score": report.risk.overall_score,
                "risk_level": report.risk.risk_level,
                "recommendation": report.risk.investment_recommendation,
                "red_flags_count": len(report.risk.red_flags)
            }
        
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/report/{report_id}")
    async def get_report(report_id: str):
        """Get report by ID"""
        if report_id not in reports_cache:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report = reports_cache[report_id]
        
        # Convert to dict
        from dataclasses import asdict
        return {
            "success": True,
            "report": {
                "report_id": report.report_id,
                "project_name": report.project_name,
                "project_type": report.project_type,
                "generated_at": report.generated_at,
                "executive_summary": report.executive_summary,
                "tokenomics": asdict(report.tokenomics),
                "market": asdict(report.market),
                "security": asdict(report.security),
                "team": asdict(report.team),
                "risk": asdict(report.risk),
            }
        }
    
    @app.get("/api/reports")
    async def list_reports():
        """List all reports"""
        return {
            "success": True,
            "count": len(reports_cache),
            "reports": [
                {
                    "report_id": r.report_id,
                    "project_name": r.project_name,
                    "generated_at": r.generated_at,
                    "overall_score": r.risk.overall_score,
                    "risk_level": r.risk.risk_level
                }
                for r in reports_cache.values()
            ]
        }
    
    @app.delete("/api/report/{report_id}")
    async def delete_report(report_id: str):
        """Delete a report"""
        if report_id not in reports_cache:
            raise HTTPException(status_code=404, detail="Report not found")
        
        del reports_cache[report_id]
        return {"success": True, "message": "Report deleted"}
    
    print(f"\n🚀 Starting Oracle API server on port {args.port}")
    print(f"   Docs: http://localhost:{args.port}/docs")
    print("=" * 60)
    
    uvicorn.run(app, host=args.host, port=args.port)


async def cmd_report(args):
    """Display a specific report"""
    from oracle.report_generator import ReportGenerator
    
    print_banner()
    
    report_id = args.report_id
    print(f"\n📄 Looking for report: {report_id}")
    
    # Look in default reports directory
    reports_dir = Path("./reports")
    if not reports_dir.exists():
        print("❌ Reports directory not found")
        sys.exit(1)
    
    # Find matching report
    found = None
    for f in reports_dir.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
                if data.get("report_id") == report_id:
                    found = f
                    break
        except:
            continue
    
    if not found:
        print(f"❌ Report not found: {report_id}")
        sys.exit(1)
    
    print(f"✅ Found: {found}")
    
    with open(found) as f:
        data = json.load(f)
    
    print(json.dumps(data, indent=2))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🔮 Oracle - Financial Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project")
    analyze_parser.add_argument("path", help="Path to project directory")
    analyze_parser.add_argument("-o", "--output", help="Output report path")
    analyze_parser.add_argument("-f", "--format", choices=["html", "json", "text", "markdown"],
                                help="Report format (default: html)")
    
    # watch command
    watch_parser = subparsers.add_parser("watch", help="Watch directory for new projects")
    watch_parser.add_argument("path", help="Directory to watch")
    
    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve_parser.add_argument("--port", type=int, default=8888, help="Port to listen on")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Get report by ID")
    report_parser.add_argument("report_id", help="Report ID")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        asyncio.run(cmd_analyze(args))
    elif args.command == "watch":
        asyncio.run(cmd_watch(args))
    elif args.command == "serve":
        asyncio.run(cmd_serve(args))
    elif args.command == "report":
        asyncio.run(cmd_report(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
