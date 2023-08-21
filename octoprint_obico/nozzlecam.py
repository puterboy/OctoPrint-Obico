import logging
import time
from octoprint_obico.utils import server_request
from octoprint_obico.webcam_capture import capture_jpeg

_logger = logging.getLogger('octoprint.plugins.obico')

class NozzleCam:

    def __init__(self, plugin):
        self.plugin = plugin
        self.on_first_layer = False
        self.nozzle_config = None

    def start(self):
        self.nozzle_config = self.create_nozzlecam_config()

        while True:
            if not self.nozzle_config: # cut out loop if nozzlecam not set up
                return
            if self.on_first_layer == True:
                if self.plugin._printer.is_printing():
                    try:
                        self.send_nozzlecam_jpeg(capture_jpeg(self.nozzle_config, use_nozzle_config=True))
                    except Exception:
                        _logger.error('Failed to capture jpeg', exc_info=True)
                else:
                    self.notify_server_nozzlecam_complete() # edge case of single layer print - no 2nd layer to stop snapshots
            time.sleep(0.2)

    def send_nozzlecam_jpeg(self, snapshot):
        if snapshot:
            try:
                files = {'pic': snapshot}
                server_request('POST', '/ent/api/nozzle_cam/pic/', self.plugin, timeout=60, files=files, skip_debug_logging=True, headers=self.plugin.auth_headers())
            except Exception:
                _logger.error('Failed to post jpeg', exc_info=True)

    def notify_server_nozzlecam_complete(self):
        self.on_first_layer = False
        if self.nozzle_config is None:
            return
        try:
            data = {'nozzlecam_status': 'complete'}
            server_request('POST', '/ent/api/nozzle_cam/first_layer_done/', self.plugin, timeout=60, data=data, skip_debug_logging=True, headers=self.plugin.auth_headers())
            _logger.debug('server notified 1st layer is done')
        except Exception:
            _logger.error('Failed to notify 1st layer completed', exc_info=True)

    def create_nozzlecam_config(self):
        try:
            printer_id = self.plugin.linked_printer.get('id')
            info = server_request('GET', f'/ent/api/printers/{printer_id}/ext/', self.plugin, timeout=60, skip_debug_logging=True, headers=self.plugin.auth_headers())
            ext_info = info.json().get('ext')
            _logger.debug('Printer ext info: {}'.format(ext_info))
            nozzle_url = ext_info.get('nozzlecam_url', None)
            if not nozzle_url or len(nozzle_url) == 0:
                _logger.error('No nozzlecam config found')
                return None
            else:
                return {
                    'snapshot': nozzle_url,
                    'snapshotSslValidation': False
                }
        except Exception:
            _logger.error('Failed to build nozzle config', exc_info=True)
            return None
