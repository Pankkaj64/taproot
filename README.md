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
- ✅ Sender Taproot address that commits to a two-leaf script tree, so it can be spent by key path or script path
- ✅ Taproot key-path transactions (key tweaked with the script tree, one signature per input)
- ✅ Script-path spending with two tapleaf scripts: a receiver-key `OP_CHECKSIG` leaf and a SHA-256 hash-preimage (secret keyword) leaf
- ✅ UTXO fetching from Mempool.space API
- ✅ Transaction broadcasting to Bitcoin testnet

## Prerequisites

- Python 3.8+
- Bitcoin testnet access
- Mempool.space API access

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Pankkaj64/taproot.git
cd taproot/asset-layer1
```

2. Install dependencies:

```bash
pip install bitcoin-utils python-dotenv requests bitcoinlib
```

3. Generate a sender and a receiver testnet key (printed in WIF format):

```bash
python generate_keys.py
```

4. Create your `.env` file from the template:

```bash
cp .env.example .env
```

5. Paste the two keys printed in step 3 into `.env`:

```env
SENDER_PRIVATE_KEY_WIF=your_sender_private_key_wif
RECEIVER_PRIVATE_KEY_WIF=your_receiver_private_key_wif
```

## Project Structure

```
asset-layer1/
├── assets_layer1.py      # Main implementation
├── generate_keys.py      # Key generation utility
├── .env.example          # Template for the required environment variables
└── .env                  # Your keys (create from .env.example, git-ignored)
```

## Usage

### 1. Fund Sender Address

First, run the script to get your sender's Taproot address:

```bash
python assets_layer1.py
```

Copy the sender address and fund it with testnet BTC:

> **Note:** the sender address now commits to the script tree, so it differs from the address printed by earlier versions of this script. Coins sent to an old address can only be spent with the old code (commit `e4fde45`); move them before switching, or fund the new address.

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

The script asks for the amount in sats, then for the spend path: enter `1` for a key-path spend or `2` for a script-path spend. For a script-path spend it then asks which leaf to use (`1` receiver key, `2` secret keyword) and, for the secret leaf, the keyword for each input.

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
    tr_asset_script = Script([pub_asset_key.to_x_only_hex(), 'OP_1'])
    receiver_add_obj = pub_asset_key.get_taproot_address(tr_asset_script)
    receiver_add_str = receiver_add_obj.to_string()
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
2. Create transaction inputs (UTXOs) until they cover amount + fee
3. Create a single output to the receiver (no change output)
4. Sign with a Taproot key-path or script-path spend
5. Broadcast to Bitcoin network
```

## Code Components

### Main Functions

| Function                           | Description                                              |
| ---------------------------------- | -------------------------------------------------------- |
| `sender_address()`                 | Generate sender's Taproot address over the scripts       |
| `generate_asset_id()`              | Create unique asset identifier                           |
| `receiver_address()`               | Generate receiver's Taproot address from Asset ID        |
| `generate_taproot_scripts()`       | Build the receiver-key and hash-preimage tapleaf scripts |
| `create_key_path_transaction()`    | Build, sign (key path) and broadcast the transfer        |
| `create_script_path_transaction()` | Build, sign (script path) and broadcast the transfer     |
| `fetch_utxos()`                    | Get UTXOs from Mempool API                               |
| `broadcast()`                      | Send transaction to network                              |

### Configuration

```python
MEMPOOL_API_URL = "https://mempool.space/testnet/api/"
FEE = 51            # Satoshis (transaction fee)
DUST_LIMIT = 300    # Satoshis (defined, not currently enforced)
```

## Transaction Example

```
Input:  Sender's Taproot address (funded UTXO, at least amount + 51 sats)
Output: Receiver's Taproot address
          - key path:    amount - 51 sats
          - script path: amount
Fee:    everything not sent to the receiver (no change output is created)
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

- Ensure the UTXO value is at least amount + fee
- Example: 400 + 51 = 451 satoshis minimum

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
