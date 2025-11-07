# Film Production Architecture: Gaps & Improvements

## Executive Summary

This document outlines critical architectural gaps in the film production system and provides actionable recommendations for scaling to high-volume, multi-platform, multi-project content production.

**Status**: Based on code review completed 2025-11-06

---

## 🚨 Critical Gaps

### 1. Project Isolation & Multi-Tenancy

**Current State**: No workspace/tenant isolation. All content mixed in single namespace.

**Problems**:
- Cannot isolate Brand A content from Brand B
- No project-level quotas or cost allocation
- Cannot archive/delete projects cleanly
- No hierarchical project organization (campaigns → films → shots)

**Impact**: High-risk when managing multiple brands/clients. No clear ownership boundaries.

**Files**:
- `src/data/models.py:65-85` - FilmProject model
- `director-ui/src/api/routers/film.py` - Film API (no workspace filtering)

---

### 2. Disconnected Generation → Publishing Workflow

**Current State**: Film generation and publishing are completely separate systems with no integration.

**Problems**:
- Must manually copy file paths from generation to publishing
- No tracking of which films published to which platforms
- No "generate → review → publish" workflow
- Cannot answer: "Where was this film published?" or "What films went to TikTok?"

**Impact**: Manual work, no audit trail, difficult to manage published content at scale.

**Missing**:
```python
# FilmProject model needs:
published_variants = relationship("FilmVariant")

# PublishingJob needs:
film_project_id = Column(String, ForeignKey("film_projects.id"))
```

**Files**:
- `src/data/models.py:65-85` - FilmProject (no publishing relationship)
- `director-ui/src/api/routers/publishing.py` - Publishing API (no film reference)

---

### 3. Asset Lifecycle Management

**Current State**: Caching works but no versioning, lineage tracking, or cleanup strategy.

**Problems**:
- Cache grows forever (no TTL or LRU eviction)
- Cannot track which version of asset used in which project
- Cannot trace asset lineage (source image → video → final film)
- No storage quotas per project/workspace
- Orphaned assets when projects deleted

**Impact**: Storage costs grow unbounded. Cannot audit asset usage.

**Files**:
- `src/features/film/cache.py:1-150` - Cache implementation
- `src/data/models.py:46-63` - Asset model (missing relationships)

---

### 4. Character Library Limitations

**Current State**: Character model exists but weak integration with film production.

**Problems**:
- No tracking of which shots use which characters
- Cannot query: "Show all scenes with Character A"
- No character evolution tracking (consistency over time)
- Character-project relationship is just JSON array (not relational)
- No character-asset linkage

**Impact**: Cannot leverage character library for content reusability. No consistency enforcement.

**Files**:
- `src/data/models.py:31-44` - Character model
- `director-ui/src/api/routers/characters.py:219-239` - Weak project association

---

### 5. Platform-Specific Content Variants

**Current State**: One film for all platforms. No aspect ratio management or platform optimization.

**Problems**:
- Cannot generate 16:9 (YouTube) + 9:16 (TikTok) versions automatically
- No platform requirements validation
- Must manually crop/resize for each platform
- No tracking of which variant published where

**Real-World Need**:
```
Same content, different platforms:
- YouTube: 16:9, 1920x1080, <15min
- TikTok: 9:16, 1080x1920, <3min
- Instagram Reels: 9:16, 1080x1920, <90sec
- Instagram Feed: 1:1, 1080x1080
```

**Impact**: Cannot efficiently produce for multiple platforms. Manual work scales poorly.

---

### 6. Incomplete Celery Integration

**Current State**: Celery tasks defined but not connected to actual film pipeline.

**Problems**:
- Tasks are mocked (see `film_tasks.py:58-70`)
- No progress persistence (only WebSocket broadcasts)
- No retry logic for failed generations
- Cannot resume failed jobs

**Files**:
- `director-ui/src/workers/tasks/film_tasks.py:33-83` - Mock implementation

