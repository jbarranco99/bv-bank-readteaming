"""
Browser automation module for interacting with the Aurora chatbot interface.
Uses Selenium and Helium for browser control and automation.
"""

import os
import time
import random
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import helium

class AuroraChatbotSession:
    """
    Manages a browser session for interacting with the Aurora chatbot.
    Handles browser initialization, navigation, login, and message exchange.
    """
    
    def __init__(self, aurora_url: str, username: str, password: str):
        """
        Initialize a new chatbot session.
        
        Args:
            aurora_url: URL of the Aurora chatbot interface
            username: Login username
            password: Login password
        """
        self.aurora_url = aurora_url
        self.username = username
        self.password = password
        self.driver = None
        self.initialized = False

    def initialize_browser(self):
        """
        Initialize Chrome browser with specific options for automation.
        Sets up a maximized window with disabled extensions and popups.
        """
        if not self.initialized:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-infobars")
            self.driver = helium.start_chrome(options=chrome_options)
            self.initialized = True
            print("✅ Browser initialized")

    def navigate_to_aurora(self) -> bool:
        """
        Navigate to the Aurora chatbot URL.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            helium.go_to(self.aurora_url)
            time.sleep(5)
            print(f"🌐 Navigated to: {self.aurora_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate: {str(e)}")
            return False

    def login(self) -> bool:
        """
        Perform login to the Aurora chatbot interface.
        Handles input of credentials and verification of successful login.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            WebDriverWait(helium.get_driver(), 15).until(
                EC.presence_of_element_located((By.ID, "text_input_1"))
            )

            helium.get_driver().find_element(By.ID, "text_input_1").send_keys(self.username)
            helium.get_driver().find_element(By.ID, "text_input_2").send_keys(self.password)

            try:
                helium.get_driver().find_element(By.XPATH, "//p[text()='Log in']").click()
            except:
                # Try backup login click
                login_buttons = helium.get_driver().find_elements(By.XPATH, "//*[contains(text(), 'Log in')]")
                if login_buttons:
                    login_buttons[0].click()

            time.sleep(5)
            if "dashboard" in self.driver.current_url.lower() or "aurora" in self.driver.current_url.lower():
                print("🔓 Logged in successfully")
                return True
            else:
                print(f"⚠️ Login may have failed. Current URL: {self.driver.current_url}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def send_prompt(self, prompt_text: str) -> str:
        """
        Send a prompt to the chatbot and wait for response.
        
        Features:
        - Types prompt with random delays to simulate human typing
        - Waits for response with timeout
        - Monitors response stabilization
        - Handles various edge cases and errors
        
        Args:
            prompt_text: The text to send to the chatbot
            
        Returns:
            str: The chatbot's response or error message
        """
        try:
            # Wait for input field to be available
            WebDriverWait(helium.get_driver(), 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='stChatInputTextArea']"))
            )
            
            # Find and interact with input field
            chat_input = helium.get_driver().find_element(By.CSS_SELECTOR, "textarea[data-testid='stChatInputTextArea']")
            chat_input.clear()
            
            # Type the prompt character by character (like a human)
            for char in prompt_text:
                chat_input.send_keys(char)
                time.sleep(random.uniform(0.008, 0.009))  # Random delay between keystrokes
            
            time.sleep(0.5)
            chat_input.send_keys(Keys.RETURN)
            print("💬 Prompt sent. Waiting for response...")
            
            # Get current message count
            old_count = len(helium.get_driver().find_elements(By.CSS_SELECTOR, ".stChatMessage"))
            
            # Wait for a new message to appear
            start = time.time()
            timeout = 120  # 2 minutes timeout
            new_count = old_count
            
            while time.time() - start < timeout:
                new_count = len(helium.get_driver().find_elements(By.CSS_SELECTOR, ".stChatMessage"))
                if new_count > old_count:
                    #print(f"✅ New message detected ({new_count} vs {old_count})")
                    break
                time.sleep(0.5)
            
            if new_count <= old_count:
                print("⚠️ No new message detected after timeout")
                return "Error: No response received within timeout"
            
            # Wait for the content to stabilize (stop changing)
            messages = helium.get_driver().find_elements(By.CSS_SELECTOR, ".stChatMessage")
            latest_message = messages[-1]
            
            previous_text = ""
            unchanged_count = 0
            stabilize_timeout = 40  # 40 seconds to stabilize
            stabilize_start = time.time()
            
            #print("🔄 Waiting for response to stabilize...")
            
            # Poll until content stops changing
            while time.time() - stabilize_start < stabilize_timeout:
                try:
                    content_element = latest_message.find_element(By.CSS_SELECTOR, "[data-testid='stChatMessageContent']")
                    current_text = content_element.text.strip()
                    
                    # Debug info
                    #if len(current_text) > 50:
                        #print(f"📝 Current length: {len(current_text)} chars | Unchanged count: {unchanged_count}")
                    #else:
                        #print(f"📝 Current text: '{current_text}' | Unchanged count: {unchanged_count}")
                    
                    if current_text and current_text == previous_text:
                        unchanged_count += 1
                        if unchanged_count >= 6:  # Content unchanged for 3 seconds (6 * 0.5s)
                            print("✅ Response stabilized")
                            return current_text
                    else:
                        unchanged_count = 0
                        
                    previous_text = current_text
                except Exception as e:
                    print(f"⚠️ Error checking content: {e}")
                    
                time.sleep(0.5)
            
            # If we reached here, return whatever we have
            try:
                messages = helium.get_driver().find_elements(By.CSS_SELECTOR, ".stChatMessage")
                latest = messages[-1].find_element(By.CSS_SELECTOR, "[data-testid='stChatMessageContent']")
                result = latest.text.strip()
                print(f"⚠️ Response didn't fully stabilize, returning current content ({len(result)} chars)")
                return result
            except Exception as e:
                print(f"❌ Failed to get final message: {e}")
                return "Error: Failed to retrieve response"
                
        except Exception as e:
            print(f"❌ Failed to send prompt: {str(e)}")
            return f"Error: {str(e)}"

    def close(self):
        """
        Close the browser session and cleanup resources.
        """
        if self.initialized:
            helium.kill_browser()
            self.initialized = False


