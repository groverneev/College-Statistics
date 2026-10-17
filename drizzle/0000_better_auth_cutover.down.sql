-- Restores the NextAuth/Prisma schema. Sessions and verification rows are discarded;
-- users and accounts keep their ids, so saved schools and notes stay attached.

DROP TABLE "Verification";
DROP TABLE "Session";

ALTER TABLE "SchoolNote" ALTER COLUMN "updatedAt" DROP DEFAULT;
ALTER TABLE "SchoolNote" RENAME CONSTRAINT "SchoolNote_userId_User_id_fk" TO "SchoolNote_userId_fkey";
ALTER TABLE "SavedSchool" RENAME CONSTRAINT "SavedSchool_userId_User_id_fk" TO "SavedSchool_userId_fkey";

ALTER TABLE "Account" RENAME CONSTRAINT "Account_userId_User_id_fk" TO "Account_userId_fkey";
ALTER INDEX "Account_providerId_accountId_key" RENAME TO "Account_provider_providerAccountId_key";
ALTER TABLE "Account" DROP COLUMN "updatedAt";
ALTER TABLE "Account" DROP COLUMN "createdAt";
ALTER TABLE "Account" DROP COLUMN "password";
ALTER TABLE "Account" DROP COLUMN "refreshTokenExpiresAt";
ALTER TABLE "Account" ADD COLUMN "type" text NOT NULL DEFAULT 'oauth';
ALTER TABLE "Account" ALTER COLUMN "type" DROP DEFAULT;
ALTER TABLE "Account" ADD COLUMN "session_state" text;
ALTER TABLE "Account" ADD COLUMN "token_type" text;
ALTER TABLE "Account" ADD COLUMN "expires_at" integer;
UPDATE "Account" SET "expires_at" = extract(epoch FROM "accessTokenExpiresAt" AT TIME ZONE 'UTC')::integer WHERE "accessTokenExpiresAt" IS NOT NULL;
ALTER TABLE "Account" DROP COLUMN "accessTokenExpiresAt";
ALTER TABLE "Account" RENAME COLUMN "idToken" TO "id_token";
ALTER TABLE "Account" RENAME COLUMN "refreshToken" TO "refresh_token";
ALTER TABLE "Account" RENAME COLUMN "accessToken" TO "access_token";
ALTER TABLE "Account" RENAME COLUMN "providerId" TO "provider";
ALTER TABLE "Account" RENAME COLUMN "accountId" TO "providerAccountId";

ALTER TABLE "User" DROP COLUMN "updatedAt";
ALTER TABLE "User" DROP COLUMN "createdAt";
ALTER TABLE "User" ALTER COLUMN "emailVerified" DROP NOT NULL;
ALTER TABLE "User" ALTER COLUMN "emailVerified" DROP DEFAULT;
ALTER TABLE "User" ALTER COLUMN "emailVerified" TYPE timestamp(3) USING CASE WHEN "emailVerified" THEN now() END;
ALTER TABLE "User" ALTER COLUMN "email" DROP NOT NULL;
ALTER TABLE "User" ALTER COLUMN "name" DROP NOT NULL;
