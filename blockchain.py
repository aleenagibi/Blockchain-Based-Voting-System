import hashlib, json, time, os, hmac

class Blockchain:
    def __init__(self):
        print("✅ Blockchain initialized")
        self.chain = []
        self.validators = self._load_validators()
        # Default higher quorum for production realism; can be overridden via POA_THRESHOLD
        default_threshold = 5 if len(self.validators) >= 5 else max(1, (len(self.validators) // 2) + 1)
        try:
            env_thr = int(os.environ.get("POA_THRESHOLD", str(default_threshold)))
        except Exception:
            env_thr = default_threshold
        self.threshold = max(1, min(env_thr, len(self.validators)))
        self.load_from_file()
        if not self.chain:
            self.create_genesis_block()
            self.save_to_file()
        else:
            # Migrate existing blocks to new required_signatures and top up signatures as needed
            self._migrate_required_signatures()
            self.save_to_file()

    def _load_validators(self):
        v = []
        # Core constitutional/oversight bodies
        v.append({"id": "eci", "role": "Election Commission of India (ECI)", "pub": "eci_pub", "secret": os.environ.get("POA_ECI_SECRET", "eci_secret")})
        v.append({"id": "judicial", "role": "Judicial Oversight Panel (High Court–nominated)", "pub": "judicial_pub", "secret": os.environ.get("POA_JUDICIAL_SECRET", "judicial_secret")})
        v.append({"id": "observer", "role": "Accredited Independent Observers (NGO/CSO)", "pub": "observer_pub", "secret": os.environ.get("POA_OBSERVER_SECRET", "observer_secret")})
        # Technical and independent assurance
        v.append({"id": "nic", "role": "National Informatics Centre / CERT-In", "pub": "nic_pub", "secret": os.environ.get("POA_NIC_SECRET", "nic_secret")})
        v.append({"id": "academia", "role": "Academic Consortium (IIT/IIIT/NIT)", "pub": "academia_pub", "secret": os.environ.get("POA_ACADEMIA_SECRET", "academia_secret")})
        v.append({"id": "auditor", "role": "Independent External Audit Firm Pool", "pub": "auditor_pub", "secret": os.environ.get("POA_AUDITOR_SECRET", "auditor_secret")})
        # Federal balance via rotating state pool
        v.append({"id": "state_pool", "role": "State Election Commission (Rotating Pool)", "pub": "state_pub", "secret": os.environ.get("POA_STATE_SECRET", "state_secret")})
        return v

    def _block_header(self, index, timestamp, data, previous_hash, version="1"):
        return {
            "version": version,
            "index": index,
            "timestamp": timestamp,
            "data": data,
            "previous_hash": previous_hash,
        }

    def _hash_header(self, header):
        encoded = json.dumps(header, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _sign(self, validator_secret, header_hash):
        return hmac.new(validator_secret.encode(), header_hash.encode(), hashlib.sha256).hexdigest()

    def _verify(self, validator_secret, header_hash, signature):
        expected = self._sign(validator_secret, header_hash)
        return hmac.compare_digest(expected, signature)

    def create_genesis_block(self):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        header = self._block_header(0, ts, {"voter_id": "0", "vote": "Genesis Block"}, "0")
        header_hash = self._hash_header(header)
        signatures = []
        for v in self.validators:
            sig = self._sign(v["secret"], header_hash)
            signatures.append({"validator": v["id"], "sig": sig})
        block = dict(header)
        block["author"] = self.validators[0]["id"]
        block["signatures"] = signatures
        block["required_signatures"] = self.threshold
        block["hash"] = header_hash
        self.chain.append(block)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        last = self.get_last_block()
        index = len(self.chain)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        header = self._block_header(index, ts, data, last["hash"])
        header_hash = self._hash_header(header)
        author = self.validators[index % len(self.validators)]["id"]
        signatures = []
        for v in self.validators:
            sig = self._sign(v["secret"], header_hash)
            signatures.append({"validator": v["id"], "sig": sig})
            if len(signatures) >= self.threshold:
                break
        block = dict(header)
        block["author"] = author
        block["signatures"] = signatures
        block["required_signatures"] = self.threshold
        block["hash"] = header_hash
        self.chain.append(block)
        self.save_to_file()
        print(f"✅ Block added: {block['index']}")

    def is_valid(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr.get("previous_hash") != prev.get("hash"):
                return False
            header = {
                "version": curr.get("version", "1"),
                "index": curr.get("index"),
                "timestamp": curr.get("timestamp"),
                "data": curr.get("data"),
                "previous_hash": curr.get("previous_hash"),
            }
            recomputed = self._hash_header(header)
            if recomputed != curr.get("hash"):
                return False
            sigs = curr.get("signatures", [])
            if len(sigs) < curr.get("required_signatures", 1):
                return False
            valid_count = 0
            for s in sigs:
                vid = s.get("validator")
                sig = s.get("sig")
                val = next((x for x in self.validators if x["id"] == vid), None)
                if not val:
                    continue
                if self._verify(val["secret"], recomputed, sig):
                    valid_count += 1
            if valid_count < curr.get("required_signatures", 1):
                return False
        return True
    
    def get_validator_ids(self):
        return [v["id"] for v in self.validators]

    def get_validators_full(self):
        return [{"id": v.get("id"), "role": v.get("role", "")} for v in self.validators]

    def _block_header_from_block(self, block):
        return {
            "version": block.get("version", "1"),
            "index": block.get("index"),
            "timestamp": block.get("timestamp"),
            "data": block.get("data"),
            "previous_hash": block.get("previous_hash"),
        }

    def _find_validator(self, validator_id):
        return next((v for v in self.validators if v["id"] == validator_id), None)

    def has_signature(self, block, validator_id):
        sigs = block.get("signatures", [])
        return any(s.get("validator") == validator_id for s in sigs)

    def add_signature_to_block(self, index, validator_id):
        if index < 0 or index >= len(self.chain):
            return False
        block = self.chain[index]
        if self.has_signature(block, validator_id):
            return True
        v = self._find_validator(validator_id)
        if not v:
            return False
        header = self._block_header_from_block(block)
        header_hash = self._hash_header(header)
        sig = self._sign(v["secret"], header_hash)
        block.setdefault("signatures", []).append({"validator": validator_id, "sig": sig})
        self.save_to_file()
        return True

    def _migrate_required_signatures(self):
        """Ensure each block's required_signatures equals current threshold and has sufficient signatures.
        This updates history for demo consistency.
        """
        for idx in range(len(self.chain)):
            block = self.chain[idx]
            # Set required_signatures to current threshold
            block["required_signatures"] = self.threshold
            sigs = block.setdefault("signatures", [])
            # Top up signatures until threshold reached, using available validators
            seen = set(s.get("validator") for s in sigs if s.get("validator"))
            if len(sigs) >= self.threshold:
                continue
            header = self._block_header_from_block(block)
            header_hash = self._hash_header(header)
            for v in self.validators:
                if len(sigs) >= self.threshold:
                    break
                if v["id"] in seen:
                    continue
                sig = self._sign(v["secret"], header_hash)
                sigs.append({"validator": v["id"], "sig": sig})
                seen.add(v["id"])

    def add_signature_latest(self, validator_id):
        if not self.chain:
            return False
        return self.add_signature_to_block(len(self.chain) - 1, validator_id)

    def add_signature_all(self, validator_id):
        """Add the validator's signature to all blocks that lack it."""
        v = self._find_validator(validator_id)
        if not v:
            return 0
        count = 0
        for idx in range(len(self.chain)):
            block = self.chain[idx]
            if self.has_signature(block, validator_id):
                continue
            header = self._block_header_from_block(block)
            header_hash = self._hash_header(header)
            sig = self._sign(v["secret"], header_hash)
            block.setdefault("signatures", []).append({"validator": validator_id, "sig": sig})
            count += 1
        if count:
            self.save_to_file()
        return count
    
    def save_to_file(self):
        try:
            with open("blockchain.json", "w") as f:
                json.dump(self.chain, f, indent=2)
        except Exception as e:
            print(f"Error saving blockchain: {e}")
    
    def load_from_file(self):
        try:
            if os.path.exists("blockchain.json"):
                with open("blockchain.json", "r") as f:
                    self.chain = json.load(f)
                print(f"✅ Loaded existing blockchain with {len(self.chain)} blocks")
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            self.chain = []