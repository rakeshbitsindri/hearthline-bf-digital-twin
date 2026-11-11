import "./globals.css";
import { Frame } from "../components/Frame";

export const metadata = { title: "Hearthline | Blast Furnace Advisory Digital Twin" };

export default function RootLayout({ children }) {
  return (
    <html lang="en" data-theme="scada-slate">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap"
          rel="stylesheet"
        />
        <script src="/twin-knowledge-bundle.js" defer />
      </head>
      <body>
        <div className="banner">
          <span>PUBLIC REFERENCE FURNACE : EVRAZ ZSMK (2013-2016)</span>
          <span>READ-ONLY ADVISORY TWIN : NOT THIS PLANT : NOT LIVE : CC BY 4.0</span>
        </div>
        <Frame>{children}</Frame>
      </body>
    </html>
  );
}
