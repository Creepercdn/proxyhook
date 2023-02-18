import enum
from uuid import UUID
from typing import Optional, Union


class Protocol(enum.Enum):
    custom = 0
    vmess = 'vmess'
    vless = 'vless'
    shadowsocks = 'ss'
    trojan = 'trojan'
    socks5 = 'socks5'
    http = 'http'
    shadowsocksr = 'ssr'


class KCPOptions:
    seed: Optional[str] = None

class QUICOptions:
    crypt: Optional[str] = None
    password: Optional[str] = None

class WebSocketOptions:
    path: Optional[str] = None
    headers = {}
    maxEarlyData: Optional[int] = None
    earlyDataHeaderName: Optional[str] = None


class H2Options:
    path: Optional[str] = None
    host = []


class HTTPOptions:
    method: Optional[str] = None
    path = []
    headers = {}


class GRPCOptions:
    grpcServiceName: Optional[str] = None


class Server:
    remarks: Optional[str] = None
    ip: str = ''
    port: int = 0
    password: Optional[str] = None
    protocol: Protocol = Protocol.custom
    customProtocol: str = ""
    network: Optional[str] = None # transport in v2ray
    cipher: Optional[str] = None
    udp: Optional[bool] = None
    tls: Optional[bool] = None
    xtls: Optional[bool] = None
    username: Optional[str] = None # for socks5 & http
    sni: Optional[str] = None # for trojan & http
    flow: Optional[str] = None
    alpn: Optional[list[str]] = None

    wsoption: Optional[WebSocketOptions] = None
    h2options: Optional[H2Options] = None
    httpoptions: Optional[HTTPOptions] = None
    grpcoptions: Optional[GRPCOptions] = None
    kcpoptions: Optional[KCPOptions] = None
    quicoptions: Optional[QUICOptions] = None

    # ss special
    plugin: Optional[str] = None
    pluginOptions: Optional[dict[str, Union[str, bool, int]]] = None

    # vmess special
    uuid: Optional[UUID] = None
    alterID: Optional[int] = None
    skipCertVerify: Optional[bool] = None
    serverhostname: Optional[str] = None
    networkheader: Optional[str] = None

    # ssr special
    obfs: Optional[str] = None
    ssrprotocol: Optional[str] = None
    obfsParam: Optional[str] = None
    ssrprotocolParam: Optional[str] = None

    
