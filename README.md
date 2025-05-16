# Responsible AI Testing System

A comprehensive framework for conducting automated red team testing on Aurora chatbot. This system uses AI agents to generate and evaluate security tests while maintaining detailed records of the process and results.

## Overview

This system is designed to:
- Conduct automated security testing on banking chatbots
- Generate natural language prompts that test system boundaries
- Evaluate the success of security tests
- Store and learn from test results
- Support multiple attack strategies and languages

## Components

### 1. Browser Automation (`chat_browser.py`)
Handles direct interaction with the chatbot interface:
- Browser session management
- Login automation
- Message sending and response collection
- Human-like typing simulation
- Response stabilization monitoring

Key features:
- Uses Selenium and Helium for browser control
- Implements random delays to simulate human behavior
- Handles timeouts and edge cases
- Provides detailed error logging

### 2. Database Management (`database.py`)
Manages all MongoDB operations:
- Stores test results
- Retrieves prompt examples
- Manages attack strategies
- Tracks historical learnings

Collections:
- `prompt_examples_pp`: Example prompts for different attack types
- `attack_types_pp`: Strategy definitions for each attack type
- `test_results_pp`: Results and learnings from tests

### 3. Hack Agent (`hack_agent.py`)
AI agent that generates test prompts:
- Creates natural-language security tests
- Adapts based on chatbot responses
- Uses various personas and approaches
- Learns from previous test results

Features:
- Context-aware prompt generation
- Multiple testing personas
- Strategy-based approach
- Historical learning integration

### 4. Success Classifier (`success_classifier_agent.py`)
Evaluates test effectiveness:
- Analyzes full conversation logs
- Determines test success
- Provides detailed reasoning
- Extracts learnings for future tests

Output includes:
- Success/failure determination
- Detailed success reasoning
- Practical learnings and insights

### 5. Test Runner (`run_test.py`)
Main orchestration module:
- Coordinates all components
- Manages test execution flow
- Handles multiple test iterations
- Stores results and learnings

Supported attack types:
- System prompt extraction
- Policy evasion
- Indirect injection
- Function call abuse
- Sensitive data extraction
- Misinformation amplification
- Bias/toxicity provocation
- Role confusion
- Resource drain
- Self poisoning
- Free-form testing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
MONGO_URI=your_mongodb_connection_string
MONGO_DB_NAME=your_database_name
AURORA_BV_URL=your_chatbot_url
AURORA_USERNAME=your_username
AURORA_PASSWORD=your_password
```

3. Ensure MongoDB is running and accessible
    3.1 Create 3 collections:
        - attack_types_pp
        - prompt_examples_pp
        - test_results_pp

## Usage

Basic test execution:
```python
python run_test.py
```

Custom test configuration:
```python
asyncio.run(main(
    attack_type="policy_evasion",
    model="gpt-4.1-mini",
    language="portuguese",
    tester_instructions="Custom test objective",
    turns_per_conversation=10,
    n_tests=5,
    use_previous_learnings=True
))
```

## Security Considerations

- Never expose API keys or credentials in code
- Monitor resource usage during testing
- Review and approve generated prompts
- Follow responsible disclosure practices
- Respect rate limits and usage policies







