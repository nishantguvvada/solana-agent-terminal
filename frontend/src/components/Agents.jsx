import {
  useWallet,
  useConnection
} from "@solana/wallet-adapter-react";

export const Agents = () => {
    const wallet = useWallet();
    const { connection } = useConnection();

    return (
        <>
            <div>
                <div>Agents</div>
                {wallet.publicKey ? <p>{wallet.publicKey.toString()}</p>:<p>Connect to a wallet to proceed</p>}
            </div>
        </>
    )
}