import logging
import time
from octoprint_obico.utils import server_request
from octoprint_obico.webcam_capture import capture_jpeg
_logger = logging.getLogger('obico.celestrius')

class Celestrius:

    def __init__(self, plugin):
        self.plugin = plugin
        self.on_first_layer = False

    def start(self):
        #TODO block users with no nozzle cam config
        while True:
            if self.on_first_layer == True:
                try:
                    #TODO replace webcam config with nozzle cam config
                    self.send_celestrius_jpeg(capture_jpeg(self.plugin)) #TODO replace argument with nozzle cam config
                    _logger.debug('Celestrius Jpeg captured & sent')
                except Exception as e:
                    _logger.warning('Failed to capture jpeg - ' + str(e))
            time.sleep(0.2) #TODO how many photos do we want?

    def send_celestrius_jpeg(self, snapshot):
        if snapshot: #TODO update with new endpoint & data
            try:
                files = {'pic': snapshot}
                data = {'viewing_boost': 'true'}
                server_request('POST', '/ent/api/nozzle_cam/pic/', self.plugin, timeout=60, files=files, data=data, skip_debug_logging=True, headers=self.plugin.auth_headers())
            except Exception as e:
                _logger.warning('Failed to post jpeg - ' + str(e))

    def notify_server_celestrius_complete(self):
        self.on_first_layer = False
        try: #TODO update with new endpoint & data
            data = {'celestrius_status': 'complete'}
            server_request('POST', '/ent/api/nozzle_cam/first_layer_done/', self.plugin, timeout=60, files={}, data=data, skip_debug_logging=True, headers=self.plugin.auth_headers())
            _logger.debug('server notified celestrius is done')
        except Exception as e:
            _logger.warning('Failed to notify celestrius completed' + str(e))
