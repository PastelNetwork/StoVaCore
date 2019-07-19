import base64

from core_modules.http_rpc import RPCClient
from core_modules.helpers import get_nodeid_from_pubkey
from core_modules.logger import initlogging


class ClientNodeManager:
    def __init__(self, nodenum, privkey, pubkey, blockchain):
        self.__nodenum = nodenum
        self.__logger = initlogging('', __name__)
        self.__privkey = privkey
        self.__pubkey = pubkey
        self.__blockchain = blockchain

    def get_masternode_ordering(self, blocknum):
        mn_rpc_clients = []
        workers = self.__blockchain.masternode_workers(blocknum)
        for node in workers:
            py_pub_key = node['pyPubKey']
            pubkey = base64.b64decode(py_pub_key)

            node_id = get_nodeid_from_pubkey(pubkey)
            ip, py_rpc_port = node['pyAddress'].split(':')
            rpc_client = RPCClient(self.__nodenum, self.__privkey, self.__pubkey,
                                   node_id, ip, py_rpc_port, pubkey)
            mn_rpc_clients.append(rpc_client)
        return mn_rpc_clients

    def get_rpc_client_for_masternode(self, masternode):
        py_pub_key = masternode['pyPubKey']
        pubkey = base64.b64decode(py_pub_key)

        node_id = get_nodeid_from_pubkey(pubkey)
        ip, py_rpc_port = masternode['pyAddress'].split(':')
        rpc_client = RPCClient(self.__nodenum, self.__privkey, self.__pubkey,
                               node_id, ip, py_rpc_port, pubkey)
        return rpc_client
