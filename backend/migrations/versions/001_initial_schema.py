"""Initial PostGIS Schema Migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension if PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # Create water_bodies table
    op.create_table(
        'water_bodies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('water_body_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('geometry', sa.Text(), nullable=False),
        sa.Column('area_m2', sa.Float(), nullable=True),
        sa.Column('area_hectares', sa.Float(), nullable=True),
        sa.Column('centroid', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('water_body_id')
    )
    op.create_index(op.f('ix_water_bodies_district'), 'water_bodies', ['district'], unique=False)
    op.create_index(op.f('ix_water_bodies_id'), 'water_bodies', ['id'], unique=False)
    op.create_index(op.f('ix_water_bodies_name'), 'water_bodies', ['name'], unique=False)
    op.create_index(op.f('ix_water_bodies_state'), 'water_bodies', ['state'], unique=False)
    op.create_index(op.f('ix_water_bodies_water_body_id'), 'water_bodies', ['water_body_id'], unique=True)

    # Create observations table
    op.create_table(
        'observations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('water_body_id', sa.String(length=64), nullable=False),
        sa.Column('acquisition_date', sa.String(length=50), nullable=False),
        sa.Column('satellite', sa.String(length=100), nullable=True),
        sa.Column('sensor', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('collection_id', sa.String(length=100), nullable=True),
        sa.Column('cloud_percentage', sa.Float(), nullable=True),
        sa.Column('water_area_m2', sa.Float(), nullable=True),
        sa.Column('water_area_ha', sa.Float(), nullable=True),
        sa.Column('mndwi', sa.Float(), nullable=True),
        sa.Column('ndwi', sa.Float(), nullable=True),
        sa.Column('ndvi', sa.Float(), nullable=True),
        sa.Column('rainfall', sa.Float(), nullable=True),
        sa.Column('data_quality', sa.String(length=50), nullable=True),
        sa.Column('processing_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['water_body_id'], ['water_bodies.water_body_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('water_body_id', 'acquisition_date', 'source', 'collection_id', name='uq_observation_identity')
    )
    op.create_index(op.f('ix_observations_acquisition_date'), 'observations', ['acquisition_date'], unique=False)
    op.create_index(op.f('ix_observations_id'), 'observations', ['id'], unique=False)
    op.create_index(op.f('ix_observations_water_body_id'), 'observations', ['water_body_id'], unique=False)

    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('water_body_id', sa.String(length=64), nullable=False),
        sa.Column('prediction_date', sa.String(length=50), nullable=False),
        sa.Column('health_class', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('probability_if_supported', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['water_body_id'], ['water_bodies.water_body_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)
    op.create_index(op.f('ix_predictions_prediction_date'), 'predictions', ['prediction_date'], unique=False)
    op.create_index(op.f('ix_predictions_priority'), 'predictions', ['priority'], unique=False)
    op.create_index(op.f('ix_predictions_water_body_id'), 'predictions', ['water_body_id'], unique=False)


def downgrade() -> None:
    op.drop_table('predictions')
    op.drop_table('observations')
    op.drop_table('water_bodies')
