"""Initial schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-03-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create PostGIS extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(150), unique=True, nullable=True),
        sa.Column('phone', sa.String(15), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone'),
    )
    
    # Create technicians table
    op.create_table(
        'technicians',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(15), unique=True, nullable=False),
        sa.Column('email', sa.String(150), unique=True, nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('service_category', sa.String(), nullable=False, index=True),
        sa.Column('experience_years', sa.Float(), default=0),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), default='Chennai'),
        sa.Column('location', postgresql.dialects.geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=True, server_default=None, unique=False),
        sa.Column('rating', sa.Float(), default=0.0),
        sa.Column('total_reviews', sa.Float(), default=0),
        sa.Column('is_available', sa.Boolean(), default=True, nullable=False, index=True),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False, index=True),
        sa.Column('profile_image', sa.String(), nullable=True),
        sa.Column('cancellation_rate', sa.Float(), default=0.05),
        sa.Column('response_delay_avg', sa.Float(), default=15.0),
        sa.Column('rating_stability', sa.Float(), default=0.80),
        sa.Column('availability_score', sa.Float(), default=0.85),
        sa.Column('verification_age_days', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone'),
    )
    
    # Create indexes for location queries
    op.create_index(
        'ix_technicians_location',
        'technicians',
        ['location'],
        postgresql_using='gist'
    )
    
    # Create index on service_category
    op.create_index('ix_technicians_service_category', 'technicians', ['service_category'])


def downgrade() -> None:
    """Drop initial database schema."""
    op.drop_index('ix_technicians_service_category')
    op.drop_index('ix_technicians_location')
    op.drop_table('technicians')
    op.drop_table('users')
