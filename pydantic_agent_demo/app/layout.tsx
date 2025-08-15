import "./globals.css";
import { ReactNode } from "react";
import { CopilotKit } from "@copilotkit/react-core";

export const metadata = {
  title: 'CSV Chart Agent',
  description: 'AI-powered CSV data analysis and chart generation',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* This points to the runtime we setup in the previous step */}
        <CopilotKit runtimeUrl="/api/copilotkit">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}