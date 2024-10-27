import http.server
import socketserver

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
	def end_headers(self):
		# Add headers to prevent caching
		self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
		self.send_header('Pragma', 'no-cache')
		self.send_header('Expires', '0')
		# Call the original end_headers() method to finish the request
		super().end_headers()

# Set the port you want to serve on
PORT = 8000

# Create an object of the custom handler
Handler = NoCacheHTTPRequestHandler

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
	print(f"Serving at port {PORT}")
	httpd.serve_forever()
