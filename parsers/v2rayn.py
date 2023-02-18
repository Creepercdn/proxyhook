import json
from datatypes.server import *
import logging
import uuid

def parseConfigs(data: list) -> list[Server]:
    results = []
    for s in data:
        srv = Server()
        if s['configType'] == 1:
            srv.protocol = Protocol.vmess
        elif s['configType']==2:
            srv.protocol = Protocol.vless
        elif s['configType']==3:
            srv.protocol = Protocol.shadowsocks
        elif s['configType']==4:
            srv.protocol = Protocol.socks5
        elif s['configType']==5:
            srv.protocol = Protocol.trojan
        else:
            logging.error(f'{s["configType"]} is not supported')
            continue

        srv.remarks = s['remarks']
        srv.ip = s['address']
        srv.port = s['port']
        if srv.protocol == Protocol.vmess or srv.protocol == Protocol.vless:
            srv.uuid = uuid.UUID(s['id'])
            srv.alterID = s['alterId']
        else:
            srv.password = s['id']
        srv.cipher = s['security']
        srv.network = s['network']
        srv.networkheader = s['headerType']
        srv.serverhostname = s['requestHost']
    
        wso = WebSocketOptions()
        h2o = H2Options()
        hso = HTTPOptions()
        gso = GRPCOptions()
        kcp = KCPOptions()
        qui = QUICOptions()
        wso.path = s['path']
        h2o.host = s['requestHost'].split(',')
        gso.grpcServiceName = s['path']
        hso.path = s['path'].split(',')
        kcp.seed = s['path']
        qui.password = s['path']
        qui.crypt = s['requestHost']
        if srv.protocol == Protocol.vmess or srv.protocol == Protocol.vless or srv.protocol==Protocol.trojan:
            match srv.network:
                case 'tcp':
                    if srv.networkheader == 'http':
                        srv.httpoptions = hso
                case 'h2':
                    srv.h2options = h2o
                case 'ws':
                    srv.wsoption = wso
                case 'grpc':
                    srv.grpcoptions = gso
                case 'kcp':
                    srv.kcpoptions = kcp
                case 'quic':
                    srv.quicoptions = qui
                case other:
                    logging.error(f"unknown network type {other}")
        match s['allowInsecure']:
            case 'false':
                srv.skipCertVerify = False
            case 'true':
                srv.skipCertVerify = True
            case _:
                raise ValueError
        match s['streamSecurity']:
            case '':
                pass
            case None:
                pass
            case 'tls':
                srv.tls = True
            case 'xtls':
                srv.xtls = True
        srv.sni = s['sni']
        srv.alpn = s['alpn']
        
        results.append(srv)
    return results


def parse(data: str):
    obj = json.loads(data)
    return parseConfigs(obj['vmess'])