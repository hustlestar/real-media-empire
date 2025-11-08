-- Generation History Tables for Iterative AI Creation
-- Stores all script/scene/shot generation attempts with version control

-- Script Generation History
CREATE TABLE IF NOT EXISTS script_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id VARCHAR,
    project_id UUID,
    user_id INTEGER,

    -- Generation metadata
    generation_type VARCHAR(50) NOT NULL CHECK (generation_type IN ('script', 'scene', 'shot')),
    version INTEGER NOT NULL DEFAULT 1,
    parent_id UUID REFERENCES script_generations(id) ON DELETE CASCADE,

    -- Input data (what user provided)
    input_subject TEXT,
    input_action TEXT,
    input_location TEXT,
    input_style VARCHAR(100),
    input_genre VARCHAR(100),
    input_idea TEXT,
    input_partial_data JSONB,

    -- AI refinement feedback
    ai_feedback TEXT,
    ai_enhancement_enabled BOOLEAN DEFAULT false,

    -- Generated output
    output_prompt TEXT,
    output_negative_prompt TEXT,
    output_metadata JSONB,
    output_full_data JSONB,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_favorite BOOLEAN DEFAULT false,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure uniqueness per project/version
    UNIQUE(project_id, generation_type, version)
);

-- Create index for fast lookups
CREATE INDEX idx_script_generations_project ON script_generations(project_id);
CREATE INDEX idx_script_generations_active ON script_generations(is_active) WHERE is_active = true;
CREATE INDEX idx_script_generations_created ON script_generations(created_at DESC);

-- Scenes within a script
CREATE TABLE IF NOT EXISTS scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_generation_id UUID REFERENCES script_generations(id) ON DELETE CASCADE,

    -- Scene details
    scene_number INTEGER NOT NULL,
    title VARCHAR(200),
    description TEXT,
    location VARCHAR(200),
    time_of_day VARCHAR(50),
    mood VARCHAR(100),
    characters JSONB,

    -- Scene metadata
    duration_estimate INTEGER, -- in seconds
    pacing VARCHAR(50) CHECK (pacing IN ('slow', 'medium', 'fast', 'action')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(script_generation_id, scene_number)
);

CREATE INDEX idx_scenes_script ON scenes(script_generation_id);

-- Shots within a scene (with version history)
CREATE TABLE IF NOT EXISTS shot_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,

    -- Shot identification
    shot_number INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    parent_id UUID REFERENCES shot_generations(id) ON DELETE CASCADE,

    -- Shot configuration
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    shot_type VARCHAR(100),
    camera_motion VARCHAR(100),
    lighting VARCHAR(100),
    emotion VARCHAR(100),

    -- Shot metadata
    metadata JSONB,
    duration_seconds FLOAT DEFAULT 3.0,

    -- AI feedback for regeneration
    ai_feedback TEXT,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_favorite BOOLEAN DEFAULT false,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(scene_id, shot_number, version)
);

CREATE INDEX idx_shot_generations_scene ON shot_generations(scene_id);
CREATE INDEX idx_shot_generations_active ON shot_generations(is_active, scene_id);

-- Generation sessions (for grouping related work)
CREATE TABLE IF NOT EXISTS generation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id VARCHAR,
    name VARCHAR(200),
    description TEXT,

    -- Session metadata
    total_generations INTEGER DEFAULT 0,
    active_generation_id UUID REFERENCES script_generations(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments/notes on generations (for collaboration)
CREATE TABLE IF NOT EXISTS generation_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID NOT NULL,
    generation_table VARCHAR(50) NOT NULL, -- 'script_generations' or 'shot_generations'

    user_id INTEGER,
    note TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_generation_notes ON generation_notes(generation_id, generation_table);
