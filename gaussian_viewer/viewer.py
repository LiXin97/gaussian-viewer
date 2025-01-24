import webbrowser
import asyncio
import threading
from aiohttp import web
from .server import GaussianServer

class GaussianViewer:
    def __init__(self, port: int = 6789):
        self.server = GaussianServer(port=port)
        self.port = port
        self._server_thread = None
        self._browser_opened = False
        
    async def start_server(self):
        """Start the server asynchronously"""
        runner = web.AppRunner(self.server.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
    def _run_server(self):
        """Run server in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start server
        loop.run_until_complete(self.start_server())
        
        # Print server info
        print(f"╭──────────────── gaussian-viewer ────────────────╮")
        print(f"│                                                 │")
        print(f"│   Server running at: http://localhost:{self.port:<5}     │") 
        print(f"│                                                 │")
        print(f"╰─────────────────────────────────────────────────╯")
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            loop.close()
        
    def show(self, data):
        """Show the PLY file path or pre-processed SPLAT data"""
        # Start server if not already running
        if self._server_thread is None or not self._server_thread.is_alive():
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()
            
        # Update the PLY file
        self.server.set_ply(data)
        
        # Open browser only if explicitly requested
        if self._browser_opened:
            webbrowser.open(f'http://localhost:{self.port}')
            
    def open_in_browser(self):
        """Explicitly open the viewer in browser"""
        self._browser_opened = True
        webbrowser.open(f'http://localhost:{self.port}')