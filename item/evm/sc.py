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


