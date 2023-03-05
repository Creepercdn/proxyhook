'''
ProxyHook
'''

import base64
import importlib
import logging
import pprint
import sys
import os
from typing import Any
import binascii

import chardet
import requests
import tomlkit
import coloredlogs
import requests.adapters
from requests.exceptions import ConnectionError

from datatypes.server import *


def setupLogger():
    coloredlogs.install(fmt="[%(asctime)s %(threadName)s/%(levelname)s] [%(module)s] %(message)s",
                        datefmt="%H:%M:%S", level=logging.DEBUG, stream=sys.stdout)


config: tomlkit.TOMLDocument = None  # type: ignore


def loadConfig():
    global config
    with open("proxyhook.toml", "r") as f:
        config = tomlkit.parse(f.read())


def parse(data: str, source: dict[str, Any], prefix: str = '') -> list[Server]:
    log.info('Start parsing using parser module {}'.format(
        source['type']))
    try:
        parserlib = importlib.import_module(
            "parsers.{}".format(source['type']))
    except ModuleNotFoundError:
        log.fatal("Fatal to import parser library", exc_info=True)
        return []
    result: list[Server] = []

    decodedbytes: bytes | None = None
    try:
        decodedbytes = base64.decodebytes(data.encode('ascii'))
    except (binascii.Error, UnicodeEncodeError):
        log.info('Failed to decode result as base64, maybe unencoded plain text')

    if decodedbytes is not None:
        codec = chardet.detect(decodedbytes)
        decoded = decodedbytes.decode(codec.get('encoding'))
    else:
        decoded = data

    result = parserlib.parse(decoded)
    for srv in result:
        if srv.remarks is not None:
            srv.remarks = ''.join([prefix, srv.remarks])
        else:
            raise ValueError
    return result


def write(data: list[Server], type: str, skipUnsupported: bool) -> str:
    try:
        writerlib = importlib.import_module(
            "writers.{}".format(type))
    except ModuleNotFoundError:
        log.fatal("Fatal to import writer library", exc_info=True)
        return ''

    return writerlib.write(data, skipUnsupported)


setupLogger()

log = logging

# begin

def main():
    log.info("ProxyHook")
    log.info("Loading config")
    loadConfig()
    log.info("Fetching from {} sources".format(
        len(config["sources"])))  # type: ignore

    servers: list[Server] = []

    requests.session().mount('http://', requests.adapters.HTTPAdapter(max_retries=16))
    requests.session().mount('https://', requests.adapters.HTTPAdapter(max_retries=16))

    for name, source in config["sources"].items():  # type: ignore
        if not source.get('enabled', True):
            continue
        log.info("Requesting source {}".format(name))
        okCount = 0
        failCount = 0
        serversBefore = len(servers)  # severs count before
        hashValue: int | None = None

        for url in source['urls']:
            log.info(f"Requesting {url}")

            headers = {}
            if config["requests"]["useragent"]:  # type: ignore
                # type: ignore
                headers["user-agent"] = str(config["requests"]["useragent"])

            response = None
            try:
                response = requests.get(url, headers=headers, stream=True)
            except ConnectionError:
                log.error("Failed to request", exc_info=True)
            log.info("Response: {}".format(repr(response)))
            # log.debug("Data: {}".format(response.text))

            if response and (response.ok or config["requests"]['forceParse']):  # type: ignore
                currenthash = hash(response.text)
                if hashValue is not None and hashValue != currenthash:
                    log.error(
                        f"Hash of the config from {url} is different with the previous one, refusing")
                    log.debug(f"Current {currenthash}, pervious {hashValue}")
                    continue
                else:
                    hashValue = currenthash

                result = parse(response.text, source, f'[{name}] ')
                if result:
                    okCount += 1
                else:
                    failCount += 1
                servers += result

                if not config['requests']['requestAll']:  # type: ignore
                    break

        log.info(
            f"Statistics: Succeeded {okCount}, Failed {failCount}, Unknown (not requested) {len(source['urls'])-okCount-failCount}, Summary {len(source['urls'])}")
        log.info(f'Imported {len(servers)-serversBefore} servers')

    log.info(f"Import {len(servers)} servers from all sources")

    log.info(f"Start writing, current working dir: {os.getcwd()}")
    for id, setting in config['output'].items():
        log.info(
            f"Writing output {id} to {setting['path']} using type {setting['type']}")
        with open(setting['path'], 'w', encoding='utf-8') as f:
            _ = f.write(write(servers, setting['type'], setting['skipUnsupported']))
    log.info(f'Writed to {len(config["output"])} outputs')

    log.info('Done! Have a nice day!')
    return 0

try:
    exit(main())
except KeyboardInterrupt:
    logging.critical("Keyboard interrupt, exiting")
