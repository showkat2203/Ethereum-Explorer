# export WEB3_INFURA_PROJECT_ID=b586327d0bc040b6a56e574a1e3ae332
# export INFURA_API_KEY=8757247f3db246549c43461ec49a588f
# export INFURA_API_KEY=https://mainnet.infura.io/v3/b586327d0bc040b6a56e574a1e3ae332


from web3 import Web3
from web3.eth import Eth
import pprint

# w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/b586327d0bc040b6a56e574a1e3ae332"))

import requests
apipath = 'https://api.etherscan.io/api?'
apikey = "YK9SX9V14RUKKDHYVBTDRFTYKYEKT1ACZU"


# GETH/PARITY Proxy API
def getBlockNumber():
    payload = {'module': 'proxy', 'action':'eth_BlockNumber', 'apikey':apikey}
    return requests.get(apipath, params=payload).json()['result']

def getBlockByNumber(number):
    payload = {'module':'proxy', 'action':'eth_getBlockByNumber', 'tag': hex(number), 'boolean':'true', 'apikey':apikey}
    return requests.get(apipath, params=payload).json()['result']

def getSourceCode(address):
	payload = {'module':'contract', 'action':'getsourcecode', 'address':address, 'apikey':apikey}
	response = requests.get(apipath, params=payload)

	# print(response)
	# print(response.__dict__)
	# print(response.json())
	# print("----------------", response.json()["status"])


	if response.json()["status"] == "1":
		# print("******************************************")
		response = response.json()['result']
	else:
		print("getSourceCode Failed ")
		response = "NotFound"

	return response

def getContractTxStatus(txhash):
	payload = {'module':'proxy', 'action':'eth_getTransactionByHash', 'txhash':txhash, 'apikey':apikey}
	response = requests.get(apipath, params=payload)


	print(response)
	print(response.__dict__)

	if len(response.json()["status"]) == "1":
		response = response.json()['result']
	else:
		print("getContractTxStatus Failed ")

	return response

contract_list = []
contract_cnt = 0

import json
with open('existing_source.txt') as f:
    lines = f.readlines()
    for line in lines:
    	contract_list.append(line)
    	contract_cnt += 1
	

with open('existing_source.txt', "w") as out_text_file:
	for line in contract_list:
		out_text_file.write(line + "\n")

	# cur_block = w3.eth.getBlock('latest')
	cur_block = getBlockNumber()

	cur_block = int(cur_block, 16)

	cur_block = getBlockByNumber(cur_block)

	prev_block = cur_block["number"]
	print(prev_block)
	prev_block = int(prev_block, 16)
	print(prev_block)

	print("Start Block ", prev_block)

	# prev_block = cur_block.json()['result']["number"] - 1

	# print("Second ", cur_block['transactions'])


	found = 0

	import os
	if not os.path.exists('solidity_source'):
	    os.makedirs('solidity_source')

	while contract_cnt < 200:
		for tx in cur_block['transactions']:
			tx_ad = tx['to']
			if( tx_ad in contract_list ):
				continue
			contract = getSourceCode(tx_ad)

			if( contract == "NotFound"):
				continue

			if not (contract[0].get('SourceCode') is None):
				# print("Tx: ", tx_ad, "To ", retobj['to'])
				my_code = contract[0]['SourceCode']
				# print(type(my_code))
				if(len(my_code) > 200):
					contract_list.append(tx_ad)
					
					contract_cnt += 1
					print("Contract Count: ", contract_cnt)
					out_text_file.write(tx_ad + "\n")

					with open(os.path.join('/home/sonnet/Desktop/custom_etherscan/solidity_source', tx_ad + ".sol"), "w") as text_file:
						lines = my_code.splitlines()
						for line in lines:
							text_file.write(line)
							# break		
			if(contract_cnt > 200):
				break

		# if( found == 1):
		# 	break

		# cur_block = w3.eth.getBlock(prev_block)
		cur_block = getBlockByNumber(prev_block)
		prev_block -= 1

	print("End Block ", prev_block)