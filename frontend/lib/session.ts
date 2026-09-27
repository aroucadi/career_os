"use client";

import { useState, useEffect } from "react";

export interface StoredCV {
  filename: string;
  textContent: string;
  charCount: number;
  parsedAt: string;
  profileId?: string;
  fullName?: string;
  headline?: string;
}

const ANON_SESSION_KEY = "careeros_anon_id";
const ACTIVE_CV_KEY = "careeros_active_cv";

export function getAnonymousSessionId(): string {
  if (typeof window === "undefined") return "anon_default";
  let id = localStorage.getItem(ANON_SESSION_KEY);
  if (!id) {
    id = `anon_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;
    localStorage.setItem(ANON_SESSION_KEY, id);
  }
  return id;
}

export function getStoredCV(): StoredCV | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(ACTIVE_CV_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function storeCV(cv: StoredCV): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACTIVE_CV_KEY, JSON.stringify(cv));
}

export function clearStoredCV(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACTIVE_CV_KEY);
}

export function useAnonymousSession() {
  const [sessionId, setSessionId] = useState<string>("anon_init");
  const [activeCV, setActiveCVState] = useState<StoredCV | null>(null);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  useEffect(() => {
    const id = getAnonymousSessionId();
    const cv = getStoredCV();
    setSessionId(id);
    setActiveCVState(cv);
    setIsHydrated(true);
  }, []);

  const saveCV = (cv: StoredCV) => {
    storeCV(cv);
    setActiveCVState(cv);
  };

  const removeCV = () => {
    clearStoredCV();
    setActiveCVState(null);
  };

  return {
    sessionId,
    activeCV,
    saveCV,
    removeCV,
    isHydrated
  };
}
