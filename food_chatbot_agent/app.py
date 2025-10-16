"""
FoodieExpress AI Agent - Application Entry Point
=================================================
Production-ready entry point for the AI chatbot agent

This is the main entry point for running the agent server.
Compatible with Docker, local development, and production deployment.

Version: 4.0
Author: Meet Ghadiya
Date: October 2025

Usage:
    Development:  python app.py
    Production:   python app.py --production
    Docker:       Automatically starts via Dockerfile
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config, validate_config
from utils.logger import logger
from agent import app


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="FoodieExpress AI Agent Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Run in development mode
  python app.py --production       # Run in production mode
  python app.py --port 5001        # Run on custom port
  python app.py --host 0.0.0.0     # Listen on all interfaces
        """
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='Run in production mode (uses Waitress server)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=config.FLASK_HOST,
        help=f'Host to bind to (default: {config.FLASK_HOST})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=config.FLASK_PORT,
        help=f'Port to bind to (default: {config.FLASK_PORT})'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (auto-reload, detailed errors)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration and exit'
    )
    
    return parser.parse_args()


def print_banner():
    """Print startup banner"""
    banner = f"""
{'=' * 80}
   _____ ____  ____  _____ ________ ______   _____ _  ______  _____  ________ ____ ____ 
  / ___// __ \\/ __ \\/ ___// ____/ ___/ /   / ___/| |/ / __ \\/ __ \\/ ____/ // _// ___/
  \\__ \\/ / / / / / /\\__ \\/ __/  \\__ \\/ /    \\__ \\ |   / /_/ / /_/ / __/ / /  / / \\__ \\ 
 ___/ / /_/ / /_/ /___/ / /___ ___/ / /___ ___/ / /   / ____/ _, _/ /___/ /__/ / ___/ / 
/____/\\____/\\____//____/_____//____/_____//____/ /_/  /_/   /_/ |_/_____/_____/___//____/  
{'=' * 80}
                    🤖 FOODIEEXPRESS AI AGENT v{config.AGENT_VERSION}
                         AI-Powered Food Delivery Assistant
{'=' * 80}
    """
    print(banner)


def print_startup_info(args):
    """Print startup information"""
    mode = "PRODUCTION" if args.production else "DEVELOPMENT"
    
    logger.info("=" * 80)
    logger.info(f"🚀 Starting FoodieExpress Agent in {mode} mode")
    logger.info("=" * 80)
    logger.info(f"📍 Server: http://{args.host}:{args.port}")
    logger.info(f"📊 Log file: {config.LOG_FILE}")
    logger.info(f"🤖 AI Model: {config.OLLAMA_MODEL if config.USE_OLLAMA else config.GEMINI_MODEL}")
    logger.info(f"🔗 Backend: {config.FASTAPI_BASE_URL}")
    logger.info(f"💾 Redis: {'Enabled' if config.REDIS_ENABLED else 'Disabled (using in-memory storage)'}")
    logger.info("=" * 80)
    logger.info("✨ Features:")
    logger.info("  • Personalized AI Greetings")
    logger.info("  • Multi-Item Orders with Confirmation")
    logger.info("  • Restaurant Reviews & Ratings")
    logger.info("  • Cuisine-Based Search")
    logger.info("  • Context-Aware Conversations")
    logger.info("  • Proactive Review Requests")
    logger.info("=" * 80)
    logger.info("📡 Endpoints:")
    logger.info("  POST /chat          - Process chat messages")
    logger.info("  GET  /health        - Health check")
    logger.info("  POST /clear-session - Clear chat history")
    logger.info("  GET  /              - API information")
    logger.info("=" * 80)


def run_development_server(host: str, port: int, debug: bool = False):
    """Run Flask development server"""
    logger.info("🔧 Running Flask development server...")
    logger.warning("⚠️  This server is not suitable for production!")
    logger.info("=" * 80)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise


def run_production_server(host: str, port: int):
    """Run Waitress production server"""
    try:
        from waitress import serve
        logger.info("🏭 Running Waitress production server...")
        logger.info("=" * 80)
        
        serve(
            app,
            host=host,
            port=port,
            threads=config.FLASK_THREADS,
            channel_timeout=120,
            cleanup_interval=30,
            asyncore_use_poll=True
        )
        
    except ImportError:
        logger.error("❌ Waitress not installed!")
        logger.error("   Install with: pip install waitress")
        logger.error("   Or run in development mode without --production flag")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise


def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Validate configuration
    if not validate_config():
        logger.error("❌ Configuration validation failed!")
        logger.error("   Please fix the errors above and try again.")
        sys.exit(1)
    
    # If validate-only mode, exit now
    if args.validate_only:
        logger.info("✅ Configuration validated successfully!")
        logger.info("   Agent is ready to run.")
        sys.exit(0)
    
    # Print startup information
    print_startup_info(args)
    
    # Start the server
    try:
        if args.production:
            run_production_server(args.host, args.port)
        else:
            run_development_server(args.host, args.port, args.debug)
            
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
