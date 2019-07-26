import logging
import threading
import time
import traceback

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient

from . import JobProcessor, TaskExecutor
from .util import to_job_executor

logger = logging.getLogger(__name__)


class AutonomClient:
    def __init__(self, job_client: AWSIoTMQTTThingJobsClient):
        self._job_client = job_client
        self._job_processor = JobProcessor(job_client, to_job_executor(TaskExecutor()))

    def process(self):
        self._job_processor()

    def start(self, interval: int = 60):
        thread = threading.Thread(target=self._process_continually, args=(interval,))
        thread.start()

    def _process_continually(self, interval):
        while True:
            try:
                self._job_processor()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
