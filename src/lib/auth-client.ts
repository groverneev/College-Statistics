import { createAuthClient } from "better-auth/react";

export const { useSession, signIn, signOut } = createAuthClient();

export function signInWithGoogle() {
  return signIn.social({ provider: "google", callbackURL: window.location.pathname });
}
