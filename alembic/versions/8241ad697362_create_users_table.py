"""create users table

Revision ID: 8241ad697362
Revises: ce3d6786132d
Create Date: 2026-11-01 12:11:00.399822

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8241ad697362'
down_revision: Union[str, Sequence[str], None] = 'e5b5232151b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email")
    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
