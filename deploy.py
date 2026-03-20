import json
from web3 import Web3
from solcx import compile_source, install_solc

install_solc("0.8.0")

with open("VideoRegistry.sol", "r") as f:
    source_code = f.read()

compiled = compile_source(
    source_code,
    output_values=["abi", "bin"],
    solc_version="0.8.0"
)
contract_interface = compiled["<stdin>:VideoRegistry"]

# 连接 Ganache 本地私链
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("连接状态:", w3.is_connected())

# 使用 Ganache 自动生成的第一个账户
deployer = w3.eth.accounts[0]

Contract = w3.eth.contract(
    abi=contract_interface["abi"],
    bytecode=contract_interface["bin"]
)

tx_hash = Contract.constructor().transact({"from": deployer})
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ 合约部署成功！地址: {receipt.contractAddress}")

with open("contract_info.json", "w") as f:
    json.dump({
        "address": receipt.contractAddress,
        "abi": contract_interface["abi"]
    }, f, indent=2)

print("合约信息已保存到 contract_info.json")
