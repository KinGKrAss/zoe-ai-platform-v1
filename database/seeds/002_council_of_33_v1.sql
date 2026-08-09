-- Seed: 002_council_of_33_v1.sql
-- Source of truth: services/zoe-agents/council/council.yaml

INSERT INTO council_agents (agent_code, name, domain, title, capabilities, status)
VALUES
('GOD-002','Finyra','finance','Treasury & Financial Intelligence','["cashflow","financial_analysis","portfolio_analysis","forecasting"]','confirmed'),
('GOD-003','Fortuna','wealth_management','Wealth & Cashflow Management','["asset_overview","liquidity","cashflow","allocation"]','confirmed'),
('GOD-004','Midas','valuation','Valuation & Asset Intelligence','["valuation","market_value","scenario_analysis","benchmarking"]','confirmed'),
('GOD-005','Gaia','real_estate','Real Estate Intelligence','["property_analysis","rent","operating_costs","market_analysis"]','confirmed'),
('GOD-006','Electra','energy','Energy & Infrastructure Intelligence','["energy_analysis","sustainability","infrastructure","production"]','confirmed'),
('GOD-007','Jurena','legal','Legal & Contract Intelligence','["contract_review","legal_research","obligations","clause_analysis"]','confirmed'),
('GOD-008','Themis','compliance','Governance & Compliance','["compliance","governance","controls","regulatory_reporting"]','confirmed'),
('GOD-009','Astraea','strategy','Strategy & Future Intelligence','["strategy","scenarios","planning","long_term_analysis"]','confirmed'),
('GOD-010','Artemis','research','Research & Discovery','["research","data_retrieval","source_analysis","discovery"]','confirmed'),
('GOD-011','Aura','diplomacy','Diplomacy & Stakeholder Intelligence','["negotiation","stakeholder_analysis","diplomacy","relationship_mapping"]','confirmed'),
('GOD-012','Lyra','communication','Communication & Narrative Intelligence','["communication","reporting","narrative","presentation"]','confirmed'),
('GOD-013','Athena','knowledge_strategy','Knowledge & Strategic Reasoning','["knowledge_synthesis","reasoning","decision_support","research_synthesis"]','confirmed'),
('GOD-014','Kyra','leadership','Leadership & System Coordination','["leadership","coordination","prioritization","escalation"]','confirmed'),
('GOD-015','Neuralis','technology','AI & Technology Intelligence','["software_architecture","ai_systems","technical_analysis","automation"]','confirmed'),
('GOD-016','Metis','risk','Risk & Foresight Intelligence','["risk_assessment","stress_testing","early_warning","mitigation"]','reconstructed'),
('GOD-017','Dike','justice','Justice & Dispute Analysis','["dispute_analysis","fairness","evidence_review","case_mapping"]','reconstructed'),
('GOD-018','Sophia','education','Knowledge & Learning','["explanation","training","documentation","knowledge_transfer"]','reconstructed'),
('GOD-019','Hestia','operations','Operations & Resource Management','["operations","resource_planning","workflows","service_management"]','reconstructed'),
('GOD-020','Demetra','sustainability','Sustainability & Development','["sustainability","land_use","resource_efficiency","development"]','reconstructed'),
('GOD-021','Selene','time_series','Temporal Intelligence','["trend_analysis","time_series","forecasting","historical_comparison"]','reconstructed'),
('GOD-022','Iris','information','Information Routing','["information_routing","notifications","summaries","dissemination"]','reconstructed'),
('GOD-023','Theia','data_intelligence','Data Visibility & Analytics','["data_quality","analytics","dashboards","anomaly_detection"]','reconstructed'),
('GOD-024','Eirene','peace','Conflict Prevention & Resolution','["conflict_analysis","deescalation","mediation","scenario_planning"]','reconstructed'),
('GOD-025','Nike','performance','Performance & Objectives','["kpi","objectives","performance_analysis","benchmarking"]','reconstructed'),
('GOD-026','Clio','history','History & Archive Intelligence','["archival_research","chronology","provenance","historical_context"]','reconstructed'),
('GOD-027','Mnemosyne','memory','Memory & Knowledge Continuity','["memory","consolidation","provenance","continuity"]','reconstructed'),
('GOD-028','Harmonia','integration','System Integration & Coherence','["integration","dependency_mapping","consistency","orchestration_support"]','reconstructed'),
('GOD-029','Vesta','security','Security & Protection','["security","access_control","threat_analysis","protection"]','reconstructed'),
('GOD-030','Hera','governance','Institutional Governance','["governance","organizational_structure","policy","oversight"]','reconstructed'),
('GOD-031','Aphrodite','relationships','Relationship & Partnership Intelligence','["relationship_analysis","partnerships","stakeholder_value","reputation"]','reconstructed'),
('GOD-032','Hecate','security_strategy','Thresholds, Contingency & Crisis Intelligence','["contingency","crisis_analysis","access_boundaries","decision_gates"]','reconstructed'),
('GOD-033','Persephone','transformation','Transformation & Change Intelligence','["change_management","transformation","restructuring","transition_planning"]','reconstructed')
ON CONFLICT (agent_code) DO UPDATE SET
  name = EXCLUDED.name,
  domain = EXCLUDED.domain,
  title = EXCLUDED.title,
  capabilities = EXCLUDED.capabilities,
  status = EXCLUDED.status,
  updated_at = NOW();
