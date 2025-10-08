import {
  useWallet,
  useConnection
} from "@solana/wallet-adapter-react";
import { VersionedTransaction, Connection, clusterApiUrl } from "@solana/web3.js";
import { useState } from "react";
import axios from "axios";

export const Agents = () => {
    const [loading, setLoading] = useState(false);
    const { publicKey, signTransaction, sendTransaction } = useWallet();
    const { connection } = useConnection();

    async function signAndSend(txBase64) {
        if (!publicKey) throw new Error("Wallet not connected");

        try {
            const txBytes = Buffer.from(txBase64, "base64");

            console.log("txBytes", txBytes);

            const tx = VersionedTransaction.deserialize(txBytes);

            console.log("tx", tx);

            // const signedTx = await signTransaction(tx);

            // console.log("signedTx", signedTx);

            // const txid = await connection.sendRawTransaction(signedTx.serialize());
            const txid = await sendTransaction(tx, connection);

            console.log("Transaction submitted:", txid);
            return txid;
        } catch(err) {
            console.log(err)
        }
    }

    async function handleClick() {
        setLoading(true);

        const res = await axios.post("http://localhost:8000/execute-task", {
            user_pubkey: publicKey.toString(),
            target_wallet: "7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Dtb"
        })

        console.log(res);
        const tx = res.data.tx;
        console.log("tx", tx);

        try {
        const txid = await signAndSend(tx);
        alert(`Transaction successful: ${txid}`);
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
                <button onClick={handleClick} disabled={loading}>
                    {loading ? "Processing..." : "Initialize Global Config"}
                </button>
            </div>
        </>
    )
}