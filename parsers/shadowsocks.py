import json
from datatypes.server import *
import logging


def parseConfigs(data: list) -> list[Server]:
    results = []
    for s in data:
        srv = Server()
        srv.protocol = Protocol.shadowsocks
        srv.ip = s['server']
        srv.port = s['server_port']
        srv.password = s['password']
        srv.cipher = s['method']
        srv.plugin = s['plugin']
        srv.remarks = s['remarks']

        srv.pluginOptions = {}
        for entry in s['plugin_opts'].split(';'):
            if entry=='tls':
                srv.pluginOptions['tls'] = True
            elif '=' in entry:
                lhs, rhs = entry.split('=')
                if not lhs or not rhs:
                    logging.warn("lhs or rhs is None")
                else:
                    if lhs=='mux':
                        rhs = int(rhs)
                    srv.pluginOptions[lhs] = rhs
            else:
                raise ValueError;

        if 'mode' not in srv.pluginOptions:
            srv.pluginOptions['mode'] = 'websocket'

        if s['plugin_args']:
            logging.warn("plugin_args is ignored!")
        
        results.append(srv)
    return results


def parse(data: str):
    obj = json.loads(data)
    return parseConfigs(obj['configs'])
