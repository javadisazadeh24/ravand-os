import type { ReactNode } from "react";

import AppShell from "./AppShell";

type LayoutProps = {
    children: ReactNode;
};

export default function Layout({ children }: LayoutProps) {
    return <AppShell>{children}</AppShell>;
}
