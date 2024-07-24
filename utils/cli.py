import argparse

from utils.conf import Vm, Net, Module


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--module', choices=[
        'tx.trans', 'tx.trace', 'tx.rcpt',
        'blk.block', 'sc.abi', 'parse.trans', 'parse.sg'
    ], type=str, default='tx.trans')
    parser.add_argument('-h', '--hashes', type=str, default='')
    parser.add_argument('-a', '--addresses', type=str, default='')
    parser.add_argument('-o', '--output', type=str, default='out/')

    args = parser.parse_args()


async def main():
    label_fpath = f'out/label.csv'
    tasks = {'eth': [], 'bsc': [], 'pol': []}
    with open(label_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            src, dst = row.get("Src"), row.get("Dst")
            src_tx_hash = row.get("SrcTxHash")
            dst_tx_hash = row.get("DstTxHash")

            tasks[src.lower()].append(src_tx_hash.lower())
            if dst != "" and dst_tx_hash != "":
                tasks[dst.lower()].append(dst_tx_hash.lower())

    batch_size = 64
    for k, v in tasks.items():
        vm = Vm.EVM
        if k == 'eth':
            net = Net.ETH
        elif k == 'bsc':
            net = Net.BSC
        elif k == 'pol':
            net = Net.POL
        module = Module.PS

        out = f"../out"
        parser = CompleteFormParser(vm, net, module)

        for i in tqdm(range(0, len(v), batch_size)):
            await parser.parse(keys=v[i:i+batch_size], mode=Mode.CF, out=out)


asyncio.get_event_loop().run_until_complete(main())