---

### 7. No Batch Operations or Templates

**Current State**: Each film configured individually. No templates or shot libraries.

**Problems**:
- Cannot save successful shot sequences as templates
- Cannot batch generate 100 films with similar structure
- Cannot reuse good shots in new films
- Manual configuration doesn't scale

**Impact**: To produce 100 films/month requires 5000+ individual configurations (50 shots × 100 films).

---

### 8. Cost Tracking Gaps

**Current State**: Per-shot cost tracking but no allocation or forecasting.

**Problems**:
- No cost allocation by workspace/project/client
- No cost forecasting or trend analysis
- No budget alerts (only checked at generation time)
- Cannot track ROI per platform

**Files**:
- `src/features/film/cost_tracker.py` - Basic tracking only

---

## 📊 Recommended Database Schema Changes

### New Tables Needed

```sql
-- ============================================================================
-- 1. Workspace/Tenant Isolation
-- ============================================================================

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id INT NOT NULL,
    storage_quota_gb INT DEFAULT 100,
    monthly_budget_usd DECIMAL(10,2) DEFAULT 1000.00,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_slug ON workspaces(slug);


-- ============================================================================
-- 2. Project Hierarchy (Campaigns → Projects → Films)
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'campaign',  -- 'campaign', 'brand', 'series'
    parent_project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, slug)
);

CREATE INDEX idx_projects_workspace ON projects(workspace_id);
CREATE INDEX idx_projects_parent ON projects(parent_project_id);
CREATE INDEX idx_projects_type ON projects(type);


-- ============================================================================
-- 3. Enhanced Film Projects (Add workspace/project scoping)
-- ============================================================================

ALTER TABLE film_projects ADD COLUMN workspace_id UUID REFERENCES workspaces(id);
ALTER TABLE film_projects ADD COLUMN project_id UUID REFERENCES projects(id);
ALTER TABLE film_projects ADD COLUMN base_film_id VARCHAR(255);  -- For variants
ALTER TABLE film_projects ADD COLUMN variant_type VARCHAR(50);    -- NULL = base, or 'platform', 'language'

CREATE INDEX idx_film_projects_workspace ON film_projects(workspace_id);
CREATE INDEX idx_film_projects_project ON film_projects(project_id);


-- ============================================================================
-- 4. Platform Variants
-- ============================================================================

CREATE TABLE film_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_project_id VARCHAR(255) NOT NULL REFERENCES film_projects(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,  -- 'youtube', 'tiktok', 'instagram_reels', 'instagram_feed'
    aspect_ratio VARCHAR(10) NOT NULL,  -- '16:9', '9:16', '1:1'
    width INT NOT NULL,
    height INT NOT NULL,
    max_duration_seconds INT,
    output_path VARCHAR(1024),
    status VARCHAR(50) DEFAULT 'pending',
    generation_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(film_project_id, platform, aspect_ratio)
);

CREATE INDEX idx_film_variants_project ON film_variants(film_project_id);
CREATE INDEX idx_film_variants_platform ON film_variants(platform);


-- ============================================================================
-- 5. Publishing History (Connect generation → publishing)
-- ============================================================================

CREATE TABLE publish_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_variant_id UUID REFERENCES film_variants(id) ON DELETE SET NULL,
    film_project_id VARCHAR(255) REFERENCES film_projects(id),
    account_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),  -- External ID from platform API
    post_url VARCHAR(1024),
    title VARCHAR(500),
    description TEXT,
    published_at TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'published',
    metrics JSONB DEFAULT '{}',  -- views, likes, shares, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_publish_history_variant ON publish_history(film_variant_id);
CREATE INDEX idx_publish_history_project ON publish_history(film_project_id);
CREATE INDEX idx_publish_history_platform ON publish_history(platform);
CREATE INDEX idx_publish_history_published_at ON publish_history(published_at);


-- ============================================================================
-- 6. Asset-Project Relationships
-- ============================================================================

CREATE TABLE project_assets (
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    asset_id VARCHAR(255) NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'source', 'generated', 'intermediate', 'final'
    used_in_shots JSONB DEFAULT '[]',  -- Array of shot IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, asset_id, role)
);

CREATE INDEX idx_project_assets_project ON project_assets(project_id);
CREATE INDEX idx_project_assets_asset ON project_assets(asset_id);


-- ============================================================================
-- 7. Character-Shot Tracking
-- ============================================================================

CREATE TABLE shot_characters (
    film_project_id VARCHAR(255) NOT NULL REFERENCES film_projects(id) ON DELETE CASCADE,
    shot_id VARCHAR(255) NOT NULL,
    shot_index INT NOT NULL,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(id),
    prominence VARCHAR(50) DEFAULT 'primary',  -- 'primary', 'secondary', 'background'
    screen_time_seconds DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (film_project_id, shot_id, character_id)
);

CREATE INDEX idx_shot_characters_film ON shot_characters(film_project_id);
CREATE INDEX idx_shot_characters_character ON shot_characters(character_id);


-- ============================================================================
-- 8. Enhanced Characters (Add workspace scoping)
-- ============================================================================

ALTER TABLE characters ADD COLUMN workspace_id UUID REFERENCES workspaces(id);
ALTER TABLE characters DROP COLUMN projects_used;  -- Replace with relational table

CREATE INDEX idx_characters_workspace ON characters(workspace_id);


-- ============================================================================
-- 9. Film Templates
-- ============================================================================

CREATE TABLE film_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),  -- 'trailer', 'product_demo', 'explainer', etc.
    shot_sequence JSONB NOT NULL,  -- Array of shot configs
    default_style VARCHAR(100),
    default_providers JSONB,
    usage_count INT DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, name)
);

CREATE INDEX idx_film_templates_workspace ON film_templates(workspace_id);
CREATE INDEX idx_film_templates_category ON film_templates(category);


-- ============================================================================
-- 10. Asset Metadata & Lineage
-- ============================================================================

ALTER TABLE assets ADD COLUMN workspace_id UUID REFERENCES workspaces(id);
ALTER TABLE assets ADD COLUMN source_asset_id VARCHAR(255) REFERENCES assets(id);  -- Lineage
ALTER TABLE assets ADD COLUMN generation_params JSONB;
ALTER TABLE assets ADD COLUMN cache_key VARCHAR(255);  -- For content-addressed storage
ALTER TABLE assets ADD COLUMN expires_at TIMESTAMP;  -- For cache TTL
ALTER TABLE assets ADD COLUMN access_count INT DEFAULT 0;
ALTER TABLE assets ADD COLUMN last_accessed_at TIMESTAMP;

CREATE INDEX idx_assets_workspace ON assets(workspace_id);
CREATE INDEX idx_assets_source ON assets(source_asset_id);
CREATE INDEX idx_assets_cache_key ON assets(cache_key);
CREATE INDEX idx_assets_expires_at ON assets(expires_at);


-- ============================================================================
-- 11. Cost Allocation
-- ============================================================================

CREATE TABLE cost_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    project_id UUID REFERENCES projects(id),
    film_project_id VARCHAR(255) REFERENCES film_projects(id),
    cost_type VARCHAR(50) NOT NULL,  -- 'image_generation', 'video_generation', 'audio_generation', 'storage'
    provider VARCHAR(50),
    amount_usd DECIMAL(10,4) NOT NULL,
    quantity INT,  -- Number of images/videos/etc
    metadata JSONB DEFAULT '{}',
    occurred_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cost_allocations_workspace ON cost_allocations(workspace_id);
CREATE INDEX idx_cost_allocations_project ON cost_allocations(project_id);
CREATE INDEX idx_cost_allocations_occurred_at ON cost_allocations(occurred_at);
```

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Project isolation and workspace multi-tenancy

