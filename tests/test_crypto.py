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
