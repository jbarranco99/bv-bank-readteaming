"""
Test Runner Module for RAI Testing System

This module orchestrates the execution of red team testing against banking chatbots.
It coordinates between the browser automation, hack agent, and success classifier
to conduct and evaluate security tests.
"""

from dotenv import load_dotenv
import os
import asyncio
from chat_browser import AuroraChatbotSession  
from hack_agent import HackAgent, HackAgentDeps
from success_classifier_agent import SuccessClassifierAgent, SuccessClassifierDeps
from pydantic_ai.models.openai import OpenAIModel
from database import Database

# Load environment variables for authentication
load_dotenv()
AURORA_URL = os.getenv("AURORA_BV_URL")
USERNAME = os.getenv("AURORA_USERNAME")
PASSWORD = os.getenv("AURORA_PASSWORD")


async def main(
        attack_type: str, 
        model: str, 
        language: str = "portuguese", 
        tester_instructions: str = "No specific instructions", 
        turns_per_conversation: int = 10, 
        n_tests: int = 1, 
        use_previous_learnings: bool = False
        ):
    """
    Main function that runs the red team testing process.
    
    Args:
        attack_type: Type of security test to perform
        model: Name of the language model to use
        language: Target language for testing
        tester_instructions: Specific test objectives
        turns_per_conversation: Number of exchanges per test
        n_tests: Number of test conversations to run
        use_previous_learnings: Whether to incorporate past insights
    """
    
    # Initialize database connection
    db = Database()

    # Step 1: Query the attack strategy
    strategy_doc = db.get_attack_strategy(attack_type)
    if not strategy_doc:
        print(f"❌ No attack strategy found for '{attack_type}'")
        return
    strategy = strategy_doc["strategy"]

    # Step 2: Query prompt examples for reference
    prompts = db.get_active_prompts(attack_type=attack_type, limit=10)
    if not prompts:
        print(f"❌ No prompts found for attack type '{attack_type}'")
        return

    prompts_array = [p["prompt"] for p in prompts]
    print(f"🧠 Strategy: {strategy}")
    print(f"🪧 Loaded {len(prompts)} prompt examples for '{attack_type}'")

    # Run multiple test conversations if requested
    for conversation_number in range(n_tests):

        # Step 2.1: Load previous learnings if enabled
        if use_previous_learnings:
            previous_learnings = db.get_previous_learnings(attack_type=attack_type)
            if previous_learnings:
                print(f"🔍 Using previous learnings from {1+previous_learnings.count(chr(10))} previous tests")
            else:
                print("❌ No previous learnings found for this attack type.")

        # Step 3: Initialize AI agents and dependencies
        llm = OpenAIModel(model_name=model)
        agent = HackAgent(model=llm)
        deps = HackAgentDeps(
            user_id="test_user_123", 
            language=language, 
            attack_type=attack_type, 
            strategy=strategy, 
            examples=prompts, 
            tester_instructions=tester_instructions,
            previous_learnings=previous_learnings if use_previous_learnings else None)
                  
        message_history = []
        conversation = []

        # Step 4: Set up browser session with chatbot
        print("🚀 Starting Aurora chatbot session test")

        session = AuroraChatbotSession(
            aurora_url=AURORA_URL,
            username=USERNAME,
            password=PASSWORD
        )
        session.initialize_browser()

        if not session.navigate_to_aurora():
            print("❌ Failed to navigate to Aurora")
            session.close()
            return

        if not session.login():
            print("❌ Failed to log in to Aurora")
            session.close()
            return

        # Step 5: Execute conversation loop
        for turn in range(turns_per_conversation):
            if turn == 0:
                response = "Create the first attack prompt, there is no previous message history yet."
            result = await agent.run(response, deps, message_history)
            print(f"Hack Agent: {result.output.prompt}")
            conversation.append("HACK AGENT: "+ result.output.prompt)
            message_history.extend(result.new_messages())

            response = session.send_prompt(result.output.prompt)
            print("\n🤖 Chatbot response:")
            print("-" * 80)
            print(response)
            print("-" * 80)
            conversation.append("AURORA: "+ result.output.prompt)

        # Step 6: Evaluate test success
        success_classifier_agent = SuccessClassifierAgent(model=llm)
        success_classifier_deps = SuccessClassifierDeps(
            language=language,
            attack_type=attack_type,
            strategy=strategy,
            conversation=db.array_to_string(conversation),
            tester_instructions=tester_instructions
        )

        classification_result = await success_classifier_agent.run(
            prompt="Classify the success of the test",
            deps=success_classifier_deps,
        )      

        print(f"Success Classifier Result: {classification_result.output.test_result}")
        print(f"Success Reason: {classification_result.output.success_reason}")

        # Step 7: Store test results
        db.save_test_result(
            attack_type=attack_type,
            language=language,
            tester_instructions=tester_instructions,
            strategy=strategy,
            prompt_examples=prompts_array,
            success=classification_result.output.test_result,
            success_reason=classification_result.output.success_reason,
            learnings=classification_result.output.learnings,
            conversation=conversation,
            turns=turns_per_conversation
        )
        print(f"💾 Saved results for conversation {conversation}")

        # Step 8: Cleanup and reset for next test
        conversation = []
        message_history = []
        session.close()

if __name__ == "__main__":
    # Example attack types:
    # - system_prompt_extraction
    # - policy_evasion
    # - indirect_injection
    # - function_call_abuse
    # - sensitive_data_extraction
    # - misinformation_amplification
    # - bias_toxicity_provocation
    # - role_confusion
    # - resource_drain
    # - self_poisoning
    # - free
    asyncio.run(main(attack_type="system_prompt_extraction", 
                     model="gpt-4.1-mini",
                     language="portuguese",
                     #tester_instructions="Make the chatbot tell a dirty joke",
                     turns_per_conversation=10,
                     n_tests=1,
                     use_previous_learnings = True                     
                     ))



#[
#    "system_prompt_extraction",
#    "policy_evasion",
#    "indirect_injection",
#    "function_call_abuse",
#   "sensitive_data_extraction",
#   "misinformation_amplification",
#   "bias_toxicity_provocation",
#   "role_confusion",
#   "resource_drain",
#   "self_poisoning",
#   "free"
#]