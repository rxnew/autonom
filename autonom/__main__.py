#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys
import time
import uuid

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient

from .client import AutonomClient

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Autonom - Ansible executor via AWS IoT Jobs')
    parser.add_argument('-c', '--config-path', type=str, required=False, default=None, help='configuration file path')
    parser.add_argument('--thing-name', type=str, required=False, default=None, help='AWS IoT Thing name')
    parser.add_argument('--host-name', type=str, required=False, default=None, help='AWS IoT host name')
    parser.add_argument('--ca-path', type=str, required=False, default=None, help='root CA path')
    parser.add_argument('--key-path', type=str, required=False, default=None, help='private key path')
    parser.add_argument('--cert-path', type=str, required=False, default=None, help='certificate path')
    parser.add_argument('--client-id', type=str, required=False, default=None, help='MQTT client ID')
    parser.add_argument('--interval', type=int, required=False, default=None, help='checking interval seconds')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    config = {}
    config_path = args.config_path

    if not config_path:
        config_path = os.path.expanduser('~/.autonom/config.json')

    if os.path.isfile(config_path):
        with open(config_path, 'r') as fp:
            config = json.load(fp)

    def getarg(name, default=None):
        val = getattr(args, name, None)
        if val is not None:
            return val
        val = config.get(name, default)
        if val is not None:
            return val
        print(f'Required argument `{name}` is not specified.\n', file=sys.stderr)
        parser.print_help()
        exit(1)

    thing_name = getarg('thing_name')
    host_name = getarg('host_name')
    ca_path = getarg('ca_path')
    key_path = getarg('key_path')
    cert_path = getarg('cert_path')
    client_id = getarg('client_id', str(uuid.uuid4()))
    interval = getarg('interval', 60)

    client = AWSIoTMQTTThingJobsClient(client_id, thing_name, 1)
    client.configureEndpoint(host_name, 8883)
    client.configureCredentials(ca_path, key_path, cert_path)
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(5)
    client.connect()

    autonom = AutonomClient(client)
    autonom.start(interval=interval)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
