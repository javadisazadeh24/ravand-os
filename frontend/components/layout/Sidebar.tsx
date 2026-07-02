"use client";

export default function Sidebar() {

  return (

    <aside className="w-72 border-r border-neutral-800 bg-neutral-900 flex flex-col">

      <div className="h-16 flex items-center px-6 border-b border-neutral-800">

        <h1 className="text-xl font-bold">

          RAVAND OS

        </h1>

      </div>

      <nav className="flex-1 p-4 space-y-2">

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Dashboard
        </button>

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Chat
        </button>

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Agents
        </button>

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Plugins
        </button>

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Memory
        </button>

        <button className="w-full text-left p-3 rounded-lg hover:bg-neutral-800">
          Settings
        </button>

      </nav>

    </aside>

  );

}