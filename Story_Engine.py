# Interactive Children's Adventure Engine v2.0
# This version uses a class structure and connects to the Gemini API for story generation.

import google.generativeai as genai
import re

class StoryEngine:
    def __init__(self, api_key):
        # Configure the AI with the provided key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Story attributes
        self.user_profile = {}
        self.story_mode = ""
        self.story_length = ""
        self.story_text = ""
        self.key_items = []
        self.wisdom_gem = ""
        self.story_map = [] # For future interactive use

    def start(self):
        """Begins the story creation process."""
        print("Hello! I'm ready to create a magical story.")
        self.select_story_mode()
        self.select_story_length()
        self.intake_calibration()
        self.generate_story_with_ai()
        self.generate_adventure_report()

    def select_story_mode(self):
        """Asks user to choose between Linear and Interactive modes."""
        choice = input("Choose your adventure type (A = Linear, B = Interactive): ")
        self.story_mode = "Linear" if choice.upper() == "A" else "Interactive"

    def select_story_length(self):
        """Asks user to choose the story length."""
        choice = input("Choose your story length (A = Short, B = Medium, C = Long): ")
        lengths = {"A": "Short (~400 words)", "B": "Medium (~700 words)", "C": "Long (~1000 words)"}
        self.story_length = lengths.get(choice.upper(), "Medium")

    def intake_calibration(self):
        """Gathers all details about the child and story elements."""
        profile = {}
        # This version supports multiple children and friends
        characters = []
        while True:
            add_char = input("Add a child or friend to the story? (y/n): ").lower()
            if add_char != 'y':
                break
            char = {
                'name': input("  Name: "),
                'age': input("  Age: "),
                'personality': input("  Personality (e.g., 'shy and kind', 'brave and loud'): ")
            }
            characters.append(char)
        profile['characters'] = characters
        
        profile['challenge'] = input("What challenge should the story explore (e.g., 'standing up to bullies')? ")
        profile['magic'] = input("What kind of magic exists in this world (e.g., 'talking animals', 'magic paintbrushes')? ")
        self.user_profile = profile

    def generate_story_with_ai(self):
        """Builds a detailed prompt and calls the Gemini API."""
        print("\n✨ Building a magical world... please wait while the story is written... ✨")
        
        # --- Build the Master Prompt ---
        character_descriptions = "\n".join([f"- {c['name']}, age {c['age']}, who is {c['personality']}." for c in self.user_profile['characters']])
        
        master_prompt = f"""
        You are a world-class children's author with a magical, gentle, and therapeutic voice, in the style of Kate DiCamillo.
        Your task is to write a {self.story_length} story for the following children:
        {character_descriptions}
        
        The core theme of the story must be about the challenge of: '{self.user_profile['challenge']}'.
        The story exists in a world where there is magic involving: '{self.user_profile['magic']}'.

        INSTRUCTIONS:
        1. Write a complete, engaging, and age-appropriate story.
        2. During the story, the children must discover one or more magical items. For each item, embed it in the text using the format [KEY ITEM: The name of the item].
        3. Conclude the entire response with a single, positive "Wisdom Gem" sentence, formatted exactly as [WISDOM GEM: The lesson of the story.]
        4. Do not add any other headers, titles, or conversational text. Just the story and the special tags.
        """
        
        try:
            # Call the API
            response = self.model.generate_content(master_prompt)
            # --- Parse the Response ---
            self.parse_ai_response(response.text)
        except Exception as e:
            self.story_text = f"An error occurred while generating the story: {e}"

    def parse_ai_response(self, text):
        """Extracts Key Items and Wisdom Gem from the AI's response text."""
        # Find all Key Items using regex
        self.key_items = re.findall(r'\[KEY ITEM: (.*?)\]', text)
        
        # Find the Wisdom Gem
        gem_match = re.search(r'\[WISDOM GEM: (.*?)\]', text)
        if gem_match:
            self.wisdom_gem = gem_match.group(1)
        
        # Clean the story text by removing the tags for display
        clean_text = re.sub(r'\[KEY ITEM: .*?\]', '', text)
        self.story_text = re.sub(r'\[WISDOM GEM: .*?\]', '', clean_text).strip()

    def generate_adventure_report(self):
        """Prints the final story and the extracted report elements."""
        print("\n" + "="*50)
        print("📖 Here is your new, unique story! 📖")
        print("="*50 + "\n")
        print(self.story_text)
        
        if self.key_items:
            print("\n--- KEY ITEMS DISCOVERED ---")
            for item in self.key_items:
                print(f"* {item}")
        
        if self.wisdom_gem:
            print("\n--- WISDOM GEM ---")
            print(self.wisdom_gem)

if __name__ == "__main__":
    api_key = input("Please paste your Google AI API Key here to begin: ")
    if not api_key:
        print("An API Key is required.")
    else:
        engine = StoryEngine(api_key)
        engine.start()
        
