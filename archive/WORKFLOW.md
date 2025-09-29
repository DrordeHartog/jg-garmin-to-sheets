# ��‍♂️ Garmin Swimming Analyzer - 7-Week Summer Sprint

## 📋 Project Overview
Transform the existing Garmin data sync tool into a focused swimming performance analyzer MVP within 7 weeks, balancing quality with time constraints for portfolio development.

## 🌿 Branch Management
- **`develop`**: Main development branch with merged features
- **`feature/swimming-intervals`**: ✅ **MERGED** - Database schema and swimming data models
- **`feature/data-processing`**: 🔄 **CURRENT** - Data processing and ETL pipeline
- **`feature/refactor`**: Core refactoring work (completed)

## �� Project Goals
- **Core functionality** that works end-to-end
- **Clean architecture** (maintainable, not perfect)
- **Portfolio-ready** with real swimming insights
- **Time for job hunting** and other commitments

---

## ⏰ Timeline & Time Management

### **Total Duration: 7 weeks**
- **Weekly commitment**: 20-25 hours
- **Total project time**: 140-175 hours
- **Daily average**: 3-4 hours (weekdays), 0-2 hours (weekends)

### **Weekly Schedule Template**

### **Job Hunting Integration**
- **Weekday evenings**: Coding (2-3 hours after classes/job prep)
- **Weekends**: Job applications, interviews, light coding
- **Flexible schedule**: Adapt to interview calls

---

## 📅 Week-by-Week Breakdown

### **Week 1: Foundation & Refactoring**
**Goal**: Get clean, working codebase
**Time**: 20-25 hours

#### **Day 1: Setup & Structure** *(COMPLETED)*
- [x] Create new directory structure
- [x] Move existing files to appropriate locations
- [x] Update `__init__.py` files
- [x] Test basic imports

#### **Day 2: Extract Authentication & Data Fetching** *(COMPLETED)*
- [x] Move Garmin authentication logic to `core/garmin_client.py`
- [x] Create clean authentication interface
- [x] Update imports in main.py
- [x] Test authentication still works
- [x] Move metrics fetching logic to `core/garmin_client.py`
- [x] Create clean data fetching interface
- [x] Test data fetching functionality

#### **Day 3: Data Processing Refactoring** *(COMPLETED)*
- [x] Extract data processing methods from `get_metrics`
- [x] Create individual processing methods (`_process_hrv_data`, `_process_activities_data`, etc.)
- [x] Remove duplicate data fetching logic
- [x] Test refactored data processing

#### **Day 4: Update Data Models** *(COMPLETED)*
- [x] Update `GarminMetrics` dataclass for swimming data
- [x] Add missing swimming fields discovered in API analysis
- [x] Fix pool length calculation (3333.33m → 33.33m)
- [x] Test updated data models
- [x] **BONUS**: Implement new data model structure with specialized models:
  - [x] `SleepMetrics` for sleep-related data
  - [x] `HealthMetrics` for health and fitness data
  - [x] `RecoveryMetrics` for recovery and HRV data
  - [x] `SwimmingMetrics` for comprehensive swimming data
  - [x] `DailyMetrics` container combining all metrics
- [x] Remove cycling and tennis metrics as per requirements
- [x] Ensure data model field names are stable and API-independent
- [x] Add comprehensive tests for new data models
- [x] Commit refactored data model structure

#### **Day 5: Database Infrastructure Setup** *(COMPLETED)*
- [x] Create SQLite database setup
- [x] Create database utilities and connection management
- [x] Add SQLAlchemy dependency to requirements.txt
- [x] Create DatabaseManager class with connection management
- [x] Implement context manager for safe database connections
- [x] Add database info, backup, and metadata functionality
- [x] Set up professional database architecture for portfolio value
- [x] Commit database infrastructure

#### **Day 6: Database Schema Design & Implementation** *(COMPLETED)*
- [x] Design database schema for swimming sessions
- [x] Design database schema for daily metrics (sleep, health, recovery, swimming)
- [x] Implement comprehensive 7-table schema in schema.py:
  - [x] `daily_summary` - Daily activity metrics (steps, calories, weight, VO2 max)
  - [x] `recovery` - Sleep, HRV, stress, and resting HR metrics
  - [x] `activities` - Non-swimming activities (running, cycling, etc.)
  - [x] `swimming_sessions` - Complete swimming session data with summary metrics
  - [x] `swimming_intervals` - Training phases (WARMUP, ACTIVE, REST, COOLDOWN)
  - [x] `swimming_laps` - Laps within intervals with detailed metrics
  - [x] `swimming_lengths` - Individual pool lengths (33.33m) for granular analysis
- [x] Set up database tables and relationships with foreign key constraints
- [x] Create 11 performance indexes for efficient queries
- [x] Test database operations with comprehensive foundation tests
- [x] Test table creation and basic CRUD operations
- [x] Validate schema with sample data insertion and retrieval
- [x] **BONUS**: Implement hierarchical swimming data structure (Session → Interval → Lap → Length)
- [x] **BONUS**: Support for 33.33m pool length and comprehensive swimming metrics
- [x] Fix database import issues and test data fetching methods
- [x] Commit comprehensive database schema implementation

#### **Day 7: Data Processing Implementation** *(IN PROGRESS - feature/data-processing branch)*
- [x] Create `DataProcessor` class in `src/orchestration/data_processor.py`
- [x] **BONUS**: Implement enterprise ETL orchestration framework:
  - [x] Create separate processor files for each database table
  - [x] Implement `BaseTableProcessor` abstract class for consistency
  - [x] Add comprehensive logging and metrics (success/failure, record counts, runtime)
  - [x] Implement fault tolerance with separate transactions per table
  - [x] Add comprehensive test suite for orchestration framework
- [x] **NEW BRANCH**: Working on `feature/data-processing` branch
- [x] **ARCHITECTURE**: Enterprise-level ETL pipeline structure completed
- [x] **DUPLICATE PREVENTION**: Implement data import deduplication mechanism:
  - [x] Add `INSERT OR REPLACE` strategy for idempotent imports
  - [x] Implement date-based duplicate detection in processors
  - [x] Add import status tracking (success/failure per date)
  - [x] Create resume capability for interrupted imports
  - [x] Add import validation and rollback on errors
- [x] **RECOVERY DATA ETL**: Complete recovery table processing:
  - [x] Implement RecoveryProcessor with extract, transform, load methods
  - [x] Successfully import 47 days of Garmin data (15 with complete metrics)
  - [x] Validate data quality and completeness (31.9% success rate due to rate limiting)
  - [x] Create comprehensive data analysis and testing scripts
- [ ] **EDA FOR PARTIAL DATA**: Perform exploratory data analysis on recovery data:
  - [ ] Analyze data availability patterns (why only 31.9% success rate)
  - [ ] Investigate rate limiting impact and optimization strategies
  - [ ] Explore data quality issues and missing data patterns
  - [ ] Create data completeness reports and recommendations
  - [ ] Design retry logic and exponential backoff for rate limiting
