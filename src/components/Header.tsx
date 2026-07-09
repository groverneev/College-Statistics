"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";
import { useSession, signIn, signOut } from "next-auth/react";
import { useSavedSchools } from "@/components/SavedSchoolsContext";

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const { data: session } = useSession();
  const { isLoggedIn, promptSignIn } = useSavedSchools();
  const signedIn = isLoggedIn || !!session;
  const isHome = usePathname() === "/";

  useEffect(() => {
    if (!isHome) return;
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [isHome]);

  // Close user menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navLinks = [
    { href: "/schools", label: "Browse Schools" },
    { href: "/my-schools", label: "My Schools" },
    { href: "/trends", label: "Trends" },
    { href: "/uc", label: "UC Explorer" },
  ];

  const desktopLinkClass = isHome
    ? "header-dark-link font-medium text-base"
    : "text-gray-600 hover:text-gray-900 font-medium transition-colors text-base";

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 ${
        isHome ? "header-dark" : "bg-white shadow-sm"
      }`}
      style={
        isHome
          ? {
              borderBottom: `1px solid rgba(0, 0, 0, ${
                scrolled ? 0.08 : 0
              })`,
              transition: "border-color 0.2s ease",
            }
          : undefined
      }
    >
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span
              className={`text-xl font-bold ${
                isHome ? "header-dark-logo" : "text-gray-800"
              }`}
            >
              College Statistics
            </span>
          </Link>

          {/* Desktop Navigation + Auth — grouped right */}
          <div className="hidden md:flex items-center space-x-8 ml-auto">
            <nav className="flex items-center space-x-6">
              {navLinks.map((link) => {
                const className = desktopLinkClass;
                // "My Schools" is gated: signed out, open the sign-in popup instead of navigating
                if (link.href === "/my-schools" && !signedIn) {
                  return (
                    <button
                      key={link.href}
                      onClick={() => promptSignIn()}
                      className={className}
                    >
                      {link.label}
                    </button>
                  );
                }
                return (
                  <Link key={link.href} href={link.href} className={className}>
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          <div className="flex items-center">
            {session ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 rounded-full focus:outline-none"
                >
                  {session.user?.image ? (
                    <Image
                      src={session.user.image}
                      alt={session.user.name ?? "User"}
                      width={32}
                      height={32}
                      className="rounded-full"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-sm font-medium">
                      {session.user?.name?.[0] ?? "U"}
                    </div>
                  )}
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {session.user?.name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {session.user?.email}
                      </p>
                    </div>
                    <button
                      onClick={() => signOut()}
                      className="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => signIn("google")}
                className="flex items-center space-x-2 bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span>Sign in</span>
              </button>
            )}
          </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            className={`md:hidden ml-auto p-2 rounded-md ${
              isHome
                ? "header-dark-link"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div
            className={`md:hidden border-t py-4 ${
              isHome ? "header-dark-border" : "border-gray-100 bg-white"
            }`}
            style={isHome ? { backgroundColor: "#f7f8fa" } : undefined}
          >
            <nav className="flex flex-col space-y-4">
              {navLinks.map((link) => {
                const className = isHome
                  ? "header-dark-link font-medium px-2 py-1 text-left"
                  : "text-gray-600 hover:text-gray-900 font-medium px-2 py-1 text-left";
                // "My Schools" is gated: signed out, open the sign-in popup instead of navigating
                if (link.href === "/my-schools" && !signedIn) {
                  return (
                    <button
                      key={link.href}
                      onClick={() => {
                        setMobileMenuOpen(false);
                        promptSignIn();
                      }}
                      className={className}
                    >
                      {link.label}
                    </button>
                  );
                }
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={className}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {link.label}
                  </Link>
                );
              })}
              <div
                className={`border-t pt-4 px-2 ${
                  isHome ? "header-dark-border" : "border-gray-100"
                }`}
              >
                {session ? (
                  <div className="flex items-center justify-between">
                    <div>
                      <p
                        className={`text-sm font-medium ${
                          isHome ? "header-dark-logo" : "text-gray-800"
                        }`}
                      >
                        {session.user?.name}
                      </p>
                      <p
                        className="text-xs"
                        style={isHome ? { color: "#8a8f98" } : undefined}
                      >
                        {session.user?.email}
                      </p>
                    </div>
                    <button
                      onClick={() => signOut()}
                      className={`text-sm font-medium ${
                        isHome
                          ? "header-dark-link"
                          : "text-gray-600 hover:text-gray-900"
                      }`}
                    >
                      Sign out
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => signIn("google")}
                    className={`flex items-center space-x-2 font-medium ${
                      isHome
                        ? "header-dark-link"
                        : "text-gray-600 hover:text-gray-900"
                    }`}
                  >
                    <span>Sign in with Google</span>
                  </button>
                )}
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
