// Zevy Messenger - Peer-to-Peer Encrypted Messaging
// Copyright (c) 2025, Zevy Contributors. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
//    this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
// 3. Neither the name of Zevy nor the names of its contributors may be used to
//    endorse or promote products derived from this software without specific
//    prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use tfhe::boolean::prelude::*;
use tfhe::boolean::client_key::ClientKey;
use tfhe::boolean::server_key::ServerKey;

// --- REAL ARKWORKS GROTH16 ZKP IMPLEMENTATION ---
use ark_bn254::{Bn254, Fr};
use ark_groth16::{Groth16, ProvingKey, VerifyingKey, Proof};
use ark_relations::r1cs::{ConstraintSynthesizer, ConstraintSystemRef, SynthesisError};
use ark_relations::lc;
use rand::thread_rng;
use ark_serialize::{CanonicalSerialize, CanonicalDeserialize};
use ark_snark::SNARK;

#[derive(Clone)]
struct MultiplyCircuit {
    pub a: Option<Fr>,
    pub b: Option<Fr>,
    pub c: Option<Fr>,
}

impl ConstraintSynthesizer<Fr> for MultiplyCircuit {
    fn generate_constraints(self, cs: ConstraintSystemRef<Fr>) -> Result<(), SynthesisError> {
        let a = cs.new_witness_variable(|| self.a.ok_or(SynthesisError::AssignmentMissing))?;
        let b = cs.new_witness_variable(|| self.b.ok_or(SynthesisError::AssignmentMissing))?;
        let c = cs.new_input_variable(|| self.c.ok_or(SynthesisError::AssignmentMissing))?;

        cs.enforce_constraint(lc!() + a, lc!() + b, lc!() + c)?;
        Ok(())
    }
}

#[pyfunction]
fn generate_zkp_keys() -> PyResult<(String, String)> {
    let mut rng = thread_rng();
    let circuit = MultiplyCircuit { a: None, b: None, c: None };
    
    // Generate the Trusted Setup (pk, vk)
    let (pk, vk) = Groth16::<Bn254>::circuit_specific_setup(circuit, &mut rng)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Setup failed: {:?}", e)))?;
    
    let mut pk_bytes = Vec::new();
    pk.serialize_compressed(&mut pk_bytes).unwrap();
    let mut vk_bytes = Vec::new();
    vk.serialize_compressed(&mut vk_bytes).unwrap();
    
    Ok((hex::encode(pk_bytes), hex::encode(vk_bytes)))
}

#[pyfunction]
fn generate_proof(private_key_hex: String, factor_a: u32, factor_b: u32) -> PyResult<String> {
    let pk_bytes = hex::decode(private_key_hex)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hex err: {:?}", e)))?;
    let pk = ProvingKey::<Bn254>::deserialize_compressed(&pk_bytes[..])
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("De err: {:?}", e)))?;
    
    let mut rng = thread_rng();
    let circuit = MultiplyCircuit { 
        a: Some(Fr::from(factor_a)), 
        b: Some(Fr::from(factor_b)), 
        c: Some(Fr::from(factor_a * factor_b)) 
    };
    
    let proof = Groth16::<Bn254>::prove(&pk, circuit, &mut rng)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Prove failed: {:?}", e)))?;
        
    let mut proof_bytes = Vec::new();
    proof.serialize_compressed(&mut proof_bytes).unwrap();
    
    Ok(hex::encode(proof_bytes))
}

#[pyfunction]
fn verify_proof(public_key_hex: String, product: u32, proof_hex: String) -> PyResult<bool> {
    let vk_bytes = hex::decode(public_key_hex)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hex err: {:?}", e)))?;
    let vk = VerifyingKey::<Bn254>::deserialize_compressed(&vk_bytes[..])
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("De err: {:?}", e)))?;
    
    let proof_bytes = hex::decode(proof_hex)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hex err: {:?}", e)))?;
    let proof = Proof::<Bn254>::deserialize_compressed(&proof_bytes[..])
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("De err: {:?}", e)))?;
    
    let public_input = vec![Fr::from(product)];
    
    let result = Groth16::<Bn254>::verify(&vk, &public_input, &proof)
        .unwrap_or(false);
        
    Ok(result)
}

// --- REAL TFHE-RS BOOLEAN IMPLEMENTATION ---

#[pyclass]
struct HEClient {
    client_key: ClientKey,
}

#[pymethods]
impl HEClient {
    #[new]
    fn new() -> Self {
        // We generate a set of client/server keys for the boolean FHE scheme
        let client_key = ClientKey::new(&tfhe::boolean::parameters::DEFAULT_PARAMETERS);
        HEClient { client_key }
    }

    fn get_evaluation_key<'a>(&self, py: Python<'a>) -> PyResult<&'a PyBytes> {
        let server_key = ServerKey::new(&self.client_key);
        let bytes = bincode::serialize(&server_key).unwrap();
        Ok(PyBytes::new(py, &bytes))
    }

    fn encrypt_bool<'a>(&self, py: Python<'a>, value: bool) -> PyResult<&'a PyBytes> {
        let encrypted = self.client_key.encrypt(value);
        let bytes = bincode::serialize(&encrypted).unwrap();
        Ok(PyBytes::new(py, &bytes))
    }

    fn decrypt_bool(&self, encrypted_bytes: Vec<u8>) -> PyResult<bool> {
        let encrypted: Ciphertext = bincode::deserialize(&encrypted_bytes).unwrap();
        let decrypted = self.client_key.decrypt(&encrypted);
        Ok(decrypted)
    }
}

#[pyclass]
struct HEServer {
    server_key: ServerKey,
}

#[pymethods]
impl HEServer {
    #[new]
    fn new(eval_key: Vec<u8>) -> Self {
        let server_key: ServerKey = bincode::deserialize(&eval_key).unwrap();
        HEServer { server_key }
    }

    fn compute_and<'a>(&self, py: Python<'a>, enc_a: Vec<u8>, enc_b: Vec<u8>) -> PyResult<&'a PyBytes> {
        let ct_a: Ciphertext = bincode::deserialize(&enc_a).unwrap();
        let ct_b: Ciphertext = bincode::deserialize(&enc_b).unwrap();
        
        // Compute Homomorphic AND
        let result = self.server_key.and(&ct_a, &ct_b);
        
        let bytes = bincode::serialize(&result).unwrap();
        Ok(PyBytes::new(py, &bytes))
    }
}

#[pymodule]
fn crypto_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_zkp_keys, m)?)?;
    m.add_function(wrap_pyfunction!(generate_proof, m)?)?;
    m.add_function(wrap_pyfunction!(verify_proof, m)?)?;
    m.add_class::<HEClient>()?;
    m.add_class::<HEServer>()?;
    Ok(())
}
