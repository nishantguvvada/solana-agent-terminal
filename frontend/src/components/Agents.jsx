import {
  useWallet,
  useConnection
} from "@solana/wallet-adapter-react";
import { VersionedTransaction, TransactionMessage, TransactionInstruction, PublicKey } from "@solana/web3.js";
import { useState } from "react";
import axios from "axios";

export const Agents = () => {
    const [loading, setLoading] = useState(false);
    const [agentFee, setAgentFee] = useState(0);
    const { publicKey, signTransaction } = useWallet();
    const { connection } = useConnection();

    async function signAndSend(ixPayload) {
        if (!publicKey) throw new Error("Wallet not connected");

        const { program_id, keys, data } = ixPayload;

        try {

            const ix = new TransactionInstruction({
                programId: new PublicKey(program_id),
                keys: keys.map(k => ({
                pubkey: new PublicKey(k.pubkey),
                isSigner: k.is_signer,
                isWritable: k.is_writable,
                })),
                data: Buffer.from(data, "base64"),
            });

            const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("finalized");
            const messageV0 = new TransactionMessage({
                payerKey: publicKey,
                recentBlockhash: blockhash,
                instructions: [ix],
            }).compileToV0Message();

            const versionedTx = new VersionedTransaction(messageV0);
            const signedTx = await signTransaction(versionedTx);
            console.log("signed tx:", signedTx);
            const signature = await connection.sendRawTransaction(signedTx.serialize())
            console.log("signature:", signature);
            await connection.confirmTransaction({ signature: signature, blockhash, lastValidBlockHeight });

            console.log("Transaction submitted:", signature);

        } catch(err) {
            console.log(err)
        }
    }

    async function handleExecuteTask() {
        setLoading(true);

        const res = await axios.post("http://localhost:8000/execute-task", {
            user_pubkey: publicKey.toString(),
            target_wallet: "7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Dtb"
        });

        console.log(res);
        const ix = res.data.ix;
        console.log("ix", ix);

        try {
            await signAndSend(ix);
        } catch (err) {
            console.error("Transaction failed", err);
            alert("Transaction failed. Check console.");
        }

        setLoading(false);
    }

    async function handleAdminConfig() {
        setLoading(true);
        console.log("Agent Fee", agentFee);

        const res = await axios.post("http://localhost:8000/config", {
            admin_pubkey: publicKey.toString(),
            agent_fee_lamports: 7
        });

        console.log(res);
        const ix = res.data.ix;
        console.log("ix", ix);

        try {
            await signAndSend(ix);
        } catch (err) {
            console.error("Transaction failed", err);
            alert("Transaction failed. Check console.");
        }

        setLoading(false);
    }

    return (
        <>
            <div>
                <div>Agents</div>
                {publicKey ? <p>{publicKey.toString()}</p>:<p>Connect to a wallet to proceed</p>}
                <button onClick={handleExecuteTask} disabled={loading}>
                    {loading ? "Processing..." : "Execute Task"}
                </button>
                <button onClick={handleAdminConfig} disabled={loading}>
                    {loading ? "Processing..." : "Global Config"}
                </button>
                <input onChange={(value) => {setAgentFee(value*100000000)}}/>
            </div>
        </>
    )
}