**Tasks**:
1. Create workspace model and migration
2. Add workspace_id to all relevant tables
3. Update all API endpoints to filter by workspace
4. Add workspace selector to UI
5. Implement workspace-level quotas

**Files to modify**:
- `src/data/models.py` - Add Workspace and Project models
- `director-ui/src/api/routers/*` - Add workspace filtering
- Database migration script

**Success Metrics**:
- All content scoped to workspaces
- Can switch between workspaces in UI
- Quotas enforced

---

### Phase 2: Publishing Integration (Weeks 3-4)

**Goal**: Connect film generation to publishing workflow

**Tasks**:
1. Create film_variants and publish_history tables
2. Add "Publish" button to FilmGenerationPage
3. Auto-create publishing job when film completes
4. Track publication history in database
5. Add "Published Films" view

**Files to modify**:
- `src/data/models.py` - Add FilmVariant, PublishHistory
- `director-ui/frontend/src/pages/FilmGenerationPage.tsx` - Add publish button
- `director-ui/src/api/routers/film.py` - Add publish endpoint
- `director-ui/src/api/routers/publishing.py` - Accept film_project_id

**Success Metrics**:
- One-click publish from film generation
- Can see where each film was published
- Publishing history tracked

---

### Phase 3: Platform Variants (Weeks 5-6)

