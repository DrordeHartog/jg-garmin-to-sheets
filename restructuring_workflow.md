# ETL Architecture Restructuring Workflow

## **Phase 1: Complete Ports & Interfaces** ✅

### **Task 1.1: Expand `shared/ports.py`** ✅ COMPLETED
- [x] Add `Cache` protocol for cache operations
- [x] Add `NotificationService` protocol for Discord notifications
- [x] Add proper type hints and docstrings

### **Task 1.2: Create `shared/models.py`** ✅ COMPLETED
- [x] Move all data models here (SwimmingLap, SwimmingSession, etc.)
- [x] Ensure models are pure data classes with no dependencies
- [x] Add validation methods if needed

## **Phase 2: Implement Repositories**

### **Task 2.1: Create `ingestion/sources/garmin_repository.py`** 🔄 CURRENT
- [ ] Implement `GarminRepository` protocol
- [ ] Move API navigation logic from `garmin_api_data_job`
- [ ] Handle JSON parsing and data extraction
- [ ] Keep `GarminClient` as pure authentication/connection

### **Task 2.2: Create `etl/repositories/` directory**
- [ ] Create `cache_repository.py` implementing `Cache` protocol
- [ ] Create `database_repository.py` implementing `DB` protocol
- [ ] Move SQL logic from jobs to repositories

## **Phase 3: Refactor Adapters**

### **Task 3.1: Update `etl/adapters/database_client.py`**
- [ ] Implement `DB` protocol
- [ ] Add `upsert_raw_sessions()`, `upsert_raw_laps()`, `upsert_raw_intervals()`
- [ ] Move all SQL logic here from jobs
- [ ] Keep only database-specific code

### **Task 3.2: Update `etl/adapters/notification_service.py`**
- [ ] Implement `NotificationService` protocol
- [ ] Move Discord logic here
- [ ] Make it testable with fake implementations

## **Phase 4: Refactor Jobs (Proof of Concept)**

### **Task 4.1: Refactor `garmin_api_data_job.py`**
- [ ] Remove direct `GarminClient` dependency
- [ ] Inject `GarminRepository` via constructor
- [ ] Remove JSON parsing logic (move to repository)
- [ ] Keep only orchestration logic (Extract → Transform → Load)

### **Task 4.2: Refactor `swimming_laps_job.py`**
- [ ] Remove direct `DatabaseClient` dependency
- [ ] Inject `DB` protocol via constructor
- [ ] Remove SQL logic (move to adapter)
- [ ] Keep only transformation orchestration

## **Phase 5: Update Orchestration**

### **Task 5.1: Update `etl/orchestration/orchestrator.py`**
- [ ] Wire all dependencies (repositories, adapters, jobs)
- [ ] Use dependency injection pattern
- [ ] Remove direct concrete imports
- [ ] Pass protocols to jobs

### **Task 5.2: Update `etl/orchestration/config.py`**
- [ ] Add configuration for all services
- [ ] Make it easy to swap implementations
- [ ] Add environment-based configuration

## **Phase 6: Update Utils**

### **Task 6.1: Move transformation logic to `etl/utils/transformers.py`**
- [ ] Move JSON parsing from jobs
- [ ] Move data validation logic
- [ ] Keep pure functions with no dependencies
- [ ] Add comprehensive docstrings

### **Task 6.2: Update `etl/utils/validators.py`**
- [ ] Add schema validation functions
- [ ] Add data quality checks
- [ ] Keep pure functions

## **Phase 7: Testing & Validation**

### **Task 7.1: Create fake implementations**
- [ ] Create `tests/fakes/fake_garmin_repository.py`
- [ ] Create `tests/fakes/fake_database_client.py`
- [ ] Create `tests/fakes/fake_cache_manager.py`

### **Task 7.2: Write unit tests**
- [ ] Test jobs with fake implementations
- [ ] Test repositories independently
- [ ] Test adapters independently
- [ ] Ensure 100% test coverage for business logic

### **Task 7.3: Integration tests**
- [ ] Test full ETL pipeline
- [ ] Test with real database
- [ ] Test with real Garmin API (if available)

## **Phase 8: Clean Up & Documentation**

### **Task 8.1: Fix imports**
- [ ] Ensure all imports follow the layer rules
- [ ] Remove circular dependencies
- [ ] Use absolute imports consistently

### **Task 8.2: Update CLI**
- [ ] Update `cli/shell.py` to use new architecture
- [ ] Update `cli/etl_commands.py`
- [ ] Test interactive shell

### **Task 8.3: Documentation**
- [ ] Update README with new architecture
- [ ] Add architecture diagrams
- [ ] Document the import rules
- [ ] Add examples of how to add new jobs

---

## **Current Status:**
- ✅ **Phase 1 Complete** - Ports and models are ready
- 🔄 **Phase 2 In Progress** - Working on Task 2.1 (Garmin Repository)
- ⏳ **Phases 3-8 Pending** - Awaiting completion of Phase 2

## **Next Action:**
Start with **Task 2.1: Create `ingestion/sources/garmin_repository.py`**
