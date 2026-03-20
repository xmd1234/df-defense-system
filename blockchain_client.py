import json
import datetime
from web3 import Web3


class GanacheBlockchain:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        # 使用 Ganache 自动生成的第一个账户（无需私钥）
        self.w3.eth.default_account = self.w3.eth.accounts[0]

        with open("contract_info.json", "r") as f:
            info = json.load(f)

        self.contract = self.w3.eth.contract(
            address=info["address"],
            abi=info["abi"]
        )

    def is_connected(self):
        return self.w3.is_connected()

    # 上链（替代原来的 add_new_transaction + mine）
    def add_and_mine(self, video_hash, device_id, location, author):
        tx_hash = self.contract.functions.register(
            video_hash, device_id, location, author
        ).transact()
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.blockNumber, tx_hash.hex()

    # 溯源查询（替代原来的 check_video_integrity）
    def check_video_integrity(self, video_hash):
        exists, device_id, location, author, timestamp = \
            self.contract.functions.verify(video_hash).call()

        if exists:
            tx_data = {
                "video_hash": video_hash,
                "device_id": device_id,
                "location": location,
                "author": author,
                "timestamp": str(datetime.datetime.fromtimestamp(timestamp))
            }
            return True, tx_data
        return False, None

    def get_block_height(self):
        return self.w3.eth.block_number

    def get_total_videos(self):
        return self.contract.functions.getTotalCount().call()

    # 获取所有链上记录（用于区块链浏览器页面）
    def get_all_records(self):
        total = self.get_total_videos()
        records = []
        for i in range(total):
            h = self.contract.functions.getHashByIndex(i).call()
            _, device_id, location, author, timestamp = \
                self.contract.functions.verify(h).call()
            records.append({
                "video_hash": h,
                "device_id": device_id,
                "location": location,
                "author": author,
                "timestamp": str(datetime.datetime.fromtimestamp(timestamp))
            })
        return records

    # 获取 Ganache 上所有账户（展示私链节点）
    def get_accounts(self):
        return self.w3.eth.accounts
