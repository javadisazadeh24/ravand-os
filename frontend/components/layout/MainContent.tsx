"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";

type MainContentProps = {
    children: ReactNode;
};

export default function MainContent({ children }: MainContentProps) {
    return (
        <main className="min-h-0 flex-1 overflow-y-auto px-4 py-5 pb-24 sm:px-6 lg:px-8">
            <motion.div
                className="mx-auto min-h-[calc(100vh-9.5rem)] w-full max-w-7xl"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.32, ease: "easeOut", delay: 0.08 }}
            >
                {children}
            </motion.div>
        </main>
    );
}
