from config_reader import MongoConfig


def build_mongodb_url(mongo_config: MongoConfig) -> str:
    return f"mongodb+srv://"\
            f"{mongo_config.username}:{mongo_config.password}"\
            f"@{mongo_config.cluster_url}/?appName={mongo_config.app_name}"