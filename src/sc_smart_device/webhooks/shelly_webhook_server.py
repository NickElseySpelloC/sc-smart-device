import threading
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

from sc_foundation import SCLogger

DEFAULT_WEBHOOK_PATH = "/shelly/webhook"


class _ShellyWebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Shelly webhook callbacks.

    Expects the HTTP server to have these attributes attached:
      - controller: the ShellyProvider instance (must implement _push_webhook_event)
      - app_wake_event: threading.Event to signal the main app loop
      - webhook_path: expected URL path (e.g. "/shelly/webhook")
      - logger: SCLogger instance
    """

    @property
    def app_wake_event(self) -> threading.Event:
        return getattr(self.server, "app_wake_event", None)  # pyright: ignore[reportReturnType]

    @property
    def logger(self) -> SCLogger:
        return getattr(self.server, "logger", None)  # pyright: ignore[reportReturnType]

    def _ok(self, body: bytes = b"OK") -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        expected_path = getattr(self.server, "webhook_path", DEFAULT_WEBHOOK_PATH)
        path_only = self.path.split("?")[0]
        query_string = self.path[len(path_only):].lstrip("?") if "?" in self.path else ""

        if expected_path and path_only != expected_path:
            self.send_error(404, "Not Found")
            return

        args: dict = {}
        if query_string:
            args = parse_qs(query_string)
            if self.logger:
                self.logger.log_message(f"Webhook GET {self.path} args={args}", "debug")
        else:
            if self.logger:
                self.logger.log_message(f"Webhook GET {self.path} (no args)", "debug")

        try:
            controller = getattr(self.server, "controller", None)
            if controller is not None:
                args["path"] = self.path  # pyright: ignore[reportArgumentType]
                controller._push_webhook_event(args)  # noqa: SLF001

            wake_event = getattr(self.server, "app_wake_event", None)
            if wake_event is not None:
                wake_event.set()
        except AttributeError:
            pass

        self._ok(b"sc-smart-device webhook")

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Suppress the default per-request stdout logging from BaseHTTPRequestHandler."""
