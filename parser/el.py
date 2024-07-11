#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : el.py
@Time   : 2024/7/11 11:18
@Author : zzYe

"""
import asyncio
import warnings
from typing import Dict

from hexbytes import HexBytes
from web3 import Web3

from item.evm.sc import Contract
from item.evm.tx import Receipt
from settings import URL_DICT
from spider.evm.sc import ContractSpider
from spider.evm.tx import TransactionSpider
from utils.conf import Vm, Net, Module
from utils.req import RPCNode
from utils.web3 import parse_hexbytes_dict


class EventLogParser:
    def __init__(self, vm: Vm, net: Net):
        self.vm = vm.value
        self.net = net.value
        self.provider = RPCNode(
            domain=URL_DICT.get(self.vm).get(self.net).get("provider").get("domain"),
            keys=URL_DICT.get(self.vm).get(self.net).get("provider").get("keys"),
        )
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))

    def parse(self, hash: str, contract_dict: Dict[str, Contract]):

        receipt = self.w3.eth.get_transaction_receipt(HexBytes(hash))
        event_logs = []
        for idx, log in enumerate(receipt["logs"]):
            addr = log["address"].lower()
            contract = self.w3.eth.contract(
                self.w3.to_checksum_address(addr), abi=contract_dict[addr].abi
            )
            receipt_event_signature_hex = self.w3.to_hex(
                log["topics"][0]
            )

            events = [e for e in contract.abi if e["type"] == "event"]
            for event in events:
                # Get event signature components
                name = event["name"]
                param_type, param_name = [], []

                for param in event["inputs"]:
                    if "components" not in param:
                        param_type.append(param["type"])
                        param_name.append(param["name"])
                    else:
                        param_type.append(f"({','.join([p['type'] for p in param['components']])})")
                        param_name.append(f"({','.join([p['name'] for p in param['components']])})")

                inputs = ",".join(param_type)
                p_t = ",".join([e.lstrip('(').rstrip(')') for e in param_type]).split(",")
                p_n = ",".join([e.lstrip('(').rstrip(')') for e in param_name]).split(",")
                p_p = [f"{a} {b}" for a, b in zip(p_t, p_n)]

                # Hash event signature
                event_signature_text = f"{name}({inputs})"
                event_signature_hex = self.w3.to_hex(
                    self.w3.keccak(text=event_signature_text)
                )

                # Find match between log's event signature and ABI's event signature
                if event_signature_hex == receipt_event_signature_hex:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        decoded_log = dict(contract.events[event["name"]]().process_receipt(receipt)[0])
                        event_logs.append(
                            {
                                'event': f"{name}({','.join(p_p)})",
                                'args': parse_hexbytes_dict(dict(decoded_log['args']))
                            }
                        )
                        break
        return event_logs


async def main():
    hash = '0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8'
    address = '0x609c690e8F7D68a59885c9132e812eEbDaAf0c9e'

    spider = TransactionSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.TX
    )
    tx = await spider.get(mode='rcpt', hash=hash)
    trace = await spider.get(mode='trace', hash=hash)

    addresses = list(
        set([l.get("address").lower() for l in tx.get("logs")])
    )

    contract_dict = {}
    spider = ContractSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.SC
    )
    for i in range(len(addresses)):
        try:
            addr = next(
                t["action"]["to"].lower()
                for t in trace
                if (
                        t["action"]["callType"].lower() == "delegatecall"
                        and t["action"]["from"].lower() == addresses[i].lower()
                )
            )
        except StopIteration:
            addr = addresses[i]

        contract_dict[addresses[i]] = Contract(
            address=addresses[i],
            abi=await spider.get(mode='abi', address=addr)
        )

    parser = EventLogParser(
        vm=Vm.EVM,
        net=Net.ETH
    )

    event_logs = parser.parse(
        hash, contract_dict
    )
    print(len(event_logs))


asyncio.get_event_loop().run_until_complete(main())