- [ ] Implement individual processor logic for remaining tables (extract, transform, load methods)
- [ ] Move processing methods from `GarminClient` to individual processors
- [ ] Update `GarminClient` to only handle data fetching (remove processing)
- [ ] Test complete data flow from fetch to process to database
- [ ] Validate swimming data extraction and storage


#### **Week 1 Deliverables**
- [x] New directory structure
- [x] Extracted Garmin authentication
- [x] Extracted data fetching
- [x] Updated data models
- [x] Database infrastructure setup
- [ ] Database schema design and implementation
- [ ] Refactored data processing
- [ ] Basic working system with database integration

---

### **Week 2: ETL Orchestration & Production Readiness**
**Goal**: Production-ready ETL pipeline with monitoring and orchestration
**Time**: 20-25 hours

#### **Day 1-2: Repository Restructuring & Service Architecture** *(COMPLETED)*
- [x] Restructure repository into service-based architecture
- [x] Move `src/core/*` to `src/ingestion/` and `src/shared/`
- [x] Move `src/orchestration/*` to `src/etl/`
- [x] Move `src/ui/*` to `src/dashboard/`
- [x] Move `src/utils/*` to `src/shared/`
- [x] Create new service directories: `monitoring`, `infrastructure`, `docs`, `scripts`
- [x] Update all import paths across codebase and tests
- [x] Fix 29 core tests to work with new structure
- [x] Demonstrate understanding of service boundaries and enterprise architecture
- [x] **BONUS**: Portfolio value through clean service separation

#### **Day 3-4: ETL Orchestration & Load Management** *(COMPLETED)*
- [x] **LOGGING & MONITORING SYSTEM**: Implement comprehensive monitoring infrastructure:
  - [x] Structured JSON logging with SQLite metrics storage
  - [x] Discord webhook notifications with rich embeds
  - [x] Metrics collection for jobs, API calls, and system health
  - [x] Health monitoring and alerting capabilities
  - [x] Support for Grafana dashboards with proper database schema
  - [x] Job context manager for automatic logging
  - [x] Comprehensive test suite with full system validation
- [x] **ETL ORCHESTRATOR**: Implement main orchestrator with enhanced caching:
  - [x] Create `ETLOrchestrator` class with proper ETL flow
  - [x] Implement enhanced caching system with JSON file storage
  - [x] Add rate limiting and proper API call management
  - [x] Create comprehensive data fetching pipeline
  - [x] Implement cache-first strategy with automatic cleanup
- [x] **ENHANCED SWIMMING DATA CACHING**: Complete swimming data hierarchy:
  - [x] Fetch detailed swimming data for each swimming activity
  - [x] Implement Session → Lap → Length → Stroke data structure
  - [x] Cache individual stroke analysis (SWOLF, stroke count, HR per length)
  - [x] Handle multiple API calls per date with proper rate limiting
  - [x] Achieve 100% success rate for detailed data fetching (11 activities)
  - [ ] Create staging layer for batch processing
  - [ ] Implement job retry logic with configurable strategies

#### **Day 5-6: Swimming Data Processing & Database Population** *(PLANNED)*
- [ ] **SWIMMING PROCESSORS IMPLEMENTATION**: Implement complete swimming data processors:
  - [ ] Create `SwimmingSessionsProcessor` for session-level data processing
  - [ ] Create `SwimmingIntervalsProcessor` for training interval processing  
  - [ ] Create `SwimmingLapsProcessor` for lap-level data processing
  - [ ] Create `SwimmingLengthsProcessor` for individual length processing
  - [ ] Integrate all processors with enhanced cached data structure
- [ ] **DATABASE POPULATION**: Populate swimming tables with enhanced cached data:
  - [ ] Process all 11 swimming activities through complete ETL pipeline
  - [ ] Populate `swimming_sessions`, `swimming_intervals`, `swimming_laps`, `swimming_lengths` tables
  - [ ] Validate data integrity and foreign key relationships
  - [ ] Test complete Session → Interval → Lap → Length hierarchy
- [ ] **ETL PIPELINE TESTING**: Test complete swimming data pipeline:
  - [ ] End-to-end testing from enhanced cache to structured database
  - [ ] Performance testing with multiple swimming sessions
  - [ ] Data quality validation and error handling testing

#### **Day 7: Monitoring & Observability** *(PLANNED)*
- [ ] **GRAFANA DASHBOARDS**: Set up monitoring dashboards:
  - [ ] Create ETL job success rate dashboard
  - [ ] Add API response times and rate limiting status
  - [ ] Implement system health monitoring
  - [ ] Create data quality and completeness reports
- [ ] **DISCORD INTEGRATION**: Enhance notification system:
  - [ ] Add daily summary reports
  - [ ] Implement critical alert escalation
  - [ ] Create job failure notifications with error details
  - [ ] Add system health status updates

#### **Day 7: Swimming Data ETL & Integration Testing** *(PLANNED)*
- [ ] **SWIMMING ETL**: Implement swimming data processors:
  - [ ] Complete swimming sessions, intervals, laps, and lengths processors
  - [ ] Test swimming data extraction and storage
  - [ ] Validate hierarchical data structure (Session → Interval → Lap → Length)
- [ ] **INTEGRATION TESTING**: Test complete ETL pipeline:
  - [ ] End-to-end testing with real Garmin data
  - [ ] Performance testing with rate limiting scenarios
  - [ ] Error handling and recovery testing
  - [ ] Data quality validation and reporting

#### **Week 2 Deliverables**
- [x] Service-based repository architecture
- [x] Comprehensive logging and monitoring system
- [x] Discord webhook notifications working
- [ ] ETL orchestrator with scheduling and load management
- [ ] Grafana dashboards for monitoring
- [ ] Complete swimming data ETL pipeline
- [ ] Production-ready error handling and resilience

---

## **🚀 ETL Orchestration Implementation Plan**

### **Phase 1: Core Orchestration Foundation (2-3 hours)**

#### **Step 1: Basic ETLOrchestrator (30-45 min)**
**Goal**: Get the orchestrator running and executing recovery ETL jobs
**What we implement**:
- Basic `ETLOrchestrator.start()` and `ETLOrchestrator.stop()`
- Simple `execute_recovery_etl()` method
- Direct integration with existing `RecoveryProcessor`
- Basic logging and error handling

**Test**: Run orchestrator, execute single recovery job, verify data in database

#### **Step 2: Job Management (45-60 min)**
**Goal**: Add job tracking and state management
**What we implement**:
- `JobManager.execute_job()` with proper state tracking
- Job result storage and retrieval
- Basic job history
- Job status monitoring

**Test**: Execute multiple jobs, check job status, verify job history

