import base64
import asyncio
import signal
import time
import os

import bitcoinrpc

from core_modules.logger import initlogging
from core_modules.blockchain import BlockChain
from core_modules.settings import NetWorkSettings

from masternode_prototype.masternode_logic import MasterNodeLogic


class MasterNodeDaemon:
    def __init__(self):
        # initialize logging
        self.__logger = initlogging(int(0), __name__)
        self.__logger.debug("Started logger")
        self.basedir = os.getcwd()

        # set up BlockChain object
        self.blockchain = self.__connect_to_daemon()

        pastelid_list = self.blockchain.pastelid_list()

        if not len(pastelid_list):
            result = self.blockchain.pastelid_newkey(NetWorkSettings.PASTEL_ID_PASSPHRASE)
            self.pastel_id = result['pastelid']
        else:
            self.pastel_id = pastelid_list[0]['PastelID']

        # self.pastel_id contains bitcoin-address-encoded PastelID public key.
        # It is used in sign/verify interactions with cNode exactly in a given format

        self.logic = MasterNodeLogic(nodenum=0,
                                     blockchain=self.blockchain,
                                     basedir=self.basedir,
                                     pastelid=self.pastel_id)

    def __connect_to_daemon(self):
        while True:
            blockchain = BlockChain(user='rt',
                                    password='rt',
                                    ip='127.0.0.1',
                                    rpcport=19932)
            try:
                blockchain.getwalletinfo()
            except (ConnectionRefusedError, bitcoinrpc.authproxy.JSONRPCException) as exc:
                self.__logger.debug("Exception %s while getting wallet info, retrying..." % exc)
                time.sleep(0.5)
            else:
                self.__logger.debug("Successfully connected to daemon!")
                break
        return blockchain

    def run_event_loop(self):
        # start async loops
        loop = asyncio.get_event_loop()

        # set signal handlers
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        loop.create_task(self.logic.run_rpc_server())
        loop.create_task(self.logic.run_masternode_parser())
        loop.create_task(self.logic.run_ticket_parser())
        loop.create_task(self.logic.run_chunk_fetcher_forever())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # FIXME: such stopping create infinite recursion. Need to close port when stopping.
            # loop.run_until_complete(self.logic.stop_rpc_server())
            loop.stop()
