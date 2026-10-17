-- One-time move from the NextAuth/Prisma schema to the Better Auth/Drizzle schema.
-- Apply with `bun scripts/db-cutover.ts up`; undo with `bun scripts/db-cutover.ts down`.

ALTER TABLE "User" ALTER COLUMN "name" SET NOT NULL;
ALTER TABLE "User" ALTER COLUMN "email" SET NOT NULL;
ALTER TABLE "User" ALTER COLUMN "emailVerified" TYPE boolean USING "emailVerified" IS NOT NULL;
ALTER TABLE "User" ALTER COLUMN "emailVerified" SET DEFAULT false;
ALTER TABLE "User" ALTER COLUMN "emailVerified" SET NOT NULL;
ALTER TABLE "User" ADD COLUMN "createdAt" timestamp(3) NOT NULL DEFAULT now();
ALTER TABLE "User" ADD COLUMN "updatedAt" timestamp(3) NOT NULL DEFAULT now();

ALTER TABLE "Account" RENAME COLUMN "providerAccountId" TO "accountId";
ALTER TABLE "Account" RENAME COLUMN "provider" TO "providerId";
ALTER TABLE "Account" RENAME COLUMN "access_token" TO "accessToken";
ALTER TABLE "Account" RENAME COLUMN "refresh_token" TO "refreshToken";
ALTER TABLE "Account" RENAME COLUMN "id_token" TO "idToken";
ALTER TABLE "Account" ADD COLUMN "accessTokenExpiresAt" timestamp(3);
UPDATE "Account" SET "accessTokenExpiresAt" = to_timestamp("expires_at") AT TIME ZONE 'UTC' WHERE "expires_at" IS NOT NULL;
ALTER TABLE "Account" DROP COLUMN "expires_at";
ALTER TABLE "Account" DROP COLUMN "token_type";
ALTER TABLE "Account" DROP COLUMN "session_state";
ALTER TABLE "Account" DROP COLUMN "type";
ALTER TABLE "Account" ADD COLUMN "refreshTokenExpiresAt" timestamp(3);
ALTER TABLE "Account" ADD COLUMN "password" text;
ALTER TABLE "Account" ADD COLUMN "createdAt" timestamp(3) NOT NULL DEFAULT now();
ALTER TABLE "Account" ADD COLUMN "updatedAt" timestamp(3) NOT NULL DEFAULT now();
ALTER INDEX "Account_provider_providerAccountId_key" RENAME TO "Account_providerId_accountId_key";
ALTER TABLE "Account" RENAME CONSTRAINT "Account_userId_fkey" TO "Account_userId_User_id_fk";

ALTER TABLE "SavedSchool" RENAME CONSTRAINT "SavedSchool_userId_fkey" TO "SavedSchool_userId_User_id_fk";
ALTER TABLE "SchoolNote" RENAME CONSTRAINT "SchoolNote_userId_fkey" TO "SchoolNote_userId_User_id_fk";
ALTER TABLE "SchoolNote" ALTER COLUMN "updatedAt" SET DEFAULT now();

CREATE TABLE "Session" (
  "id" text PRIMARY KEY,
  "userId" text NOT NULL CONSTRAINT "Session_userId_User_id_fk" REFERENCES "User"("id") ON DELETE CASCADE,
  "token" text NOT NULL,
  "expiresAt" timestamp(3) NOT NULL,
  "ipAddress" text,
  "userAgent" text,
  "createdAt" timestamp(3) NOT NULL DEFAULT now(),
  "updatedAt" timestamp(3) NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX "Session_token_key" ON "Session" ("token");
CREATE INDEX "Session_userId_idx" ON "Session" ("userId");

CREATE TABLE "Verification" (
  "id" text PRIMARY KEY,
  "identifier" text NOT NULL,
  "value" text NOT NULL,
  "expiresAt" timestamp(3) NOT NULL,
  "createdAt" timestamp(3) NOT NULL DEFAULT now(),
  "updatedAt" timestamp(3) NOT NULL DEFAULT now()
);
CREATE INDEX "Verification_identifier_idx" ON "Verification" ("identifier");
