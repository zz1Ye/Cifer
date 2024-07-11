#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : in.py
@Time   : 2024/7/11 11:19
@Author : zzYe

"""
import asyncio

from web3 import Web3

from item.evm.sc import Contract
from item.evm.tx import Transaction
from settings import URL_DICT
from spider.evm.sc import ContractSpider
from spider.evm.tx import TransactionSpider
from utils.conf import Vm, Net, Module
from utils.req import RPCNode
from utils.web3 import parse_hexbytes_dict


class InputParser:
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

    def parse(self, trans: Transaction, contract_item: Contract):
        function_signature = trans.input[:10]

        input = {'func': '', 'args': {}}
        if len(function_signature) == 10:
            contract = self.w3.eth.contract(
                self.w3.to_checksum_address(contract_item.address),
                abi=contract_item.abi
            )
            function = contract.get_function_by_selector(function_signature)

            function_abi_entry = next(
                (
                    abi for abi in contract.abi if
                    abi['type'] == 'function' and abi.get('name') == function.function_identifier
                ), None)

            if function_abi_entry:
                decoded_input = contract.decode_function_input(trans.input)

                args, formal_params = {}, []
                for param in function_abi_entry['inputs']:
                    param_name, param_type = param['name'], param['type']
                    param_value = decoded_input[1].get(param_name, None)

                    formal_params.append(f"{param_type} {param_name}")
                    if isinstance(param_value, bytes):
                        args[param_name] = '0x' + param_value.hex().lstrip('0')
                    else:
                        args[param_name] = param_value

                input["func"] = f"{function.function_identifier}({','.join(formal_params)})"
                input["args"] = parse_hexbytes_dict(dict(args))

        return input


async def main():
    spider = TransactionSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.TX
    )
    tx = await spider.get(mode='trans', hash='0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8')

    spider = ContractSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.SC
    )
    abi = await spider.get(mode='abi', address='0x609c690e8F7D68a59885c9132e812eEbDaAf0c9e')

    parser = InputParser(
        vm=Vm.EVM,
        net=Net.ETH
    )

    print(tx)
    input = parser.parse(
        Transaction(
            hash=tx.get("hash"),
            block_hash=tx.get("blockHash"),
            block_number=int(tx.get("blockNumber"), 16),
            from_address=tx.get("from"),
            to_address=tx.get("to"),
            value=int(tx.get("value"), 16),
            timestamp=0,
            gas=int(tx.get("gas"), 16),
            gas_price=int(tx.get("gasPrice"), 16),
            input=tx.get("input"),
            nonce=tx.get("nonce"),
            type=tx.get("type"),
            chain_id=int(tx.get("chainId"), 16)
        ),
        Contract(
            address='0x609c690e8F7D68a59885c9132e812eEbDaAf0c9e',
            abi=abi
        )
    )
    print(input)

asyncio.get_event_loop().run_until_complete(main())