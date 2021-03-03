CREATE TABLE "tags" (
	"tag_id" INT GENERATED ALWAYS AS IDENTITY,
	"name" TEXT NOT NULL,
	"content" TEXT NOT NULL,
	"guild_id" BIGINT NOT NULL,
	"author_id" BIGINT NOT NULL,
	"uses" INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("tag_id"),
	UNIQUE INDEX "tags_tag_name_unqiue_per_guild" ("name", "guild_id")
)
;
COMMENT ON COLUMN "tags"."tag_id" IS 'Unqiue ID of Tag';
COMMENT ON COLUMN "tags"."name" IS 'Name of the Tag';
COMMENT ON COLUMN "tags"."content" IS 'Content of the Tag';
COMMENT ON COLUMN "tags"."guild_id" IS 'Discord Guild ID where the tag is located';
COMMENT ON COLUMN "tags"."author_id" IS 'Discord User ID of tag creator';
COMMENT ON COLUMN "tags"."uses" IS 'Amount of times the tag has been used.';
