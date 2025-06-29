BOT_NAME = "flstatutes_pkg"

SPIDER_MODULES = ["flstatutes_pkg.spiders"]
NEWSPIDER_MODULE = "flstatutes_pkg.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.0

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

ITEM_PIPELINES = {
    "flstatutes_pkg.pipelines.FlStatutesPipeline": 300,
}