#### **Step 3: Load Management (30-45 min)**
**Goal**: Add rate limiting and basic backoff
**What we implement**:
- `LoadManager.can_make_request()` for Garmin API
- Simple rate limiting (requests per minute)
- Basic exponential backoff
- Integration with GarminClient

**Test**: Test rate limiting, verify backoff behavior, check API call patterns

### **Phase 2: Scheduling & Automation (1-2 hours)**

#### **Step 4: APScheduler Integration (45-60 min)**
**Goal**: Add automated job scheduling
**What we implement**:
- `BackgroundScheduler` setup
- Daily recovery ETL job scheduling
- Cron-based triggers
- Scheduler start/stop integration

**Test**: Schedule daily jobs, verify automatic execution, check scheduler status

#### **Step 5: Webhook API (30-45 min)**
**Goal**: Add external trigger capability
**What we implement**:
- Basic Flask webhook endpoints
- Manual job triggering via HTTP
- Job status checking via API
- Health check endpoint

**Test**: Trigger jobs via webhook, check job status via API, verify health checks

### **Phase 3: Production Features (1 hour)**

#### **Step 6: Enhanced Monitoring (30-45 min)**
**Goal**: Add comprehensive monitoring and alerting
**What we implement**:
- Discord notifications for job start/success/failure
- Enhanced logging with job context
- Metrics collection for job performance
- Error alerting and recovery

**Test**: Verify Discord notifications, check enhanced logs, validate metrics collection

### **🔧 Implementation Order & Dependencies**

```
Step 1: ETLOrchestrator (Foundation)
    ↓
Step 2: JobManager (State Management)
    ↓
Step 3: LoadManager (Rate Limiting)
    ↓
Step 4: APScheduler (Automation)
    ↓
Step 5: WebhookAPI (External Triggers)
    ↓
Step 6: Enhanced Monitoring (Production Ready)
```

### **🧪 Testing Strategy**

#### **After Each Step**:
1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test with existing recovery data
3. **Manual Tests**: Run orchestrator and verify behavior
4. **Database Verification**: Check data is properly stored

#### **Test Data**:
- **Recovery data**: 7-14 days of real Garmin data
- **Rate limiting**: Test with multiple rapid requests
- **Error scenarios**: Test with invalid credentials, network issues

### **📁 Files to Implement (In Order)**

1. **`src/etl/orchestration/orchestrator.py`** - Core orchestrator logic
2. **`src/etl/orchestration/job_manager.py`** - Job state management
3. **`src/etl/orchestration/load_manager.py`** - Rate limiting logic
4. **`src/etl/orchestration/orchestrator.py`** - APScheduler integration
5. **`src/etl/orchestration/webhook_api.py`** - Flask API endpoints
6. **`src/etl/orchestration/orchestrator.py`** - Enhanced monitoring

### **🎯 Success Criteria**

#### **After Step 1**: 
- ✅ Orchestrator can start/stop
- ✅ Can execute single recovery ETL job
- ✅ Data appears in database

#### **After Step 3**:
- ✅ Can execute multiple jobs with rate limiting
- ✅ Job states are properly tracked
- ✅ API calls respect rate limits

#### **After Step 5**:
- ✅ Jobs can be triggered via webhook
- ✅ Job status can be checked via API
- ✅ Scheduler runs jobs automatically

#### **After Step 6**:
- ✅ Complete production-ready ETL system
- ✅ Discord notifications working
- ✅ Comprehensive monitoring and alerting

---

### **Week 3: Enhanced Data & Validation**
**Goal**: Better data quality and session-level analysis
**Time**: 20-25 hours

#### **Day 1-2: Session-Level Data**
- [ ] Implement session-level data collection
- [ ] Add interval breakdown capabilities
- [ ] Create session metadata
- [ ] Handle multiple session types

#### **Day 3-4: Data Validation**
- [ ] Implement basic data validation
- [ ] Add anomaly detection
- [ ] Create data quality scoring
- [ ] Handle missing data gracefully

#### **Day 5-7: Interval Analysis**
- [ ] Add interval-level metrics
- [ ] Implement lap-by-lap analysis
- [ ] Create interval comparisons
- [ ] Add performance consistency metrics

#### **Week 3 Deliverables**
- [ ] Session-level data collection
- [ ] Basic data validation
- [ ] Interval analysis
- [ ] Data quality scoring

---

### **Week 4: Advanced Analysis Features**
**Goal**: Meaningful swimming insights
**Time**: 20-25 hours

#### **Day 1-2: Stroke Analysis**
- [ ] Implement stroke efficiency analysis
- [ ] Add stroke consistency metrics
- [ ] Create stroke recommendations
- [ ] Analyze stroke patterns

#### **Day 3-4: Progress Tracking**
- [ ] Implement progress tracking over time
- [ ] Add performance trend analysis
- [ ] Create improvement metrics
- [ ] Add goal setting capabilities

#### **Day 5-7: Recommendations**
- [ ] Implement basic recommendations
- [ ] Add training suggestions
- [ ] Create performance insights
- [ ] Add personalized feedback

#### **Week 4 Deliverables**
- [ ] Stroke efficiency analysis
- [ ] Progress tracking
- [ ] Basic recommendations
- [ ] Performance trends

---

### **Week 5: User Interface & Output**
**Goal**: User-friendly interface
**Time**: 20-25 hours

#### **Day 1-2: Dashboard Setup**
- [ ] Set up Streamlit application
- [ ] Create basic layout and navigation
- [ ] Implement data upload functionality
- [ ] Add basic data display

#### **Day 3-4: Analysis Display**
- [ ] Create analysis results display
- [ ] Implement interactive charts
- [ ] Add metric summaries
- [ ] Create comparison views

#### **Day 5-7: Export & Output**
- [ ] Implement CSV export with analysis
- [ ] Add basic chart generation
- [ ] Create user input forms
- [ ] Add data download functionality

#### **Week 5 Deliverables**
- [ ] Streamlit dashboard
- [ ] CSV export with analysis
- [ ] Basic charts and visualizations
- [ ] User input forms

---

### **Week 6: Testing & Polish**
**Goal**: Robust, bug-free system
**Time**: 20-25 hours

#### **Day 1-2: Comprehensive Testing**
- [ ] Write unit tests for core functions
- [ ] Test data validation logic
- [ ] Test analysis functions
- [ ] Test UI functionality

#### **Day 3-4: Bug Fixes**
- [ ] Fix identified issues
- [ ] Improve error handling
- [ ] Add input validation
- [ ] Handle edge cases

#### **Day 5-7: Performance & Polish**
- [ ] Optimize performance bottlenecks
- [ ] Improve user experience
- [ ] Add helpful error messages
- [ ] Polish UI elements

#### **Week 6 Deliverables**
- [ ] Comprehensive testing
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Error handling improvements

---

### **Week 7: Documentation & Deployment**
**Goal**: Portfolio-ready project
**Time**: 20-25 hours

