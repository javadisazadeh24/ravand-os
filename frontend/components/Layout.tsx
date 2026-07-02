import type { ReactNode } from "react";

import Layout from "@/components/layout/Layout";

type RootLayoutProps = {
    children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
    return <Layout>{children}</Layout>;
}
