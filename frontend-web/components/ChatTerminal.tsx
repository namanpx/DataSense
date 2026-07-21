"use client";

import { useState, useRef, useEffect } from "react";
import { askQuestion, ApiError, type AskResponse } from "@/lib/api";
import RouteBadge from "./RouteBadge";
import ChartPanel from "./ChartPanel";
import Header, { type Tab } from "./Header";
import CommandChips from "./CommandChips";
import UploadPanel from "./UploadPanel";

interface Message {
  id: string;
  question: string;
  response?: AskResponse;
  error?: string;
  loading?: boolean;
}

export default function ChatTerminal() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("TERMINAL");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  async function submitQuestion(question: string) {
    if (!question.trim()) return;
    const id = crypto.randomUUID();
    setMessages((prev) => [...prev, { id, question, loading: true }]);
    setInput("");

    try {
      const response = await askQuestion({ question });
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, response, loading: false } : m))
      );
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unexpected error occurred.";
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, error: message, loading: false } : m))
      );
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    submitQuestion(input);
  }

  function handleChip(fillText: string) {
    if (!fillText) {
      inputRef.current?.focus();
      return;
    }
    setInput(fillText);
    inputRef.current?.focus();
  }

  return (
    <div className="mx-auto flex h-screen max-w-container flex-col px-4 py-6 md:px-8">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "SOURCES" ? (
        <UploadPanel />
      ) : activeTab !== "TERMINAL" ? (
        <div className="glass-panel flex flex-1 items-center justify-center px-5 py-4 font-mono text-terminal-code text-outline">
          [{activeTab}] module not yet implemented in this build.
        </div>
      ) : (
        <>
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pb-4">
            {messages.length === 0 && (
              <div className="glass-panel px-5 py-4 font-mono text-terminal-code text-on-surface-variant">
                Terminal initialized. All sensors nominal. I am DataSense AI,
                ready for sovereign computation. What metrics shall we
                visualize today?
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id} className="space-y-2">
                <div className="flex justify-end">
                  <div className="glass-panel max-w-xl px-4 py-3">
                    <div className="mb-1 font-mono text-label-caps text-outline">
                      operator
                    </div>
                    <div className="text-body-md">{m.question}</div>
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="w-full max-w-2xl">
                    {m.loading && (
                      <div className="glass-panel px-4 py-3 font-mono text-terminal-log text-primary">
                        <span className="animate-pulse-cyan">
                          thinking<span className="animate-blink">...</span>
                        </span>
                      </div>
                    )}

                    {m.error && (
                      <div className="glass-panel border-error/40 px-4 py-3 font-mono text-terminal-log text-error">
                        [error] {m.error}
                      </div>
                    )}

                    {m.response && (
                      <div className="glass-panel-active px-4 py-3">
                        <div className="mb-2">
                          <RouteBadge
                            route={m.response.route}
                            extra={
                              m.response.doc_chunks?.length
                                ? `chunks retrieved: ${m.response.doc_chunks.length}`
                                : undefined
                            }
                          />
                        </div>
                        <p className="whitespace-pre-line text-body-md text-on-surface">
                          {m.response.final_answer}
                        </p>
                        {m.response.sql_query && (
                          <pre className="mt-3 overflow-x-auto rounded bg-surface-container-lowest px-3 py-2 font-mono text-terminal-code text-primary">
                            {m.response.sql_query}
                          </pre>
                        )}
                        {m.response.chart_data && (
                          <ChartPanel
                            chart={m.response.chart_data}
                            caption={`interactive visualization: ${m.response.route}_result.dat`}
                          />
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-2">
            <div className="terminal-input-line glass-panel flex items-center gap-3 px-4 py-3">
              <span className="flex items-center gap-0.5 font-mono text-cyan">
                <span className="text-outline">{"{"}</span>
                {">"}
              </span>
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="ask something..."
                className="flex-1 bg-transparent font-mono text-terminal-code text-on-surface outline-none placeholder:text-outline"
              />
              <span className="inline-block h-4 w-1.5 animate-blink bg-cyan" />
              <button
                type="submit"
                aria-label="Run query"
                className="flex h-8 w-8 items-center justify-center rounded-md bg-matrix text-black transition hover:shadow-glow-primary"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M5 12h14M13 6l6 6-6 6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
            <CommandChips onSelect={handleChip} />
          </form>
        </>
      )}
    </div>
  );
}
