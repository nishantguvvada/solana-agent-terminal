import { WalletDisconnectButton, WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import "@solana/wallet-adapter-react-ui/styles.css";
import { Agents } from "./Agents";

function Wallet() {

  return (
    <>
      <div>
      <nav className="bg-black bg-[radial-gradient(circle_800px_at_center,rgba(213,197,255,0.5),transparent)] dark:bg-gray-900 fixed w-full z-20 top-0 start-0 border-b border-gray-200 dark:border-gray-600">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <a href="https://flowbite.com/" className="flex items-center space-x-3 rtl:space-x-reverse">
              <span className="self-center text-white text-2xl font-semibold whitespace-nowrap dark:text-black">Solana Agent Terminal</span>
          </a>
          <div className="flex gap-4 md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
            <div className="hidden md:block"><WalletMultiButton/></div>
            <div className="hidden md:block"><WalletDisconnectButton/></div>
            <button data-collapse-toggle="navbar-sticky" type="button" className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-sticky" aria-expanded="false">
              <span className="sr-only">Open main menu</span>
              <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h15M1 7h15M1 13h15"/>
              </svg>
            </button>
          </div>
        </div>
      </nav>
    </div>
    </>
  )
}

export default Wallet
