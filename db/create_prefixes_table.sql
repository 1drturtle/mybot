CREATE TABLE "prefixes" (
	"id" BIGINT NOT NULL,
	"prefix" TEXT NOT NULL,
	PRIMARY KEY (id)
)
;
COMMENT ON COLUMN "prefixes"."id" IS 'Discord Guild ID';
COMMENT ON COLUMN "prefixes"."prefix" IS 'Command Prefix to use';
