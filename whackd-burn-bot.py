from etherscan import Etherscan
from web3 import Web3
import asyncio
import tweepy
import json
import yaml

infura_url = 'https://mainnet.infura.io/v3/fe6e0bd4a58d40558f357870c0a981e4'
web3 = Web3(Web3.HTTPProvider(infura_url))

whackd_contract_address = '0xCF8335727B776d190f9D15a54E6B9B9348439eEE'
whackd_contract_abi = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"tokens","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokens","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"tokenOwner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"acceptOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeSub","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"tokens","type":"uint256"}],"name":"transfer","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeDiv","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"tokens","type":"uint256"},{"name":"data","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeMul","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[],"name":"newOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"tokenAddress","type":"address"},{"name":"tokens","type":"uint256"}],"name":"transferAnyERC20Token","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"tokenOwner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeAdd","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"name":"_newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"tokens","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"tokenOwner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"tokens","type":"uint256"}],"name":"Approval","type":"event"}]')
contract = web3.eth.contract(
    address=whackd_contract_address, abi=whackd_contract_abi)

etherscan = 0
twitter = 0

counter = 0
whackd_countdown = 1000

# setup twitter and etherscan api config
def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
        configure_etherscan(config)
        configure_twitter(config)


def configure_etherscan(config):
    global etherscan
    etherscan_api_key = config["etherscan"]["api-key"]
    etherscan = Etherscan(etherscan_api_key)


def configure_twitter(config):
    global twitter
    consumer_key = config["twitter"]["consumer-key"]
    consumer_secret = config["twitter"]["consumer-secret"]
    access_token = config["twitter"]["access-token"]
    access_token_secret = config["twitter"]["access-token-secret"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter = tweepy.API(auth)


# calulcate the total percentage of WHACKD tokens that are sent to the burn address
def get_burn_percentage():
    max_supply = 1000000000000000000000000000
    total_supply = int(
        etherscan.get_total_supply_by_contract_address(whackd_contract_address))
    return round(100 - total_supply / max_supply * 100, 2)


# monitor each token transfer and tweet the remaining transactions until somebody gets whackd
# if defined numbers of transfers are left
def on_token_transfer(event):
    global twitter
    global counter
    global whackd_countdown

    counter += 1
    if (counter % 2 == 0):
        whackd_countdown -= 1

        if (whackd_countdown == 0):
            whackd_countdown = 1000
            counter = 0

            tweet_to_publish = 'Sorry ' + json.loads(Web3.toJSON(event))[
                "args"]["from"] + ' you just got $WHACKED.   #WHACKD #McAfeeDidntUninstallHimself #BTC #ETH #Cryptocurrency'
            twitter.update_status(tweet_to_publish)

            tweet_to_publish = str(
                get_burn_percentage()) + '% of the total suppy has been $WHACKED.   #WHACKD #McAfeeDidntUninstallHimself #BTC #ETH #Cryptocurrency'
            twitter.update_status(tweet_to_publish)

        elif (whackd_countdown == 1
                or whackd_countdown == 2
                or whackd_countdown == 3
                or whackd_countdown == 10
                or whackd_countdown == 50
                or whackd_countdown % 100 == 0):
            tweet_to_publish = str(
                whackd_countdown) + ' transactions left until sombody gets $WHACKED.   #WHACKD #McAfeeDidntUninstallHimself #BTC #ETH #Cryptocurrency'
            twitter.update_status(tweet_to_publish)


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "transfer" event
# this loop runs on a poll interval
async def tweet_loop(event_filter, poll_interval):
    while True:
        for transfer in event_filter.get_new_entries():
            on_token_transfer(transfer)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "transfer" event for the uniswap factory contract
# run an async loop
# try to run the tweet_loop function above every 2 seconds
def main():
    load_config("config.yaml")

    event_filter = contract.events.Transfer.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                tweet_loop(event_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()
