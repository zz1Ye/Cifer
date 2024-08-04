from typing import List

from pydantic import Field

from item.meta import Item, check_source, snake_to_camel


class ABI(Item):
    """
    Url
        https://docs.ethersscan.io/api-endpoints/contracts
    """
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.address = source.get('address')
        self.abi = source.get('abi')
        return self

    address: str = Field(default='')
    abi: str = Field(default='')


class Tx(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash', '')
        self.tx_type = source.get('txType', '')
        self.block_number = source.get('blockNumber', '')
        self.timestamp = source.get('timeStamp', '')
        self.from_ = source.get('from', '')
        self.to_ = source.get('to', '')
        self.contract_address = source.get('contractAddress', '')
        self.value = source.get('value', '')
        self.token_name = source.get('tokenName', '')
        self.token_symbol = source.get('tokenSymbol', '')
        self.token_decimal = source.get('tokenDecimal', '')
        self.gas = source.get('gas', '')
        self.gas_price = source.get('gasPrice', '')
        self.gas_used = source.get('gasUsed', '')
        self.cumulative_gas_used = source.get('cumulativeGasUsed', '')
        self.input = source.get('input', '')
        self.method_id = source.get('methodId', '')
        self.function_name = source.get('functionName', '')
        self.trace_id = source.get('traceId', '')
        return self

    hash: str = Field(default='')
    tx_type: str = Field(default='')
    block_number: str = Field(default='')
    timestamp: str = Field(default='')
    from_: str = Field(default='')
    to_: str = Field(default='')
    contract_address: str = Field(default='')
    value: str = Field(default='')
    token_name: str = Field(default='')
    token_symbol: str = Field(default='')
    token_decimal: str = Field(default='')
    gas: str = Field(default='')
    gas_price: str = Field(default='')
    gas_used: str = Field(default='')
    cumulative_gas_used: str = Field(default='')
    input: str = Field(default='')
    method_id: str = Field(default='')
    function_name: str = Field(default='')
    trace_id: str = Field(default='')


class TxList(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        array = []
        for e in source.get('array', []):
            element = Tx()
            element.map(e)
            array.append(element)
        self.array = array
        return self

    array: List[Tx] = Field(default=[])

