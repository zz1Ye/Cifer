HEADERS_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 '
    'Safari/537.36 Edge/16.16299',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
]


APIS = {
    "eth": "https://api.etherscan.io/api",
    "bsc": "",
    "pol": ""
}


API_KEYS = {
    "eth": [
        "7MM6JYY49WZBXSYFDPYQ3V7V3EMZWE4KJK"
    ],
    "bsc": [
        "S7N1S396ZB98XYC5WQ3IWEPDBGJKESXH5B"
    ],
    "pol": [
        "7BTFI86WFGAAD91X2AGSF7YWBWC3M4R39S"
    ]
}

PROVIDERS = {
    "eth": [
        "https://mainnet.chainnodes.org/f21d29b2-62e8-490c-97fe-01ac44dd6344"
    ],
    "bsc": [
        "https://bsc-mainnet.chainnodes.org/f21d29b2-62e8-490c-97fe-01ac44dd6344"
    ],
    "pol": [
        "https://polygon-mainnet.chainnodes.org/f21d29b2-62e8-490c-97fe-01ac44dd6344"
    ]
}

RPCS = {
    "evm": {
        "blk": {
            "block": {
                "url": "",
                "method": "POST",
                "headers": {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
                "payload": {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "eth_getBlockByNumber",
                    "params": ["", True],
                },
            }
        },
        "sc": {
            "abi": {
                "params": {
                    'module': 'contract',
                    'action': 'getabi',
                    'address': "",
                    'apikey': ""
                }
            }
        },
        "tx": {
            "trans": {
                "url": "",
                "method": "POST",
                "headers": {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
                "payload": {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionByHash",
                    "params": [""],
                },
            },
            "rcpt": {
                "url": "",
                "method": "POST",
                "headers": {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
                "payload": {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionReceipt",
                    "params": [""]
                },
            },
            "trace": {
                "url": "",
                "method": "POST",
                "headers": {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
                "payload": {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "trace_transaction",
                    "params": [""]
                },
            }
        }
    }
}