**Goal**: Generate platform-optimized versions automatically

**Tasks**:
1. Implement film_variants table
2. Add aspect ratio configuration to generation pipeline
3. Create "Generate Variants" endpoint
4. Add variant selection to publishing UI
5. Implement platform validation rules

**Files to modify**:
- `src/pipelines/film_generation.py` - Add aspect ratio support
- `src/pipelines/tasks/film_tasks.py` - Generate multiple variants
- `director-ui/frontend/src/components/publishing/` - Variant selector

**Success Metrics**:
- Can generate 16:9 + 9:16 versions from single config
- Platform requirements validated before publish
- Variants tracked separately in database

---

### Phase 4: Asset Management (Weeks 7-8)

**Goal**: Complete asset lifecycle tracking and cleanup

**Tasks**:
1. Implement project_assets relationship table
2. Add asset lineage tracking (source → generated)
3. Implement cache TTL and LRU eviction
4. Add storage quota enforcement
5. Create asset cleanup job

**Files to modify**:
- `src/features/film/cache.py` - Add TTL and eviction
- `src/data/models.py` - Add ProjectAsset relationship
- New cron job for cleanup

**Success Metrics**:
- Assets linked to projects
- Cache automatically cleaned
- Storage quotas enforced
- Can trace asset lineage

---

### Phase 5: Character System Enhancement (Weeks 9-10)

**Goal**: Full character reusability and consistency tracking

**Tasks**:
1. Implement shot_characters tracking table
2. Add character selection to shot-level configuration
3. Track which shots use which characters
4. Add "Character Usage Report" view
5. Implement character consistency validation

**Files to modify**:
- `src/data/models.py` - Add ShotCharacter model
- `director-ui/frontend/src/pages/FilmGenerationPage.tsx` - Per-shot character selection
- `director-ui/src/api/routers/characters.py` - Usage analytics

**Success Metrics**:
- Can query all shots with character X
- Character usage tracked per film
- Consistency reports generated

---

### Phase 6: Templates & Batch Operations (Weeks 11-12)

**Goal**: Scale to high-volume production with templates

**Tasks**:
1. Implement film_templates table
2. Add template creation UI
3. Implement batch generation API
4. Add template marketplace (optional)
5. Create shot library for reuse

**Files to modify**:
- `src/data/models.py` - Add FilmTemplate model
- `director-ui/frontend/src/pages/TemplateLibraryPage.tsx` - New page
- `director-ui/src/api/routers/film.py` - Batch generation endpoint

