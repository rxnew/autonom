import datetime
import json
import logging
import threading
from typing import Callable, Dict, Any

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionStatus
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicReplyType
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicType

logger = logging.getLogger(__name__)

JobExecutor = Callable[[Dict[str, Any]], bool]


class JobProcessor:
    def __init__(self, client: AWSIoTMQTTThingJobsClient, executor: JobExecutor):
        self._client = client
        self._executor = executor
        self._done = False
        self._started = 0
        self._succeeded = 0
        self._rejected = 0
        self._setup_callbacks(self._client)

    def __call__(self, *args, **kwargs):
        self.process()

    def process(self):
        self._done = False
        self._start_next()

    def is_done(self):
        return self._done

    def get_status(self):
        return {
            'jobsStarted': self._started,
            'jobsSucceeded': self._succeeded,
            'jobsRejected': self._rejected,
        }

    def callback_notify_next(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self._start_next()
        else:
            logger.info('Notify next saw no execution')
            self._done = True

    def callback_start_next_accepted(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self._started += 1
            execution = payload['execution']
            result = self._execute(execution)

            if result:
                self._update_succeeded(execution)
            else:
                self._update_failed(execution)
        else:
            logger.info('Start next saw no execution: ' + message.payload.decode('utf-8'))
            self._done = True

    def callback_start_next_rejected(self, client, userdata, message):
        logger.warning('Start next rejected:' + message.payload.decode('utf-8'))
        self._rejected += 1

    def callback_update_accepted(self, client, userdata, message):
        self._succeeded += 1

    def callback_update_rejected(self, client, userdata, message):
        self._rejected += 1

    def _setup_callbacks(self, client: AWSIoTMQTTThingJobsClient):
        client.createJobSubscription(
            self.callback_notify_next,
            jobExecutionTopicType.JOB_NOTIFY_NEXT_TOPIC,
        )
        client.createJobSubscription(
            self.callback_start_next_accepted,
            jobExecutionTopicType.JOB_START_NEXT_TOPIC,
            jobExecutionTopicReplyType.JOB_ACCEPTED_REPLY_TYPE,
        )
        client.createJobSubscription(
            self.callback_start_next_rejected,
            jobExecutionTopicType.JOB_START_NEXT_TOPIC,
            jobExecutionTopicReplyType.JOB_REJECTED_REPLY_TYPE,
        )

        # '+' indicates a wildcard for jobId in the following subscriptions
        client.createJobSubscription(
            self.callback_update_accepted,
            jobExecutionTopicType.JOB_UPDATE_TOPIC,
            jobExecutionTopicReplyType.JOB_ACCEPTED_REPLY_TYPE,
            '+',
        )
        client.createJobSubscription(
            self.callback_update_rejected,
            jobExecutionTopicType.JOB_UPDATE_TOPIC,
            jobExecutionTopicReplyType.JOB_REJECTED_REPLY_TYPE,
            '+',
        )

    def _start_next(self):
        status_details = {
            'startedAt': '{}'.format(datetime.datetime.now().isoformat()),
        }
        thread = threading.Thread(
            target=self._client.sendJobsStartNext,
            kwargs={
                'statusDetails': status_details,
            },
        )
        thread.start()

    def _update_succeeded(self, execution):
        status_details = {
            'succeededAt': '{}'.format(datetime.datetime.now().isoformat()),
        }
        thread = threading.Thread(
            target=self._client.sendJobsUpdate,
            kwargs={
                'jobId': execution['jobId'],
                'status': jobExecutionStatus.JOB_EXECUTION_SUCCEEDED,
                'statusDetails': status_details,
                'expectedVersion': execution['versionNumber'],
                'executionNumber': execution['executionNumber'],
            },
        )
        thread.start()

    def _update_failed(self, execution):
        status_details = {
            'failedAt': '{}'.format(datetime.datetime.now().isoformat()),
        }
        thread = threading.Thread(
            target=self._client.sendJobsUpdate,
            kwargs={
                'jobId': execution['jobId'],
                'status': jobExecutionStatus.JOB_EXECUTION_FAILED,
                'statusDetails': status_details,
                'expectedVersion': execution['versionNumber'],
                'executionNumber': execution['executionNumber'],
            },
        )
        thread.start()

    def _execute(self, execution):
        logger.info('Executing job ID, version, number: {}, {}, {}'
                    .format(execution['jobId'], execution['versionNumber'], execution['executionNumber']))
        logger.info('With jobDocument: ' + json.dumps(execution['jobDocument']))
        try:
            return self._executor(execution['jobDocument'])
        except Exception as e:
            logger.error('Failed to execute job', e)
            return False
