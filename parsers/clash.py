import yaml
from datatypes.server import *
import logging
from typing import Any
import uuid

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def parseProxies(proxies: list):
    result: list[Server] = []
    for proxy in proxies:
        srv = Server()
        srv.remarks = proxy['name']
        srv.ip = proxy['server']
        srv.port = proxy['port']
        srv.protocol = Protocol(proxy['type'])
        if 'password' in proxy:
            srv.password = proxy['password']
        if 'uuid' in proxy:
            srv.uuid = UUID(proxy['uuid'])
        if 'alterId' in proxy:
            srv.alterID = proxy['alterId']
        if 'cipher' in proxy:
            srv.cipher = proxy['cipher']
        if 'tls' in proxy:
            srv.tls = proxy['tls']
        if 'network' in proxy:
            srv.network = proxy['network']
        if 'ws-opts' in proxy:
            wso = WebSocketOptions()
            w = proxy['ws-opts']
            if 'path' in w:
                wso.path = w['path']
            if 'headers' in w:
                wso.headers = w['headers']
            if 'max-early-data' in w:
                wso.maxEarlyData = w['max-early-data']
            if 'early-data-header-name' in w:
                wso.earlyDataHeaderName = w['early-data-header-name']
            srv.wsoption = wso
        if 'udp' in proxy:
            srv.udp = proxy['udp']
        if 'xtls' in proxy:
            logging.warning("maybe xtls is not a standard option, still accept")
            srv.xtls = proxy['xtls']
        if 'skip-cert-verify' in proxy:
            srv.skipCertVerify = proxy['skip-cert-verify']
        if 'username' in proxy:
            srv.username = proxy['username']
        if 'sni' in proxy:
            srv.sni = proxy['sni']
        if 'h2-opts' in proxy:
            h = proxy['h2-opts']
            ho = H2Options()
            if 'path' in h:
                ho.path = h['path']
            if 'host' in h:
                ho.host = h['host']
            srv.h2options = ho
        if 'http-opts' in proxy:
            h = proxy['http-opts']
            ho = HTTPOptions()
            if 'method' in h:
                ho.method = h['method']
            if 'path' in h:
                ho.path = h['path']
            if 'headers' in h:
                ho.headers = h['headers']
            srv.httpoptions = ho
        if 'grpc-opts' in proxy and 'grpc-service-name' in proxy['grpc-opts']:
            srv.grpcoptions = GRPCOptions()
            srv.grpcoptions.grpcServiceName = proxy['grpc-opts']['grpc-service-name']
        result.append(srv)
    return result

def parse(data: str) -> list[Server]:
    return parseProxies(yaml.load(data, Loader=Loader)['proxies'])