**Success Metrics**:
- Can save successful films as templates
- Batch generate 50+ films from template
- Template library browsable in UI

---

### Phase 7: Complete Celery Integration (Weeks 13-14)

**Goal**: Robust background processing with retry logic

**Tasks**:
1. Connect Celery tasks to actual film pipeline
2. Implement progress persistence to database
3. Add retry logic with exponential backoff
4. Implement job resumption for failures
5. Add real-time progress UI

**Files to modify**:
- `director-ui/src/workers/tasks/film_tasks.py` - Remove mocks
- `director-ui/frontend/src/components/film/GenerationProgress.tsx` - Progress UI

**Success Metrics**:
- Film generation runs in background
- Failed jobs automatically retry
- Progress visible in UI
- Can resume failed jobs

---

## 🔧 Quick Wins (Can implement immediately)

### 1. Add Workspace ID to FilmProject

```python
# src/data/models.py
class FilmProject(Base):
    __tablename__ = "film_projects"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"))  # ADD THIS
    project_id = Column(String, ForeignKey("projects.id"))      # ADD THIS
    title = Column(String, nullable=False)
    # ... rest of fields
```

### 2. Add Published Tracking to FilmProject

```python
class FilmProject(Base):
    # ... existing fields
    published_at = Column(DateTime, nullable=True)             # ADD THIS
    published_platforms = Column(JSON, default=[])             # ADD THIS
    publish_history = relationship("PublishHistory")           # ADD THIS
```

### 3. Add Publish Button to Film UI

```typescript
// director-ui/frontend/src/pages/FilmGenerationPage.tsx
const handlePublish = async () => {
  const response = await fetch(apiUrl('/api/film/publish'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      film_project_id: currentFilmId,
      platforms: ['tiktok', 'instagram'],
      account_id: selectedAccount
    })
  });
  // Redirect to publishing dashboard
};

// Add button next to "Export"
<button onClick={handlePublish}>
  <Upload className="w-4 h-4" />
  <span>Publish</span>
</button>
```

### 4. Add Workspace Context Provider

```typescript
// director-ui/frontend/src/contexts/WorkspaceContext.tsx
export const WorkspaceProvider: React.FC = ({ children }) => {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);

  // Wrap all API calls with workspace filter
  const apiWithWorkspace = (path: string) => {
    return `${apiUrl(path)}?workspace_id=${currentWorkspace?.id}`;
  };

  return (
    <WorkspaceContext.Provider value={{ currentWorkspace, setCurrentWorkspace, apiWithWorkspace }}>
      {children}
    </WorkspaceContext.Provider>
  );
};
```

---

## 📈 Scalability Recommendations

### For High-Volume Production (1000+ films/month)

1. **Separate Storage Backend**
   - Move from local filesystem to S3/Cloudflare R2
   - Implement CDN for asset delivery
   - Use signed URLs for secure access

2. **Distributed Caching**
   - Move from file-based cache to Redis/Memcached
   - Implement distributed cache invalidation
   - Add cache warming for popular assets

3. **Database Optimization**
   - Partition large tables by workspace_id
   - Implement read replicas for analytics
   - Add database connection pooling

4. **Queue Optimization**
   - Use separate Celery queues per priority
   - Implement rate limiting per provider
   - Add circuit breakers for provider failures

5. **Monitoring & Observability**
   - Add OpenTelemetry tracing
   - Implement cost anomaly detection
   - Add generation time SLO monitoring

---

## 🎬 Content Workflow Best Practices

### Recommended Production Flow

