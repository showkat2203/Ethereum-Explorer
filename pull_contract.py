# export WEB3_INFURA_PROJECT_ID=b586327d0bc040b6a56e574a1e3ae332
# export INFURA_API_KEY=8757247f3db246549c43461ec49a588f
# export INFURA_API_KEY=https://mainnet.infura.io/v3/b586327d0bc040b6a56e574a1e3ae332


from web3 import Web3
from web3.eth import Eth
import pprint

w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/b586327d0bc040b6a56e574a1e3ae332"))

import requests
apipath = 'https://api.etherscan.io/api?'
apikey = "YK9SX9V14RUKKDHYVBTDRFTYKYEKT1ACZU"

def getSourceCode(address):
	payload = {'module':'contract', 'action':'getsourcecode', 'address':address, 'apikey':apikey}
	response = requests.get(apipath, params=payload)

	if response.json()["status"] == 1:
		response = response.json()['result']
	else:
		print("getSourceCode Failed ")
		response = "NotFound"

	return response

def getContractTxStatus(txhash):
	payload = {'module':'proxy', 'action':'eth_getTransactionByHash', 'txhash':txhash, 'apikey':apikey}
	response = requests.get(apipath, params=payload)

	# if len(response.json()["result"]) == 1:
	response = response.json()['result']
	# else:
	# 	print("getContractTxStatus Failed ")

	return response

contract_list = []
contract_cnt = 0

import json
with open('existing_source.txt') as f:
    lines = f.readlines()
    for line in lines:
    	contract_list.append(line)
    	contract_cnt += 1
	
cur_block = w3.eth.getBlock('latest')
prev_block = cur_block.number - 1

found = 0

import os
if not os.path.exists('solidity_source'):
    os.makedirs('solidity_source')

while contract_cnt < 100:
	for tx in cur_block.transactions:
		tx_ad = str(tx.hex())
		retobj = getContractTxStatus(tx_ad)

		if not (retobj.get('to') is None):
			if( retobj['to'] in contract_list):
				continue

			contract = getSourceCode(retobj['to'])
			if( contract == "NotFound"):
				continue

			if not (contract[0].get('SourceCode') is None):
				# print("Tx: ", tx_ad, "To ", retobj['to'])
				my_code = contract[0]['SourceCode']
				# print(type(my_code))
				if(len(my_code) > 10):
					contract_list.append(retobj['to'])
					# found = 1
					contract_cnt += 1
					print("Contract Count: ", contract_cnt)
					with open(os.path.join('/home/sonnet/Desktop/solidity_source', retobj['to'] + ".sol"), "w") as text_file:
						lines = my_code.splitlines()
						for line in lines:
							text_file.write(line)
						# break		
	if( found == 1):
		break

	if(contract_cnt > 200):
		break

	cur_block = w3.eth.getBlock(prev_block)
	prev_block -= 1


with open('existing_source.txt', "w") as text_file:
	for line in contract_list:
		text_file.write(line)