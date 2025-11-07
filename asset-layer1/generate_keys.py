from bitcoinlib import keys

# Generate a random private key
sender_key = keys.Key(network='testnet')
sender_private_wif = sender_key.wif()
print("Sender Private Key: ", sender_private_wif)

# Generate receiver private key
receiver_key = keys.Key(network='testnet')
receiver_private_wif = receiver_key.wif()
print("Receiver Private Key: ", receiver_private_wif)



