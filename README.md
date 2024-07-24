# Cifer

😋 Meet `Cifer`, the blockchain data little wizard, 
stealthily crawling through the web with the agility of a producer-consumer pattern, 
all while keeping it asynchronous for that extra oomph!

> Tip: 基于生产者-消费者的异步区块链数据爬取！

## ✅ Get Ready?

Before you start, please ensure that the virtual environment and network interface keys 
are correctly configured.

1️⃣ VE Setup

Enter the following command in the virtual environment.

```
pip install -r requirements.txt
```

2️⃣ Key Setup

- For Scan API Keys: Apply for API keys on blockchain explorers such as 
[`Etherscan`](https://cn.etherscan.com),
[`Bscscan`](https://bscscan.com), and 
[`Polygonscan`](https://polygonscan.com).
- For Provider API Keys: Apply for node keys on platforms like [`Chainnodes`](https://www.chainnodes.org).

```python
# settings.py
URL_DICT = {
    'evm': {
        'eth': {
            'scan': {
                'domain': 'https://api-cn.etherscan.com/api',
                'keys': [
                    "",
                ]
            },
            'provider': {
                'domain': 'https://mainnet.chainnodes.org',
                'keys': [
                    ""
                ]
            }
        },
        # ...    
    }
    # ...    
}
```


## 🔰 Get Started

Command your desires into data from the command line. For example:

```
python main.py -v evm -n eth -m tx -mode trace -hash 0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8 -o out
```

Here you can use --help to view the meaning of all command arguments:

```
usage: main.py [-h] [-v {evm}] [-n {eth,bsc,pol}] [-m {tx,blk,sc,ps}]
               [-mode {trans,trace,rcpt,abi,block,ts,sg,in,el}] [-hash HASHES]  
               [-a ADDRESSES] [-o OUTPUT] [-bs BATCHSIZE]

optional arguments:
  -h, --help show this help message and exit
  -v {evm}, --vm Select Virtual Machine.
  -n {eth,bsc,pol}, --net Select Network.
  -m {tx,blk,sc,ps}, --module Select Module.
  -mode {trans,trace,rcpt,abi,block,ts,sg,in,el,cf}, --mode Select mode.
  -hash HASHES, --hashes HASHES Transaction or Block Hash List (,)
  -a ADDRESSES, --addresses ADDRESSES Contract Address List (,)
  -o OUTPUT, --output OUTPUT Output Dir
  -bs BATCHSIZE, --batchsize BATCHSIZE Batch Size
```


## 🎉 PCP Power-Up

In the Producer-Consumer Pattern, the main entities involved include: 
Producer (`Pro`), Consumer (`Con`), `Job`, Source Queue (`SQ`), and Job Queue (`JQ`). 
The responsibilities of each entity are as follows:

- `Job`: The fundamental unit of execution for the crawler.
- `SQ`: Holds `Jobs` pending assignment.
- `JQ`: Contains `Jobs` ready for processing.
- `Pro`: Loads `Jobs` from the `SQ` into the `JQ`. 
- `Con`: Pulls and completes `Jobs` from the `JQ`.

Under this pattern, 
the main program first stores `Job` in the `SQ`. 
After that, the `Pro` takes the pending `Jobs` from the `SQ`
and places them into the `JQ`. Subsequently, multiple `Cons`, based on network conditions, 
asynchronously retrieve and execute these ready `Jobs` from the `JQ`, 
ultimately completing the data crawling process.




