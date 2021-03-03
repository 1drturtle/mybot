CREATE TABLE "command_usage" (
	"id" BIGINT NOT NULL,
	"commands_used" INTEGER NOT NULL,
	PRIMARY KEY ("id")
)
;
COMMENT ON COLUMN "command_usage"."id" IS 'Discord User ID';
COMMENT ON COLUMN "command_usage"."commands_used" IS 'Number of Commands used.';
