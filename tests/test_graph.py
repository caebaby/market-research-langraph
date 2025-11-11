#!/usr/bin/env python
"""
Test suite for Market Research Workflow Graph
Configured to run from tests/ folder
"""

import os
import sys
import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Any, List

# Add parent directory to Python path so we can import from team_icp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the workflow module
from team_icp.workflows.graph import (
    ICPGraph, 
    WorkflowConfig, 
    GraphState,
    create_workflow,
    validate_environment
)

# ==============================================
# 1. FIXTURES AND SETUP
# ==============================================

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables"""
    env_vars = {
        "ANTHROPIC_API_KEY": "test-api-key",
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_PROJECT": "test-project",
        "BRAVE_API_KEY": "test-brave-key",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "test-qdrant-key",
        "AGENT_TEMPERATURE_CREATIVE": "0.7",
        "AGENT_TEMPERATURE_RESEARCH": "0.5",
        "AGENT_TEMPERATURE_ANALYTICAL": "0.3",
        "MAX_TOKENS_RESEARCH": "8000",
        "MAX_TOKENS_CREATIVE": "8000",
        "MAX_TOKENS_SUMMARY": "4000"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def workflow_config():
    """Create test workflow configuration"""
    return WorkflowConfig(
        verbose=False,
        timeout_per_agent=30,
        max_retries=2,
        memory_enabled=False,  # Disable for most tests
        search_enabled=False,  # Disable for most tests
        parallel_execution=False,
        min_word_count=100,
        quality_threshold=0.5
    )


@pytest.fixture
def mock_llm():
    """Create mock LLM"""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Test analysis output with multiple sentences. This provides insight into patterns. Important findings are revealed here.")
    mock.predict.return_value = "Test prediction output"
    return mock


@pytest.fixture
def mock_memory_system():
    """Create mock memory system"""
    mock = MagicMock()
    mock.retrieve_memories.return_value = [
        MagicMock(content="Previous insight 1", importance=0.8, timestamp=datetime.now()),
        MagicMock(content="Previous insight 2", importance=0.7, timestamp=datetime.now())
    ]
    mock.store_memory.return_value = True
    mock.get_client_context.return_value = {"test_agent": ["memory1", "memory2"]}
    return mock


@pytest.fixture
def mock_search_system():
    """Create mock search system"""
    mock = MagicMock()
    mock.run.return_value = json.dumps([
        {"title": "Result 1", "link": "http://example.com/1", "snippet": "Test snippet 1"},
        {"title": "Result 2", "link": "http://example.com/2", "snippet": "Test snippet 2"}
    ])
    return mock


@pytest.fixture
def test_state() -> Dict[str, Any]:
    """Create test state"""
    return {
        "company": "TestCorp",
        "business_context": "Test context",
        "template_data": {"industry": "Technology", "company_name": "TestCorp"},
        "client_id": "test_client",
        "request_id": "test_request",
        "requested_agents": ["psychological", "voice_of_customer", "competitor"],
        "agent_config": {"temperatures": {"psychological": 0.7}},
        "search_enabled": False,
        "web_sources": [],
        "memory_enabled": False,
        "memories_loaded": {},
        "memories_stored": {},
        "agent_outputs": {},
        "agent_errors": {},
        "agent_metrics": {},
        "completed_agents": [],
        "failed_agents": [],
        "insights": {},
        "quality_scores": {},
        "current_agent": None,
        "slack_updater": None,
        "progress_messages": [],
        "final_report": None,
        "gtm_blueprint": None,
        "statistics": {},
        "start_time": time.time(),
        "end_time": None,
        "agent_timings": {},
        "analysis_depth": "comprehensive",
        "source": "test"
    }


@pytest.fixture
def mock_agent():
    """Create a mock agent"""
    mock = MagicMock()
    mock.execute.return_value = {
        "analysis": "Mock agent analysis output",
        "metrics": {"quality": 0.8}
    }
    return mock


# ==============================================
# 2. UNIT TESTS - WORKFLOW INITIALIZATION
# ==============================================

class TestWorkflowInitialization:
    """Test workflow initialization and configuration"""
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_workflow_creation_default(self, mock_env_vars):
        """Test creating workflow with default config"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph()
            
            assert workflow is not None
            assert workflow.config is not None
            assert workflow.verbose == False
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_workflow_creation_with_config(self, mock_env_vars, workflow_config):
        """Test creating workflow with custom config"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            assert workflow.config == workflow_config
            assert workflow.config.min_word_count == 100
            assert workflow.config.quality_threshold == 0.5
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_workflow_verbose_mode(self, mock_env_vars):
        """Test verbose mode initialization"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(verbose=True)
            
            assert workflow.verbose == True
            assert workflow.config.verbose == True
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', False)
    def test_workflow_without_langgraph(self, mock_env_vars):
        """Test workflow creation when LangGraph not available"""
        workflow = ICPGraph()
        
        assert workflow is not None
        assert workflow.compiled_graph is None  # Should be None without LangGraph


# ==============================================
# 3. UNIT TESTS - AGENT MANAGEMENT
# ==============================================

