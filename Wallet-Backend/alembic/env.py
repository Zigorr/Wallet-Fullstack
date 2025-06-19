import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv

from alembic import context

# Add project root to sys.path
# This assumes env.py is in alembic/ directory, so we go up one level
sys.path.append(str(Path(__file__).resolve().parent.parent))

# This will load the .env file located in the parent directory (Wallet-Backend)
# The .env file is still needed for the database.py module to load the settings
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
from database import Base, engine # Import engine directly
from models import User, Account, Category, Transaction  # Import all models
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # In this new setup, we still need the URL for offline mode.
    # We can get it from the engine that's already been created.
    url = engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # We will now use the engine imported directly from our application
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