#### **Day 1-2: Documentation**
- [ ] Write comprehensive README
- [ ] Create setup instructions
- [ ] Document API usage
- [ ] Add code comments

#### **Day 3-4: Demo & Presentation**
- [ ] Create demo video/screenshots
- [ ] Prepare portfolio presentation
- [ ] Write project summary
- [ ] Create feature showcase

#### **Day 5-7: Deployment & Final Polish**
- [ ] Set up deployment environment
- [ ] Test deployment process
- [ ] Final testing and validation
- [ ] Prepare for portfolio submission

#### **Week 7 Deliverables**
- [ ] README and documentation
- [ ] Demo video/screenshots
- [ ] Deployment setup
- [ ] Portfolio presentation

---

## 🏗️ Simplified Architecture (3 Modules)

---

## ✅ MVP Feature Set (7-Week Scope)

### **Core Functionality**
1. **Garmin Data Import** ✅ (Week 1)
   - Authentication and data fetching
   - Clean, refactored codebase

2. **Basic Swimming Metrics** ✅ (Week 2)
   - Pace, distance, duration, SWOLF
   - Session summaries

3. **Session Analysis** ✅ (Week 3)
   - Per-session insights
   - Data quality validation
   - Interval breakdown

4. **Progress Tracking** ✅ (Week 4)
   - Performance over time
   - Basic recommendations
   - Stroke analysis

5. **Simple Dashboard** ✅ (Week 5)
   - Data upload and display
   - Analysis results
   - Basic charts

6. **Robust Testing** ✅ (Week 6)
   - Error handling
   - Data validation
   - Performance optimization

7. **Documentation** ✅ (Week 7)
   - Clear setup instructions
   - Usage examples
   - Portfolio presentation

---

## �� Features to Skip (Save Time)

### **Non-Essential Features**
- ❌ Email reports
- ❌ Advanced visualizations
- ❌ Multiple export formats
- ❌ User authentication
- ❌ Complex scheduling
- ❌ Mobile app
- ❌ Real-time processing
- ❌ Advanced data validation
- ❌ Multiple user support

### **Focus on Core Value**
- ✅ Clean data fetching
- ✅ Meaningful swimming analysis
- ✅ Simple but effective UI
- ✅ CSV export with insights
- ✅ Basic progress tracking

---

## 🚨 Risk Mitigation & Contingency Plans

### **High-Risk Items to Avoid**
1. **Complex authentication flows** - Use simple credential input
2. **Advanced data validation** - Basic checks only
3. **Multiple output formats** - Focus on CSV + dashboard
4. **Real-time processing** - Batch processing is fine
5. **Mobile optimization** - Desktop-first approach

### **Contingency Plans**
- **Week 3 backup**: If data validation takes too long, skip to basic analysis
- **Week 5 backup**: If UI is complex, use simple Streamlit forms
- **Week 6 backup**: Focus on core functionality over polish