```
1. PLANNING PHASE
   ├── Create Workspace (e.g., "Acme Brand")
   ├── Create Project (e.g., "Q4 2025 Campaign")
   └── Define Characters (reusable across projects)

2. TEMPLATE PHASE
   ├── Browse template library
   ├── Select template or create custom
   └── Configure style, providers, budget

3. GENERATION PHASE (Automated)
   ├── Generate base film (16:9)
   ├── Auto-generate platform variants (9:16, 1:1)
   ├── Track costs against project budget
   └── Store in project workspace

4. REVIEW PHASE
   ├── Preview all variants
   ├── Check character consistency
   └── Approve for publishing

5. PUBLISHING PHASE (One-click)
   ├── Select platforms + accounts
   ├── Schedule or publish immediately
   ├── Track publication history
   └── Monitor metrics

6. ANALYTICS PHASE
   ├── View per-platform performance
   ├── Calculate ROI per project
   └── Identify best-performing templates
```

---

## 🔒 Security & Access Control

### Recommended Permissions Model

```python
# Workspace-level roles
WORKSPACE_OWNER = 'owner'        # Full access
WORKSPACE_ADMIN = 'admin'        # Manage users, projects
WORKSPACE_CREATOR = 'creator'    # Create/edit content
WORKSPACE_VIEWER = 'viewer'      # Read-only access

# Project-level roles
PROJECT_MANAGER = 'manager'      # Manage project settings
PROJECT_CONTRIBUTOR = 'contributor'  # Create content
PROJECT_VIEWER = 'viewer'        # Read-only

# Implement in API layer:
@router.get("/film/{film_id}")
async def get_film(
    film_id: str,
    current_user: User = Depends(get_current_user)
):
    film = db.query(FilmProject).filter_by(id=film_id).first()
    if not current_user.has_workspace_access(film.workspace_id, 'viewer'):
        raise HTTPException(403, "Access denied")
    return film
```

---

## 📊 Metrics to Track

### Production Metrics
- Films generated per day/week/month
- Average generation time per film
- Cache hit rate (target: >60%)
- Generation success rate (target: >95%)
- Average cost per film

### Business Metrics
- Cost per platform variant
- Storage cost per workspace
- ROI per platform (engagement / cost)
- Template usage distribution
- Character reuse rate

### System Health
- Queue depth (target: <100)
- Average queue wait time (target: <5min)
- Provider API latency (target: <10s)
- Database query performance (target: <100ms)
- Storage utilization (target: <80%)

---

## 🎯 Success Criteria

### After Phase 1-2 (Foundation)
- ✅ All content isolated by workspace
- ✅ Films linked to publishing history
- ✅ One-click publish workflow
- ✅ Can answer: "Where was this published?"

### After Phase 3-4 (Variants & Assets)
- ✅ Auto-generate platform variants
- ✅ Assets properly tracked and cleaned
- ✅ Storage quotas enforced
- ✅ Cache performs efficiently

### After Phase 5-6 (Characters & Templates)
- ✅ Character reusability working
- ✅ Templates enable batch production
- ✅ Can produce 100+ films/month
- ✅ Consistent character appearances

### After Phase 7 (Celery)
- ✅ Background generation working
- ✅ Failed jobs auto-retry
- ✅ Progress visible in real-time
- ✅ System handles high concurrency

---

## 📚 References

**Code Locations**:
- Film Generation Pipeline: `src/pipelines/film_generation.py`
- Data Models: `src/data/models.py`
- Film API: `director-ui/src/api/routers/film.py`
- Publishing API: `director-ui/src/api/routers/publishing.py`
- Celery Tasks: `director-ui/src/workers/tasks/film_tasks.py`
- Film UI: `director-ui/frontend/src/pages/FilmGenerationPage.tsx`
- Caching System: `src/features/film/cache.py`
- Character API: `director-ui/src/api/routers/characters.py`

**Documentation**:
- ZenML Pipelines: `CLAUDE.md:62-123`
- Film Generation: `FILM_GENERATION.md` (if exists)
- Publishing System: Publishing feature in shared library

---

**Document Status**: ✅ Complete - Ready for implementation planning
**Last Updated**: 2025-11-06
**Reviewed By**: Claude Code Analysis
