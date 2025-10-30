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
    const [uniqueKey, setUniqueKey] = useState("default");
    const [targetKey, setTargetKey] = useState("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Dtb");
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

        } catch(err) {
            console.log(err)
        }
    }

    async function handleExecuteTask() {
        setLoading(true);

        const res = await axios.post("http://localhost:8000/execute-task", {
            user_pubkey: publicKey.toString(),
            target_wallet: targetKey
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

        const res = await axios.post("http://localhost:8000/config", {
            admin_pubkey: publicKey.toString(),
            unique_key: uniqueKey,
            agent_fee_lamports: parseInt(agentFee)
        });

        console.log(res);
        const ix = res.data.ix;
        console.log("ix", ix);

        try {
            await signAndSend(ix);
            alert("Transaction Success.");
        } catch (err) {
            console.error("Transaction failed", err);
            alert("Transaction failed. Check console.");
        }

        setLoading(false);
    }

    return (
        <>
            <div  className="pt-30 flex flex-col items-center justify-center gap-8">

                {publicKey ? <p>{publicKey.toString()}</p>:<p className="self-center text-white text-2xl font-semibold whitespace-nowrap dark:text-black">Connect to a wallet to proceed</p>}
                
                <div class="relative max-w-sm p-6 rounded-2xl bg-gradient-to-b from-[#0e0a1a] to-[#141026] border border-[#2e1f47] shadow-[0_0_30px_rgba(124,58,237,0.2)] text-white hover:shadow-[0_0_40px_rgba(168,85,247,0.3)] transition-all duration-300">

                    <div class="flex justify-between items-start mb-4">
                        <div>
                        <h2 class="text-2xl font-semibold">TradeMaster AI</h2>
                        <span class="inline-block mt-2 px-3 py-1 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ACTIVE</span>
                        </div>
                        <div class="text-right">
                        <p class="text-sm text-gray-400">Performance</p>
                        <p class="text-2xl font-bold text-purple-400">94%</p>
                        </div>
                    </div>

                    <p class="text-gray-300 leading-relaxed mb-5">
                        Advanced trading agent specialized in analyzing market patterns and executing optimal trades on Solana DEXs.
                        Uses machine learning to identify profitable opportunities in real-time.
                    </p>

                    <div class="mb-5">
                        <p class="text-sm text-gray-400 mb-2 tracking-wide">CAPABILITIES</p>
                        <div class="flex flex-wrap gap-2">
                        <span class="px-3 py-1 text-xs border border-purple-500/40 rounded-full text-purple-300 bg-purple-900/30">DEX Trading</span>
                        <span class="px-3 py-1 text-xs border border-purple-500/40 rounded-full text-purple-300 bg-purple-900/30">Market Analysis</span>
                        <span class="px-3 py-1 text-xs border border-purple-500/40 rounded-full text-purple-300 bg-purple-900/30">Risk Management</span>
                        <span class="px-3 py-1 text-xs border border-purple-500/40 rounded-full text-purple-300 bg-purple-900/30">Liquidity Pooling</span>
                        </div>
                    </div>

                    <div class="border-t border-purple-500/20 pt-3 flex justify-between items-center text-sm text-gray-400">
                        <span>Solana Agent</span>
                        <div class="flex items-center space-x-2">
                        <span class="h-2 w-2 bg-emerald-400 rounded-full"></span>
                        <span>On-chain</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-row gap-4">
                    <div className="flex flex-col items-center justify-center gap-2 mt-10 w-full p-6 border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
                        <h5 className="text-center my-2 text-2xl font-bold tracking-tight text-gray-900 text-white">Set Global Config</h5>
                        <label className="mt-2 mb-2 text-base font-normal text-white dark:text-gray-400">Set Agent Fee</label>
                        <input className="max-w-xl bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" type="number" onChange={(e) => {setAgentFee(e.target.value)}}/>
                        <label className="mt-2 mb-2 text-base font-normal text-white dark:text-gray-400">Set Unique Key</label>
                        <input className="max-w-xl bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" type="text" onChange={(e) => {setUniqueKey(e.target.value)}}/>
                        <button className="mt-4 inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800" onClick={handleAdminConfig} disabled={loading}>
                            {loading ? "Processing..." : "Global Config"}
                        </button>
                    </div>
                    <div className="flex flex-col items-center justify-center gap-2 mt-10 w-full p-6 border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700"> 
                        <h5 className="text-center my-2 text-2xl font-bold tracking-tight text-gray-900 text-white">Set Wallet to copy</h5>
                        <label className="mt-2 mb-2 text-base font-normal text-white dark:text-gray-400">Target Public Key</label>
                        <input className="max-w-xl bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" type="text" onChange={(e) => {setTargetKey(e.target.value)}}/>
                        <button className="mt-4 inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800" onClick={handleExecuteTask} disabled={loading}>
                            {loading ? "Processing..." : "Execute Task"}
                        </button>
                    </div>
                </div>
            </div>
        </>
    )
}