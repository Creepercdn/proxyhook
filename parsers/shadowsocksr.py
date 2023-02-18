import json
from datatypes.server import *
import logging


def parseConfigs(data: list[dict]) -> list[Server]:
    results = []
    for s in data:
        srv = Server()
        srv.protocol = Protocol.shadowsocksr
        srv.remarks = s['remarks']
        srv.ip = s['server']
        srv.port = s['server_port']
        if s['server_udp_port'] != 0:
            logging.warn("server_udp_port is not 0")
        srv.password = s['password']
        srv.cipher = s['method']
        srv.ssrprotocol = s['protocol']
        srv.ssrprotocolParam = s['protocolparam']
        srv.obfs = s['obfs']
        srv.obfsParam = s['obfsparam']
        srv.plugin = s.get('plugin', None)
        if s['udp_over_tcp']:
            logging.warn("udp_over_tcp is not false")
        
        srv.pluginOptions = {}
        for entry in s.get('plugin_opts', '').split(';'):
            if entry=='tls':
                srv.pluginOptions['tls'] = True
            elif '=' in entry:
                lhs, rhs = entry.split('=')
                if not lhs or not rhs:
                    logging.warn("lhs or rhs is None")
                srv.pluginOptions[lhs] = rhs
            elif not entry:
                pass
            else:
                raise ValueError;

        if s.get('plugin_args', ''):
            logging.warn("plugin_args is ignored!")

        results.append(srv)
    return results


def parse(data: str):
    obj = json.loads(data)
    return parseConfigs(obj['configs'])