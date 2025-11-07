# Taproot Asset Transfer on Bitcoin Layer 1

This project demonstrates how to transfer assets on Bitcoin's Layer 1 using Taproot addresses with embedded asset commitments.

## Overview

The system implements a simple asset transfer protocol where:

- **Sender** creates asset metadata and generates a unique Asset ID
- **Receiver** generates a Taproot address derived from the Asset ID
- Assets are transferred via Bitcoin transactions with embedded commitments

## Features

- ✅ Taproot address generation (BIP-341)
- ✅ Asset ID generation from metadata
- ✅ Asset commitment embedding in addresses
- ✅ Normal Taproot key-path transactions
- ✅ UTXO fetching from Mempool.space API
- ✅ Transaction broadcasting to Bitcoin testnet

## Prerequisites

- Python 3.8+
- Bitcoin testnet access
- Mempool.space API access

## Installation

1. Clone the repository:

```bash
cd "taproot assets Layer 1/asset-layer1"
```

2. Install dependencies:

```bash
pip install python-bitcoinutils python-dotenv requests bitcoinlib
```

3. Generate keys:

```bash
python generate_keys.py
```

4. Create `.env` file:

```bash
touch .env
```

5. Add your keys to `.env`:

```env
SENDER_PRIVATE_KEY_WIF=your_sender_private_key_wif
RECEIVER_PRIVATE_KEY_WIF=your_receiver_private_key_wif
```

## Project Structure

```
asset-layer1/
├── assets_layer1.py      # Main implementation
├── generate_keys.py      # Key generation utility
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## Usage

### 1. Fund Sender Address

First, run the script to get your sender's Taproot address:

```bash
python assets_layer1.py
```

Copy the sender address and fund it with testnet BTC:

- Testnet Faucet: https://coinfaucet.eu/en/btc-testnet/

### 2. Run Asset Transfer

Once funded, run the script again to:

- Generate Asset ID from metadata
- Create receiver's Taproot address
- Build and sign the transaction
- Broadcast to Bitcoin testnet

```bash
python assets_layer1.py
```

## How It Works

### 1. Asset ID Generation

```python
def generate_asset_id(asset_metadata, genesis_outpoint, asset_tag):
    asset_data = f"{asset_metadata}|{genesis_outpoint}|{asset_tag}".encode()
    asset_id = hashlib.sha256(asset_data).digest()
    return asset_id
```

The Asset ID is created by hashing:

- Asset metadata (name, description)
- Genesis outpoint (UTXO reference)
- Asset tag (unique identifier)

### 2. Receiver Address Generation

```python
def receiver_address(asset_id):
    priv_asset_key = PrivateKey(b=asset_id)
    pub_asset_key = priv_asset_key.get_public_key()
    tr_asset_script = Script([pub_asset_key.to_x_only_hex(), 'OP_CHECKSIG'])
    receiver_add_obj = pub_asset_key.get_taproot_address([tr_asset_script])
    return receiver_add_obj, receiver_add_str
```

The receiver derives a Taproot address by:

- Converting Asset ID to private key
- Deriving public key
- Creating Taproot script commitment
- Generating P2TR address

### 3. Transaction Flow

```
1. Fetch UTXOs from sender's address
2. Create transaction inputs (UTXOs)
3. Create outputs (receiver + change)
4. Sign with Taproot key-path spend
5. Broadcast to Bitcoin network
```

## Code Components

### Main Functions

| Function               | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `sender_address()`     | Generate sender's Taproot address                 |
| `generate_asset_id()`  | Create unique asset identifier                    |
| `receiver_address()`   | Generate receiver's Taproot address from Asset ID |
| `create_transaction()` | Build unsigned transaction                        |
| `fetch_utxos()`        | Get UTXOs from Mempool API                        |
| `broadcast()`          | Send transaction to network                       |

### Configuration

```python
MEMPOOL_API_URL = "https://mempool.space/testnet/api"
FEE = 200           # Satoshis (transaction fee)
DUST_LIMIT = 300    # Minimum UTXO value
```

## Transaction Example

```
Input:  Sender's Taproot address (funded UTXO)
Output:
  - Receiver's Taproot address (400 sats)
  - Change back to sender (remaining balance - fee)
Fee:    200 satoshis
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Testnet Only**: This is for educational purposes on testnet
2. **Private Keys**: Never commit `.env` file or expose private keys
3. **Asset Validation**: Receiver must validate asset metadata off-chain
4. **No Production Use**: This is a simplified demonstration

## API Endpoints

### Mempool.space Testnet API

- **Get UTXOs**: `GET /address/{address}/utxo`
- **Broadcast TX**: `POST /tx` (raw transaction hex)
- **Block Explorer**: https://mempool.space/testnet

## Troubleshooting

### "No UTXOs found"

- Fund your sender address with testnet BTC
- Wait for 1 confirmation
- Check address on mempool.space/testnet

### "Insufficient funds"

- Ensure UTXO value > amount + fee + dust limit
- Default: 400 + 200 + 300 = 900 satoshis minimum

### "Broadcast error"

- Check transaction format
- Verify signatures
- Ensure inputs are unspent

### "Failed to create address"

- Check private key format in `.env`
- Ensure WIF format is correct for testnet

## Asset Metadata Example

```python
asset_metadata = "HelloWorld"
genesis_outpoint = "txid:vout"  # First UTXO
asset_tag = "TAG001"

# Generates deterministic Asset ID
asset_id = SHA256(asset_metadata|genesis_outpoint|asset_tag)
```

## Limitations

1. **No Asset Registry**: Assets are not tracked on-chain
2. **Off-chain Validation**: Receiver must verify asset metadata separately
3. **Single Asset Type**: Only supports one asset per transaction
4. **No SPV Proofs**: Trust in full node or API provider required

## Future Enhancements

- [ ] Multi-asset transfers
- [ ] Asset registry integration
- [ ] Script-path spending for complex conditions
- [ ] Merkle tree commitments for multiple assets
- [ ] Client-side validation framework

## Resources

- [BIP-341 Taproot](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)
- [BIP-342 Tapscript](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki)
- [python-bitcoinutils Docs](https://github.com/karask/python-bitcoinutils)
- [Mempool.space API](https://mempool.space/docs/api)

## License

MIT License - Educational purposes only

## Disclaimer

This is experimental software for educational purposes. Do not use with real Bitcoin (mainnet). Always test on testnet first.

## Contributing

Contributions welcome! Please test thoroughly on testnet before submitting PRs.

## Support

For issues or questions, please open an issue on GitHub.

---

**Made with ⚡ for Bitcoin Layer 1 Education**