class TestAgentManagement:
    """Test agent initialization and management"""
    
    @patch('team_icp.workflows.graph.ChatAnthropic')
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_create_default_llm(self, mock_anthropic, mock_env_vars, workflow_config):
        """Test LLM creation for agents"""
        mock_llm_instance = Mock()
        mock_anthropic.return_value = mock_llm_instance
        
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            llm = workflow._create_default_llm("psychological")
            
            assert llm == mock_llm_instance
            mock_anthropic.assert_called_once()
            
            # Check temperature was set correctly
            call_kwargs = mock_anthropic.call_args.kwargs
            assert call_kwargs['temperature'] == 0.7  # From env var
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_get_llm_for_agent_with_function(self, mock_env_vars, workflow_config):
        """Test getting LLM when bot provides function"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            mock_llm = Mock()
            mock_get_llm = Mock(return_value=mock_llm)
            
            state = {
                "agent_config": {"get_llm_func": mock_get_llm}
            }
            
            result = workflow._get_llm_for_agent("psychological", state)
            
            assert result == mock_llm
            mock_get_llm.assert_called_once_with("psychological")
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_prepare_agent_context(self, mock_env_vars, workflow_config, test_state):
        """Test context preparation for agents"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            context = workflow._prepare_agent_context(test_state, "psychological")
            
            assert context["company_name"] == "TestCorp"
            assert context["client_id"] == "test_client"
            assert context["business_context"] == "Test context"
            assert context["industry"] == "Technology"
            assert "insights" in context


# ==============================================
# 4. UNIT TESTS - QUALITY SCORING
# ==============================================

class TestQualityScoring:
    """Test quality scoring and statistics"""
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_calculate_quality_score_high(self, workflow_config):
        """Test quality score calculation for high-quality output"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            # High quality output - 500 words with keywords
            output = " ".join(["psychological identity fear unconscious"] * 125)
            score = workflow._calculate_quality_score(output, "psychological")
            
            assert score > 0.5
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_calculate_quality_score_low(self, workflow_config):
        """Test quality score calculation for low-quality output"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            # Low quality output
            output = "short output"
            score = workflow._calculate_quality_score(output, "psychological")
            
            assert score < 0.3
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_calculate_statistics(self, workflow_config, test_state):
        """Test statistics calculation"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            # Add some data to state
            test_state["agent_outputs"] = {
                "psychological": "Test output " * 100,
                "voice_of_customer": "Customer feedback " * 150
            }
            test_state["quality_scores"] = {
                "psychological": 0.7,
                "voice_of_customer": 0.8
            }
            test_state["completed_agents"] = ["psychological", "voice_of_customer"]
            
            stats = workflow._calculate_statistics(test_state)
            
            assert stats["total_agents"] == 3
            assert stats["successful_agents"] == 2
            assert stats["overall_quality"] == 0.75
            assert stats["total_words"] > 0


# ==============================================
# 5. INTEGRATION TESTS - BASIC WORKFLOW
# ==============================================

class TestBasicWorkflow:
    """Test basic workflow operations"""
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_create_initial_state(self, workflow_config):
        """Test initial state creation"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            inputs = {
                "company": "TestCorp",
                "business_context": "Test context",
                "client_id": "test_client",
                "requested_agents": ["psychological"]
            }
            
            state = workflow._create_initial_state(inputs)
            
            assert state["company"] == "TestCorp"
            assert state["client_id"] == "test_client"
            assert "psychological" in state["requested_agents"]
            assert state["memory_enabled"] == False  # Based on config
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_format_results(self, workflow_config, test_state):
        """Test result formatting"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            # Add some outputs
            test_state["agent_outputs"] = {
                "psychological": "Psychological analysis",
                "voice_of_customer": "Voice analysis"
            }
            test_state["statistics"] = {"overall_quality": 0.75}
            
            results = workflow._format_results(test_state)
            
            assert "result" in results
            assert "psychological" in results["result"]
            assert results["statistics"]["overall_quality"] == 0.75


# ==============================================
# 6. MOCK EXECUTION TEST
# ==============================================

class TestMockExecution:
    """Test mock execution for development"""
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', False)
    def test_mock_execution(self, workflow_config, test_state):
        """Test mock execution when graph not available"""
        workflow = ICPGraph(config=workflow_config)
        
        result = workflow._mock_execution(test_state)
        
        assert len(result["agent_outputs"]) > 0
        assert result["final_report"] is not None
        assert "[MOCK" in list(result["agent_outputs"].values())[0]


# ==============================================
# 7. ERROR HANDLING TESTS
# ==============================================

class TestErrorHandling:
    """Test error handling and recovery"""
    
    @patch('team_icp.workflows.graph.LANGGRAPH_AVAILABLE', True)
    def test_create_error_result(self, workflow_config):
        """Test error result creation"""
        with patch('team_icp.workflows.graph.StateGraph'):
            workflow = ICPGraph(config=workflow_config)
            
            error_result = workflow._create_error_result("Test error")
            
            assert error_result["error"] == "Test error"
            assert "[ERROR]" in error_result["final_report"]
            assert error_result["statistics"]["overall_quality"] == 0.0


# ==============================================
# 8. ENVIRONMENT VALIDATION
# ==============================================

def test_validate_environment():
    """Test environment validation"""
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test",
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_PROJECT": "test"
    }):
        assert validate_environment() == True
    
    with patch.dict(os.environ, {}, clear=True):
        assert validate_environment() == False


# ==============================================
# 9. MAIN TEST RUNNER
# ==============================================

if __name__ == "__main__":
    """Run tests directly"""
    print("=" * 80)
    print("RUNNING WORKFLOW TESTS")
    print("=" * 80)
    print("\nTest file location:", __file__)
    print("Working directory:", os.getcwd())
    print("Python path includes:", sys.path[0])
    print("\n" + "=" * 80)
    
    # Use pytest.main for programmatic execution
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "-x",  # Stop on first failure
        "--tb=short",  # Short traceback
        "--color=yes"  # Colored output
    ])
    
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED")
    print("=" * 80)
    
    sys.exit(exit_code)