### **Success Factors**
- **Consistent weekly progress** (even if small)
- **Regular testing** (don't let bugs accumulate)
- **Documentation** (write as you go)
- **Realistic expectations** (quality over speed)

---

## 📊 Success Metrics for 7 Weeks

### **Minimum Viable Product**
- [ ] User can upload Garmin data
- [ ] System provides meaningful swimming insights
- [ ] Clean, maintainable code architecture
- [ ] Basic but functional user interface
- [ ] Portfolio-ready documentation

### **Nice-to-Have (if time permits)**
- [ ] Basic progress charts
- [ ] Data quality warnings
- [ ] Export functionality
- [ ] Error handling for edge cases

---

## �� Weekly Checkpoints

### **Week 1 Checkpoint**
- [ ] Codebase refactored and working
- [ ] New architecture in place
- [ ] Basic functionality preserved

### **Week 2 Checkpoint**
- [ ] Swimming metrics calculated correctly
- [ ] Analysis functions working
- [ ] Data models properly structured

### **Week 3 Checkpoint**
- [ ] Session-level analysis working
- [ ] Data validation implemented
- [ ] Interval analysis functional

### **Week 4 Checkpoint**
- [ ] Advanced analysis features working
- [ ] Progress tracking functional
- [ ] Recommendations generating

### **Week 5 Checkpoint**
- [ ] Dashboard functional
- [ ] User can interact with system
- [ ] Export functionality working

### **Week 6 Checkpoint**
- [ ] System thoroughly tested
- [ ] Major bugs resolved
- [ ] Performance optimized

### **Week 7 Checkpoint**
- [ ] Documentation complete
- [ ] Portfolio presentation ready
- [ ] Project deployable

---

## �� Tips for Success

### **Time Management**
- **Start each week strong** - Get the foundation right
- **Test early and often** - Don't let bugs accumulate
- **Keep scope focused** - Resist adding "cool features"
- **Document as you go** - Don't leave it all for Week 7

### **Development Approach**
- **MVP mindset** - Build core functionality first
- **Iterative development** - Small working pieces
- **Regular commits** - Track progress and rollback if needed
- **User feedback** - Test with real data early

### **Quality vs Speed**
- **Code quality** - Maintainable, readable code
- **Functionality** - Core features working end-to-end
- **Documentation** - Clear setup and usage instructions
- **Testing** - Basic error handling and validation

---

## 🏆 Portfolio Value

### **What You'll Have**
- **Real API integration** (Garmin Connect)
- **Data analysis pipeline** (ETL + insights)
- **Clean software architecture** (refactored codebase)
- **User interface** (Streamlit dashboard)
- **End-to-end functionality** (data in → insights out)

### **Employer Appeal**
- **Demonstrates real-world skills** beyond classroom assignments
- **Shows API integration experience** - highly valued
- **Proves data analysis + software engineering** combination
- **Evidence of self-directed learning**
- **Portfolio-ready project** with clear documentation

---

## 📚 Resources & References

### **Swimming Analysis**
- FINA swimming standards
- Swimming coaching literature
- Sports science research papers

### **Technical Resources**
- Streamlit documentation
- Pandas/NumPy tutorials
- Python async programming guides
- Data visualization best practices

### **Architecture Resources**
- Clean Architecture principles
- SOLID principles
- Python design patterns

---

## 🎯 Next Steps

1. **Review and approve this workflow**
2. **Set up development environment**
3. **Create Git repository with proper branching**
4. **Begin Week 1: Foundation & Refactoring**
5. **Set up weekly progress reviews**

---

## 📝 Progress Tracking

### **Daily Log Template**

---

## ✅ MVP Feature Set (7-Week Scope)

### **Core Functionality**
1. **Garmin Data Import** ✅ (Week 1)
   - Authentication and data fetching
   - Clean, refactored codebase

2. **Basic Swimming Metrics** ✅ (Week 2)
   - Pace, distance, duration, SWOLF
   - Session summaries

3. **Session Analysis** ✅ (Week 3)
   - Per-session insights
   - Data quality validation
   - Interval breakdown

4. **Progress Tracking** ✅ (Week 4)
   - Performance over time
   - Basic recommendations
   - Stroke analysis

5. **Simple Dashboard** ✅ (Week 5)
   - Data upload and display
   - Analysis results
   - Basic charts

6. **Robust Testing** ✅ (Week 6)
   - Error handling
   - Data validation
   - Performance optimization

7. **Documentation** ✅ (Week 7)
   - Clear setup instructions
   - Usage examples
   - Portfolio presentation

---

## �� Features to Skip (Save Time)

### **Non-Essential Features**
- ❌ Email reports
- ❌ Advanced visualizations
- ❌ Multiple export formats
- ❌ User authentication
- ❌ Complex scheduling
- ❌ Mobile app
- ❌ Real-time processing
- ❌ Advanced data validation
- ❌ Multiple user support

### **Focus on Core Value**
- ✅ Clean data fetching
- ✅ Meaningful swimming analysis
- ✅ Simple but effective UI
- ✅ CSV export with insights
- ✅ Basic progress tracking

---

## 🚨 Risk Mitigation & Contingency Plans

### **High-Risk Items to Avoid**
1. **Complex authentication flows** - Use simple credential input
2. **Advanced data validation** - Basic checks only
3. **Multiple output formats** - Focus on CSV + dashboard
4. **Real-time processing** - Batch processing is fine
5. **Mobile optimization** - Desktop-first approach

### **Contingency Plans**
- **Week 3 backup**: If data validation takes too long, skip to basic analysis
- **Week 5 backup**: If UI is complex, use simple Streamlit forms
- **Week 6 backup**: Focus on core functionality over polish

### **Success Factors**
- **Consistent weekly progress** (even if small)
- **Regular testing** (don't let bugs accumulate)
- **Documentation** (write as you go)
- **Realistic expectations** (quality over speed)

---

## 📊 Success Metrics for 7 Weeks

### **Minimum Viable Product**
- [ ] User can upload Garmin data
- [ ] System provides meaningful swimming insights
- [ ] Clean, maintainable code architecture
- [ ] Basic but functional user interface
- [ ] Portfolio-ready documentation

### **Nice-to-Have (if time permits)**
- [ ] Basic progress charts
- [ ] Data quality warnings
- [ ] Export functionality
- [ ] Error handling for edge cases

---

## �� Weekly Checkpoints

### **Week 1 Checkpoint**
- [ ] Codebase refactored and working
- [ ] New architecture in place
- [ ] Basic functionality preserved

### **Week 2 Checkpoint**
- [ ] Swimming metrics calculated correctly
- [ ] Analysis functions working
- [ ] Data models properly structured

### **Week 3 Checkpoint**
- [ ] Session-level analysis working
- [ ] Data validation implemented
- [ ] Interval analysis functional

### **Week 4 Checkpoint**
- [ ] Advanced analysis features working
- [ ] Progress tracking functional
- [ ] Recommendations generating

### **Week 5 Checkpoint**
- [ ] Dashboard functional
- [ ] User can interact with system
- [ ] Export functionality working

### **Week 6 Checkpoint**
- [ ] System thoroughly tested
- [ ] Major bugs resolved
- [ ] Performance optimized

### **Week 7 Checkpoint**
- [ ] Documentation complete
- [ ] Portfolio presentation ready
- [ ] Project deployable

---

## �� Tips for Success

### **Time Management**
- **Start each week strong** - Get the foundation right
- **Test early and often** - Don't let bugs accumulate
- **Keep scope focused** - Resist adding "cool features"
- **Document as you go** - Don't leave it all for Week 7

### **Development Approach**
- **MVP mindset** - Build core functionality first
- **Iterative development** - Small working pieces
- **Regular commits** - Track progress and rollback if needed
- **User feedback** - Test with real data early

### **Quality vs Speed**
- **Code quality** - Maintainable, readable code
- **Functionality** - Core features working end-to-end
- **Documentation** - Clear setup and usage instructions
- **Testing** - Basic error handling and validation

---

## 🏆 Portfolio Value

### **What You'll Have**
- **Real API integration** (Garmin Connect)
- **Data analysis pipeline** (ETL + insights)
- **Clean software architecture** (refactored codebase)
- **User interface** (Streamlit dashboard)
- **End-to-end functionality** (data in → insights out)

### **Employer Appeal**
- **Demonstrates real-world skills** beyond classroom assignments
- **Shows API integration experience** - highly valued
- **Proves data analysis + software engineering** combination
- **Evidence of self-directed learning**
- **Portfolio-ready project** with clear documentation

---

## 📚 Resources & References

### **Swimming Analysis**
- FINA swimming standards
- Swimming coaching literature
- Sports science research papers

### **Technical Resources**
- Streamlit documentation
- Pandas/NumPy tutorials
- Python async programming guides
- Data visualization best practices

### **Architecture Resources**
- Clean Architecture principles
- SOLID principles
- Python design patterns

---

## 🎯 Next Steps

1. **Review and approve this workflow**
2. **Set up development environment**
3. **Create Git repository with proper branching**
4. **Begin Week 1: Foundation & Refactoring**
5. **Set up weekly progress reviews**

---

## 📝 Progress Tracking

### **Daily Log Template**
Date: [Date]
Hours Worked: [X] hours
Tasks Completed:
[ ] Task 1
[ ] Task 2
Challenges Faced:
[Challenge description]
Solutions Found:
[Solution description]
Tomorrow's Goals:
[ ] Goal 1
[ ] Goal 2

### **Weekly Review Template**
Week [X] Review
Goals Met: [X]/[Y]
Hours Logged: [X] hours
Major Accomplishments:
[Accomplishment 1]
[Accomplishment 2]
Challenges Overcome:
[Challenge 1]
[Challenge 2]
Next Week's Focus:
[Focus area 1]
*Last Updated: [Current Date]*
*Project Manager: [Your Name]*
*Timeline: 7 weeks (Summer Sprint)*
*Target Completion: [End Date]*

---

## **Week 2: ETL Orchestration & Production Readiness** *(September 9-15, 2025)*

### **Strategic Focus**: 
Transform our working ETL pipeline into a **production-ready, enterprise-grade data orchestration system** with proper load management, monitoring, and service architecture.

### **Week 2 Goals**:
- **ETL Orchestration**: Implement scheduling, retry logic, and external triggers
- **Load Management**: Add rate limiting, circuit breakers, and staging layers
- **Monitoring & Observability**: Set up Grafana dashboards and alerting
- **Repository Restructuring**: Organize codebase to show service boundaries
- **Swimming Data ETL**: Complete swimming data processing pipeline

### **Day 1-2: Repository Restructuring & Service Architecture**
**Hours**: 6-8 hours
**Focus**: Organize codebase to demonstrate service boundaries and enterprise thinking

#### **Optional Reading** (15-30 minutes):
- **Microservices Patterns**: https://microservices.io/patterns/ (Service boundaries, API design)
- **12-Factor App**: https://12factor.net/ (Configuration management, best practices)

#### **Tasks**:
- [ ] **Repository Restructuring**: Reorganize into service-based architecture:
  - [ ] `src/ingestion/` - Garmin API client and data fetching
  - [ ] `src/etl/` - Data processing pipeline and orchestration
  - [ ] `src/database/` - Database management and schema
  - [ ] `src/monitoring/` - Grafana integration and observability
  - [ ] `src/dashboard/` - Web interface and status monitoring
  - [ ] `src/shared/` - Common models, utilities, and configuration
- [ ] **Infrastructure Setup**: Add `infrastructure/` directory for deployment configs
- [ ] **Documentation**: Create `docs/` directory with architecture documentation
- [ ] **Scripts**: Add `scripts/` directory for setup and deployment automation
- [ ] **Update Imports**: Fix all import paths after restructuring
- [ ] **Test Suite**: Ensure all tests pass after restructuring

#### **Deliverables**:
- [ ] Clean service-based repository structure
- [ ] Updated documentation and README
- [ ] All tests passing with new structure
- [ ] Clear separation of concerns between services

### **Day 3-4: ETL Orchestration & Load Management**
**Hours**: 8-10 hours
**Focus**: Implement production-grade orchestration with proper load management

#### **Optional Reading** (20-40 minutes):
- **APScheduler Documentation**: https://apscheduler.readthedocs.io/en/stable/ (Core orchestration library)
- **Circuit Breaker Pattern**: https://martinfowler.com/bliki/CircuitBreaker.html (Error handling pattern)
- **Exponential Backoff**: https://cloud.google.com/iot/docs/how-tos/exponential-backoff (Retry strategy)

#### **Tasks**:
- [ ] **ETL Orchestration**: Implement `ETLOrchestrator` class with APScheduler:
  - [ ] Local scheduling with configurable intervals
  - [ ] Webhook-based external triggering
  - [ ] Graceful shutdown and resume capability
  - [ ] Job queuing and execution management
- [ ] **Load Management**: Add enterprise-grade load management:
  - [ ] Exponential backoff with jitter for API calls
  - [ ] Circuit breaker pattern for API failures
  - [ ] Staging layer for rate limiting mitigation
  - [ ] Batch processing with configurable sizes
- [ ] **Retry Logic**: Implement robust retry mechanisms:
  - [ ] Configurable retry attempts and delays
  - [ ] Failure classification (retryable vs. permanent)
  - [ ] Dead letter queue for failed records
  - [ ] Recovery and rollback capabilities

#### **Deliverables**:
- [ ] Production-ready ETL orchestrator
- [ ] Robust load management system
- [ ] Comprehensive retry and recovery logic
- [ ] Configuration management for all parameters

### **Day 5-6: Monitoring & Observability**
**Hours**: 6-8 hours
**Focus**: Set up enterprise-grade monitoring and alerting

#### **Optional Reading** (30-60 minutes):
- **Grafana Documentation**: https://grafana.com/docs/ (Dashboard setup and configuration)
- **Google SRE - Monitoring**: https://sre.google/sre-book/monitoring-distributed-systems/ (Production monitoring strategies)
- **The Four Golden Signals**: https://sre.google/sre-book/monitoring-distributed-systems/ (Essential metrics)

#### **Tasks**:
- [ ] **Grafana Integration**: Set up monitoring dashboard:
  - [ ] Docker-based Grafana setup
  - [ ] InfluxDB integration for time-series data
  - [ ] ETL pipeline health dashboard
  - [ ] Data quality monitoring dashboard
- [ ] **Alerting System**: Implement notification system:
  - [ ] Discord webhook integration for alerts
  - [ ] Email notifications for critical failures
  - [ ] Slack integration (optional)
  - [ ] Alert escalation and routing
- [ ] **Logging & Metrics**: Enhanced observability:
  - [ ] Structured logging with correlation IDs
  - [ ] Performance metrics collection
  - [ ] Error tracking and classification
  - [ ] Data quality scoring and reporting

#### **Deliverables**:
- [ ] Live Grafana dashboard with ETL metrics
- [ ] Discord notification system for alerts
- [ ] Comprehensive logging and metrics collection
- [ ] Data quality monitoring and reporting

### **Day 7: Swimming Data ETL & Integration Testing**
**Hours**: 4-6 hours
**Focus**: Complete swimming data processing and end-to-end testing

#### **Optional Reading** (15-30 minutes):
- **ETL Best Practices**: https://www.stitchdata.com/etl-best-practices/ (Production ETL patterns)

#### **Tasks**:
- [ ] **Swimming Data Processors**: Implement remaining ETL processors:
  - [ ] `SwimmingSessionsProcessor` - Session-level data processing
  - [ ] `SwimmingIntervalsProcessor` - Training interval processing
  - [ ] `SwimmingLapsProcessor` - Lap-level data processing
  - [ ] `SwimmingLengthsProcessor` - Length-level data processing
- [ ] **Integration Testing**: End-to-end pipeline testing:
  - [ ] Test complete data flow from API to database
  - [ ] Validate data quality and completeness
  - [ ] Test error handling and recovery scenarios
  - [ ] Performance testing with rate limiting
- [ ] **Documentation**: Update architecture and deployment docs

#### **Deliverables**:
- [ ] Complete swimming data ETL pipeline
- [ ] End-to-end integration tests passing
- [ ] Performance benchmarks and optimization
- [ ] Updated documentation and deployment guides

### **Week 2 Success Criteria**:
- [ ] **Production-Ready ETL**: Orchestrated, monitored, and fault-tolerant
- [ ] **Enterprise Architecture**: Service-based structure with clear boundaries
- [ ] **Operational Excellence**: Monitoring, alerting, and observability
- [ ] **Complete Data Pipeline**: All data types processed and stored
- [ ] **Portfolio Value**: Demonstrates senior-level system design and operations

### **Key Learning Outcomes**:
- **ETL Orchestration**: Understanding of production data pipeline management
- **Load Management**: Enterprise patterns for handling external API limitations
- **Monitoring & Observability**: Production-grade system monitoring and alerting
- **Service Architecture**: Clean separation of concerns and modular design
- **Operational Excellence**: Production readiness and fault tolerance

---

## 🔄 Data Import & Duplicate Prevention

### **Duplicate Prevention Mechanism** *(Current Implementation)*

#### **Problem Statement**
- **Data Integrity**: Prevent duplicate records when re-running imports
- **Resume Capability**: Allow interrupted imports to resume from last successful date
- **Idempotent Operations**: Ensure imports can be run multiple times safely
- **Error Recovery**: Handle partial failures gracefully

#### **Current Implementation Strategy**

##### **1. Database-Level Deduplication**
```sql
-- Using INSERT OR REPLACE for idempotent imports
INSERT OR REPLACE INTO recovery (
    date, hrv_last_night_avg, hrv_weekly_avg, hrv_last_night_5min_high,
    hrv_status, hrv_feedback_phrase, average_stress, resting_heart_rate,
    sleep_score, sleep_time_seconds
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

##### **2. Date-Based Duplicate Detection**
```python
# In each processor's load method
async def load(self, data: Optional[RecoveryMetrics], db_manager: DatabaseManager) -> int:
    """Load RecoveryMetrics into database with duplicate prevention."""
    if not data:
        return 0
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if data already exists for this date
        cursor.execute("SELECT COUNT(*) FROM recovery WHERE date = ?", (data.date.isoformat(),))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"Data for {data.date} already exists, updating...")
        
        # Use INSERT OR REPLACE for idempotent operation
        cursor.execute("""
            INSERT OR REPLACE INTO recovery (
                date, hrv_last_night_avg, hrv_weekly_avg, hrv_last_night_5min_high,
                hrv_status, hrv_feedback_phrase, average_stress, resting_heart_rate,
                sleep_score, sleep_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.date.isoformat(),
            data.hrv_last_night_avg,
            data.hrv_weekly_avg,
            data.hrv_last_night_5min_high,
            data.hrv_status,
            data.hrv_feedback_phrase,
            data.average_stress,
            data.resting_heart_rate,
            data.sleep_score,
            data.sleep_time_seconds
        ))
        conn.commit()
        return 1
```

##### **3. Import Status Tracking**
```python
# In population script
def check_existing_data(db_manager: DatabaseManager, start_date: date, end_date: date) -> Dict[str, int]:
    """Check which dates already have data in the database."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, COUNT(*) as record_count 
            FROM recovery 
            WHERE date BETWEEN ? AND ? 
            GROUP BY date
        """, (start_date.isoformat(), end_date.isoformat()))
        
        existing_data = {row[0]: row[1] for row in cursor.fetchall()}
        return existing_data

def get_missing_dates(start_date: date, end_date: date, existing_data: Dict[str, int]) -> List[date]:
    """Get list of dates that need to be imported."""
    missing_dates = []
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.isoformat() not in existing_data:
            missing_dates.append(current_date)
        current_date += timedelta(days=1)
    
    return missing_dates
```

##### **4. Resume Capability**
```python
# In population script main function
def main():
    """Main function with duplicate prevention and resume capability."""
    
    # Check existing data first
    existing_data = check_existing_data(db_manager, START_DATE, END_DATE)
    missing_dates = get_missing_dates(START_DATE, END_DATE, existing_data)
    
    if not missing_dates:
        print("✅ All data already imported!")
        return
    
    print(f"📊 Found {len(existing_data)} existing records")
    print(f"🔄 Need to import {len(missing_dates)} missing dates")
    
    # Only process missing dates
    for date in missing_dates:
        # ... import logic for missing dates only
```

#### **Benefits of Current Implementation**

##### **1. Data Integrity**
- **No Duplicates**: `INSERT OR REPLACE` ensures unique records per date
- **Consistent State**: Database always reflects latest imported data
- **Atomic Operations**: Each date import is a single transaction

##### **2. Operational Efficiency**
- **Resume Capability**: Can restart interrupted imports from last successful date
- **Selective Import**: Only import missing dates, skip existing ones
- **Idempotent**: Can run import script multiple times safely

##### **3. Error Recovery**
- **Partial Success**: Failed dates don't affect successful ones
- **Retry Logic**: Can retry failed dates without re-importing successful ones
- **Status Visibility**: Clear logging of what was imported vs. skipped

#### **Future Enhancements** *(Post-MVP)*

##### **1. Import Metadata Table**
```sql
CREATE TABLE import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    end_date DATE,
    total_dates INTEGER,
    successful_dates INTEGER,
    failed_dates INTEGER,
    status TEXT, -- 'COMPLETED', 'PARTIAL', 'FAILED'
    error_details TEXT
);
```

##### **2. Advanced Resume Logic**
```python
class ImportManager:
    def get_last_successful_import(self) -> Optional[date]:
        """Get the last date that was successfully imported."""
        
    def get_failed_dates(self) -> List[date]:
        """Get list of dates that failed during last import."""
        
    def resume_import(self, start_date: date, end_date: date) -> None:
        """Resume import from last successful date."""
```

##### **3. Data Validation & Rollback**
```python
class DataValidator:
    def validate_imported_data(self, date: date) -> bool:
        """Validate that imported data is complete and correct."""
        
    def rollback_date(self, date: date) -> None:
        """Rollback import for a specific date if validation fails."""
```

#### **Current Status**
- ✅ **Basic Duplicate Prevention**: `INSERT OR REPLACE` implemented
- ✅ **Date-Based Detection**: Processors check for existing data
- ✅ **Resume Capability**: Population script can skip existing dates
- ✅ **Error Isolation**: Failed dates don't affect successful ones
- ✅ **Recovery Data Import**: 47 days imported, 15 with complete data
- 🔄 **Import Status Tracking**: Basic logging implemented
- ⏳ **Advanced Features**: Metadata table and validation (future)

#### **Data Quality Analysis Required**
- **Success Rate**: 31.9% (15/47 days with complete data)
- **Rate Limiting Impact**: 429 errors after ~12 successful imports
- **Data Availability**: Need to investigate why some dates have no data
- **Retry Strategy**: Need exponential backoff for rate limiting
- **Data Completeness**: Analyze patterns in missing vs. available data

---

## 📊 Exploratory Data Analysis (EDA) Requirements

### **Recovery Data EDA** *(Current Priority)*

#### **Problem Statement**
- **Partial Data Success**: Only 31.9% of dates have complete recovery data
- **Rate Limiting Impact**: 429 errors after ~12 successful API calls
- **Data Quality Questions**: Why do some dates have no data from Garmin?
- **Optimization Needs**: How to improve success rate and handle rate limiting?

#### **EDA Objectives**

##### **1. Data Availability Analysis**
```python
# Analyze patterns in data availability
def analyze_data_availability():
    """Investigate why only 31.9% of dates have complete data."""
    
    # Check if missing data is due to:
    # - Rate limiting (429 errors)
    # - No data from Garmin for those dates
    # - API response structure issues
    # - Authentication failures
```

##### **2. Rate Limiting Impact Assessment**
```python
# Analyze rate limiting patterns
def analyze_rate_limiting():
    """Understand Garmin API rate limiting behavior."""
    
    # Questions to investigate:
    # - How many requests before rate limiting kicks in?
    # - What's the cooldown period?
    # - Can we optimize request timing?
    # - Should we implement exponential backoff?
```

##### **3. Data Quality Pattern Analysis**
```python
# Analyze data quality patterns
def analyze_data_quality():
    """Investigate patterns in available vs. missing data."""
    
    # Analyze:
    # - Are missing dates random or clustered?
    # - Do certain days of week have more data?
    # - Are there seasonal patterns?
    # - Is data availability related to activity levels?
```

##### **4. API Response Structure Investigation**
```python
# Deep dive into API responses
def investigate_api_responses():
    """Analyze raw API responses for data availability patterns."""
    
    # Check:
    # - What does a "no data" response look like?
    # - Are there different response structures?
    # - Can we detect data availability before processing?
    # - Are there alternative endpoints for missing data?
```

#### **EDA Implementation Plan**

##### **Phase 1: Data Collection Analysis**
- [ ] Create detailed import logs with timestamps
- [ ] Analyze success/failure patterns by date
- [ ] Map rate limiting occurrences to specific dates
- [ ] Identify data availability patterns

##### **Phase 2: API Behavior Investigation**
- [ ] Test API rate limiting thresholds
- [ ] Analyze response structures for different scenarios
- [ ] Investigate alternative data endpoints
- [ ] Document API behavior patterns

##### **Phase 3: Optimization Strategy**
- [ ] Design exponential backoff retry logic
- [ ] Implement intelligent request timing
- [ ] Create data availability prediction
- [ ] Optimize import batch sizes

##### **Phase 4: Data Quality Reporting**
- [ ] Create data completeness dashboards
- [ ] Generate data quality metrics
- [ ] Implement automated data validation
- [ ] Create data availability alerts

#### **Expected Outcomes**
- **Improved Success Rate**: Target 80%+ data completeness
- **Rate Limiting Handling**: Robust retry logic with exponential backoff
- **Data Quality Insights**: Understanding of Garmin data availability patterns
- **Optimized Import Process**: Efficient, reliable data import pipeline

#### **Tools and Techniques**
- **Jupyter Notebooks**: For interactive data analysis
- **SQL Queries**: For data pattern analysis
- **API Testing**: For rate limiting investigation
- **Statistical Analysis**: For data availability patterns
- **Visualization**: For data quality reporting

---

## 🔮 Future Features (Post-MVP)

### **Swimming Interval Data Analysis** *(Future Enhancement)*

#### **Feature Overview**
Add detailed interval/lap-level data analysis to provide more granular swimming insights beyond session summaries.

#### **Current Status Analysis**
- **API Research Completed**: Current activities endpoint provides summary data only
- **Available Data**: `lapCount: 16`, `activeLengths: 24`, `splitSummaries` (workout structure)
- **Missing Data**: Individual lap metrics (distance, duration, pace, heart rate, strokes, SWOLF per lap)
- **Scope Assessment**: Requires separate API endpoint research and implementation

#### **Proposed Architecture**

##### **1. Independent Data Models**
```python
# Existing session data (current implementation)
@dataclass
class SwimmingSession:
    session_id: str
    start_time: datetime
    end_time: datetime
    total_distance: float
    total_duration: float
    metrics: SwimmingMetrics
    # No intervals here - keeps core simple

# New interval data (future feature)
@dataclass
class SwimmingInterval:
    interval_id: str
    session_id: str  # Foreign key to link to session
    interval_number: int
    distance: float
    duration: float
    pace_per_100m: float
    heart_rate: Optional[float] = None
    strokes: Optional[int] = None
    swolf: Optional[float] = None
```

##### **2. Separate Database Tables**
```sql
-- Existing session table (current)
CREATE TABLE swimming_sessions (
    session_id TEXT PRIMARY KEY,
    date DATE,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_distance REAL,
    total_duration REAL,
    -- ... other session fields
);

-- New intervals table (future)
CREATE TABLE swimming_intervals (
    interval_id TEXT PRIMARY KEY,
    session_id TEXT,
    interval_number INTEGER,
    distance REAL,
    duration REAL,
    pace_per_100m REAL,
    heart_rate REAL,
    strokes INTEGER,
    swolf REAL,
    FOREIGN KEY (session_id) REFERENCES swimming_sessions(session_id)
);
```

#### **Implementation Strategy**

##### **Phase 1: Core Architecture (Current)**
- ✅ Move processing logic to orchestration layer
- ✅ Build swimming analyzer with session data
- ✅ Create database schema for sessions
- ✅ Focus on session-level insights

##### **Phase 2: Interval Feature (Future)**
- [ ] Research additional Garmin API endpoints for detailed lap data
- [ ] Create separate `SwimmingInterval` data model
- [ ] Add intervals table to database schema
- [ ] Build interval data fetching logic
- [ ] Create interval-based analytics functions

##### **Phase 3: Advanced Analytics (Future)**
- [ ] Data validation using interval data
- [ ] More accurate session summaries from interval aggregation
- [ ] Pace consistency analysis across intervals
- [ ] Fatigue pattern detection from lap-by-lap data
- [ ] SWOLF trend analysis
- [ ] Stroke efficiency per interval

#### **Advanced Analytics Opportunities**
```python
# Future interval-based analytics
class IntervalAnalyzer:
    def analyze_pace_consistency(self, session_id: str) -> Dict:
        """Analyze pace consistency across intervals"""
        
    def detect_fatigue_patterns(self, session_id: str) -> Dict:
        """Detect fatigue patterns from interval data"""
        
    def validate_session_accuracy(self, session_id: str) -> Dict:
        """Validate session summary against interval data"""
        
    def calculate_interval_swolf_trends(self, session_id: str) -> Dict:
        """Analyze SWOLF trends across intervals"""
        
    def analyze_stroke_efficiency_per_interval(self, session_id: str) -> Dict:
        """Analyze stroke efficiency changes across intervals"""
```

#### **Time Estimation**
- **API Research**: 2-4 hours (finding right endpoint, understanding response)
- **Implementation**: 4-6 hours (new methods, error handling, testing)
- **Integration**: 2-3 hours (fitting into existing architecture)
- **Testing & Debugging**: 2-4 hours (edge cases, error scenarios)
- **Total**: **10-17 hours** (2-3 days of work)

#### **Risk Assessment**
- **High Complexity**: Requires additional API endpoint research
- **Scope Creep Risk**: Could easily expand beyond time limits
- **Integration Complexity**: New data paths and error handling
- **Performance Impact**: Additional API calls per session

#### **Decision Rationale**
- **Current Priority**: Focus on session-level analysis with rich existing data
- **Future Enhancement**: Add intervals as separate feature branch
- **Portfolio Value**: Session analysis provides excellent foundation
- **Time Management**: Avoid scope creep during 7-week sprint

#### **Implementation Notes**
- **Feature Branch**: `feature/swimming-intervals`
- **Separate Sprint**: After core analyzer is complete
- **Proper Time Allocation**: When 2-3 days can be dedicated
- **Independent Development**: No impact on core functionality