import "./globals.css";

export const metadata = {
  title: "Financial NLP Sentiment",
  description: "Analyze financial text sentiment with a FastAPI backend.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
