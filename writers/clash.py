import yaml
from datatypes.server import *
import logging
from typing import Any
import uuid


def write(data: list[Server], skipunsupported: bool) -> str:
    result: list[dict[str, Any]] = []
    for srv in data:
        logging.debug(f"Writing server {srv.remarks}")
        s: dict[str, Any] = {}

        # basic
        s['server'] = srv.ip
        s['port'] = srv.port
        if srv.password is not None:
            s['password'] = srv.password
        if srv.remarks is not None:
            s['name'] = srv.remarks
        else:
            s['name'] = uuid.uuid5(uuid.uuid1(
                None, 0), ''.join([srv.ip, hex(srv.port)]))
        if srv.protocol == Protocol.custom:
            s['type'] = srv.customProtocol
        else:
            s['type'] = srv.protocol.value

        # other
        if srv.cipher is not None:
            s['cipher'] = srv.cipher
        if srv.udp is not None:
            s['udp'] = srv.udp
        if srv.tls is not None:
            s['tls'] = srv.tls
        if srv.xtls is not None:
            logging.warning("i dont know how to enable xtls only (without flow). if you know, create an issue")
            s['xtls'] = srv.xtls
        if srv.skipCertVerify is not None:
            s['skip-cert-verify'] = srv.skipCertVerify
        if srv.username:
            s['username'] = srv.username
        if srv.sni:
            s['sni'] = srv.sni
        if srv.alpn is not None:
            s['alpn'] = srv.alpn
        if srv.wsoption is not None:
            w = {}
            wso = srv.wsoption
            if wso.path is not None:
                w['path'] = wso.path
            if wso.headers:
                w['headers'] = wso.headers
            if wso.maxEarlyData is not None:
                w['max-early-data'] = wso.maxEarlyData
            if wso.earlyDataHeaderName is not None:
                w['early-data-header-name'] = wso.earlyDataHeaderName
            if w:
                s['ws-opts'] = w
        if srv.h2options is not None:
            h = {}
            ho = srv.h2options
            if ho.path is not None:
                h['path'] = ho.path
            if ho.host:
                h['host'] = ho.host
            if h:
                s['h2-opts'] = h
        if srv.httpoptions is not None:
            h = {}
            ho = srv.httpoptions
            if ho.method is not None:
                h['method'] = ho.method
            if ho.path:
                h['path'] = ho.path
            if ho.headers:
                h['headers'] = ho.headers
            if h:
                s['http-opts'] = h
        if srv.grpcoptions is not None and srv.grpcoptions.grpcServiceName is not None:
            s['grpc-opts'] = {}
            s['grpc-opts']['grpc-service-name'] = srv.grpcoptions.grpcServiceName

        # specific
        if srv.protocol == Protocol.shadowsocks:
            if srv.plugin is not None:
                s['plugin'] = srv.plugin
            if srv.pluginOptions:
                s['plugin-opts'] = srv.pluginOptions
                if 'mux' in s['plugin-opts']:
                    if s['plugin-opts']['mux'] > 0: # type: ignore
                        s['plugin-opts']['mux'] = True
                    else:
                        s['plugin-opts']['mux'] = False
        elif srv.protocol == Protocol.vmess:
            if srv.uuid is not None:
                s['uuid'] = str(srv.uuid)
            if srv.alterID is not None:
                s['alterId'] = srv.alterID
            if srv.serverhostname is not None:
                s['servername'] = srv.serverhostname
            if srv.network is not None:
                s['network'] = srv.network
            if srv.networkheader is not None:
                if srv.network == 'tcp' and srv.networkheader=='http':
                    s['network'] = 'http'
                else:
                    logging.warn('clash does not support networkheader')
                    if skipunsupported:
                        logging.warning("Skip!")
                        continue
        elif srv.protocol == Protocol.socks5:
            pass
        elif srv.protocol == Protocol.http:
            pass
        elif srv.protocol == Protocol.shadowsocksr:
            if srv.obfs is not None:
                s['obfs'] = srv.obfs
            if srv.ssrprotocol is not None:
                s['protocol'] = srv.ssrprotocol
            if srv.obfsParam is not None:
                s['obfs-param'] = srv.obfsParam
            if srv.ssrprotocolParam is not None:
                s['protocol-param'] = srv.ssrprotocolParam
        elif srv.protocol == Protocol.trojan:
            pass
        elif srv.protocol == Protocol.custom:
            pass
        else:
            logging.warn(f"clash does not support {srv.protocol}!")
            if skipunsupported:
                logging.warning("Skip!")
                continue

        result.append(s)
    return yaml.dump({'proxies': result})
