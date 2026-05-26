# Zevy Messenger - Peer-to-Peer Encrypted Messaging
# Copyright (c) 2025, Zevy Contributors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of Zevy nor the names of its contributors may be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pytest
import crypto_rust

def test_fhe_boolean():
    """
    Test real FHE boolean operations using tfhe-rs.
    Alice encrypts True and False. Bob computes an AND gate homomorphically.
    """
    client = crypto_rust.HEClient()
    eval_key = client.get_evaluation_key()
    
    # Alice encrypts 
    enc_true = client.encrypt_bool(True)
    enc_false = client.encrypt_bool(False)
    
    # Bob evaluates AND homomorphically (without decrypting)
    server = crypto_rust.HEServer(eval_key)
    enc_result = server.compute_and(enc_true, enc_false)
    
    # Alice decrypts the result
    result = client.decrypt_bool(enc_result)
    assert result is False

def test_zkp_groth16():
    """
    Test ZKP proof generation (Groth16/Schnorr simulation).
    """
    pk, vk = crypto_rust.generate_zkp_keys()
    
    # Prove knowledge of factors (e.g. 3 and 11 for 33)
    proof = crypto_rust.generate_proof(pk, 3, 11)
    
    # Verify the proof against public input 33
    is_valid = crypto_rust.verify_proof(vk, 33, proof)
    assert is_valid is True
