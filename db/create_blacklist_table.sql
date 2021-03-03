CREATE TABLE "blacklist" (
	"id" BIGINT NOT NULL,
	"when" TIMESTAMP NOT NULL,
	"why" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
)
;
COMMENT ON COLUMN "blacklist"."id" IS 'discord user id';
COMMENT ON COLUMN "blacklist"."when" IS 'UTC timestamp of blacklist';
COMMENT ON COLUMN "blacklist"."why" IS 'reason for blacklist';
