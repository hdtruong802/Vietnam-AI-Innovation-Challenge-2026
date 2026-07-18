import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VNGov - Trợ lý Thủ tục Hành chính Công",
  description: "Trợ lý hướng dẫn và tiền kiểm hồ sơ dịch vụ công trực tuyến dựa trên cơ sở pháp lý và có trích dẫn nguồn cụ thể.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${lora.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
