import { boolean, index, pgEnum, pgTable, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";

const timestamps = {
  createdAt: timestamp("createdAt", { precision: 3 }).notNull().defaultNow(),
  updatedAt: timestamp("updatedAt", { precision: 3 })
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
};

export const users = pgTable(
  "User",
  {
    id: text("id").primaryKey(),
    name: text("name").notNull(),
    email: text("email").notNull(),
    emailVerified: boolean("emailVerified").notNull().default(false),
    image: text("image"),
    ...timestamps,
  },
  (t) => [uniqueIndex("User_email_key").on(t.email)],
);

export const accounts = pgTable(
  "Account",
  {
    id: text("id").primaryKey(),
    userId: text("userId")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    accountId: text("accountId").notNull(),
    providerId: text("providerId").notNull(),
    accessToken: text("accessToken"),
    refreshToken: text("refreshToken"),
    idToken: text("idToken"),
    accessTokenExpiresAt: timestamp("accessTokenExpiresAt", { precision: 3 }),
    refreshTokenExpiresAt: timestamp("refreshTokenExpiresAt", { precision: 3 }),
    scope: text("scope"),
    password: text("password"),
    ...timestamps,
  },
  (t) => [uniqueIndex("Account_providerId_accountId_key").on(t.providerId, t.accountId)],
);

export const sessions = pgTable(
  "Session",
  {
    id: text("id").primaryKey(),
    userId: text("userId")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    token: text("token").notNull(),
    expiresAt: timestamp("expiresAt", { precision: 3 }).notNull(),
    ipAddress: text("ipAddress"),
    userAgent: text("userAgent"),
    ...timestamps,
  },
  (t) => [uniqueIndex("Session_token_key").on(t.token), index("Session_userId_idx").on(t.userId)],
);

export const verifications = pgTable(
  "Verification",
  {
    id: text("id").primaryKey(),
    identifier: text("identifier").notNull(),
    value: text("value").notNull(),
    expiresAt: timestamp("expiresAt", { precision: 3 }).notNull(),
    ...timestamps,
  },
  (t) => [index("Verification_identifier_idx").on(t.identifier)],
);

export const categoryEnum = pgEnum("Category", ["REACH", "TARGET", "SAFETY", "UNDECIDED"]);
export type Category = (typeof categoryEnum.enumValues)[number];

export const savedSchools = pgTable(
  "SavedSchool",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    userId: text("userId")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    schoolSlug: text("schoolSlug").notNull(),
    category: categoryEnum("category").notNull().default("UNDECIDED"),
    savedAt: timestamp("savedAt", { precision: 3 }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex("SavedSchool_userId_schoolSlug_key").on(t.userId, t.schoolSlug)],
);

export const schoolNotes = pgTable(
  "SchoolNote",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    userId: text("userId")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    schoolSlug: text("schoolSlug").notNull(),
    body: text("body").notNull(),
    ...timestamps,
  },
  (t) => [uniqueIndex("SchoolNote_userId_schoolSlug_key").on(t.userId, t.schoolSlug)],
);
