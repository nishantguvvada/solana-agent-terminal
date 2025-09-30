import { WalletDisconnectButton, WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import "@solana/wallet-adapter-react-ui/styles.css";
import { Agents } from "./Agents";

function Wallet() {

  return (
    <>
        <WalletMultiButton/>
        <WalletDisconnectButton />
    </>
  )
}

export default Wallet
