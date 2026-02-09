from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from core.database import Base
from core.config import settings
from models.task_profile import Task # <- Import your model here
# ----------------- SYNC ENGINE -----------------
# Convert async URL to sync URL for Alembic
sync_engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://"),
    echo=True,
    poolclass=pool.NullPool
)

# ----------------- ALEMBIC CONFIG -----------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # your models

# ----------------- OFFLINE MODE -----------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ----------------- ONLINE MODE -----------------
def run_migrations_online():
    """Run migrations using the synchronous engine"""
    connectable = sync_engine  # use the sync engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# ----------------- RUN -----------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
