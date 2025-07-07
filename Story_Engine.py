# Interactive Children's Adventure Engine v9.0
# REFACTORED: Externalized static data (companions, twists) into JSON files.
# NEW: Implemented a Character class for better data structure and readability.
# NEW: Added a "Surprise Me!" quick start mode for faster story generation.

import google.generativeai as genai
import re
import getpass
from datetime import datetime
import os
import json
import random

class Character:
    """A class to represent a story character, replacing the use of dictionaries."""
    def __init__(self, name, age, personality, favorites, special_trait=None):
        self.name = name
        self.age = age
        self.personality = personality
        self.favorites = favorites
        self.special_trait = special_trait

    def to_dict(self):
        """Converts the Character object to a dictionary for JSON serialization."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """Creates a Character object from a dictionary."""
        return cls(**data)

    def get_description(self):
        """Returns a formatted description string for the AI prompt."""
        desc = f"- {self.name}, age {self.age}, who is {self.personality} and loves {self.favorites}"
        if self.special_trait:
            desc += f". Special: {self.special_trait}"
        return desc

class StoryEngine:
    def __init__(self, api_key):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_key_is_valid = True
            # Load static data from external files
            self.twist_options = self._load_json_data("twists.json")
            self.magical_companions = self._load_json_data("companions.json")
            self.saved_characters = self.load_character_profiles()
        except Exception as e:
            print(f"❌ ERROR: Could not configure the API. Please check your key. Details: {e}")
            self.api_key_is_valid = False

    def _load_json_data(self, filename):
        """Helper function to load data from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"⚠️ WARNING: Could not load or parse {filename}. Some features may be disabled.")
            return [] if filename == "twists.json" else {}

    def load_character_profiles(self):
        """Loads character profiles and converts them to Character objects."""
        if not os.path.exists("characters.json"):
            return []
        try:
            with open("characters.json", 'r', encoding='utf-8') as f:
                if os.path.getsize("characters.json") > 0:
                    char_data = json.load(f)
                    return [Character.from_dict(data) for data in char_data]
                return []
        except json.JSONDecodeError:
            return []

    def save_character_profiles(self, characters_in_story):
        """Saves new character profiles to the JSON file."""
        existing_names = {char.name for char in self.saved_characters}
        for new_char in characters_in_story:
            if new_char.name not in existing_names:
                self.saved_characters.append(new_char)
                existing_names.add(new_char.name)
        
        # Limit to 20 saved characters
        self.saved_characters = self.saved_characters[-20:]

        with open("characters.json", 'w', encoding='utf-8') as f:
            # Convert Character objects to dictionaries for saving
            json.dump([char.to_dict() for char in self.saved_characters], f, indent=4)

    def start(self):
        """Main entry point to choose story creation mode."""
        if not self.api_key_is_valid:
            return
        
        while True:
            print("\n" + "="*60)
            print("CHOOSE YOUR ADVENTURE PATH".center(60))
            print("="*60)
            print("A) ✍️ Create a Custom Story (You choose all the details)")
            print("B) 🎲 Surprise Me! (A random adventure with your characters)")
            
            choice = input("\nSelect an option (A/B): ").upper()

            if choice == 'A':
                self.run_custom_cycle()
            elif choice == 'B':
                self.run_quick_start_cycle()
            else:
                print("❌ Invalid choice. Please select A or B.")
                continue

            if input("\n\nWould you like to return to the main menu? (y/n): ").lower() != 'y':
                break
        
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")

    def _run_story_flow(self):
        """The shared logic for generating and reporting a story."""
        if self.generate_story_with_ai():
            self.analyze_story_content()
            self.generate_adventure_report()
            self.save_story_to_file()

    def run_custom_cycle(self):
        """Runs the full, detailed story creation cycle."""
        self._reset_story_attributes()
        print("\n--- ✍️ Creating a Custom Story ---")
        self.user_profile['genre'] = self._select_option("genre")
        self.user_profile['tone'] = self._select_option("tone")
        self.user_profile['length'] = self._select_option("length")
        self._intake_character_data()
        self._intake_story_details()
        self._run_story_flow()

    def run_quick_start_cycle(self):
        """Runs a randomized story creation cycle."""
        self._reset_story_attributes()
        print("\n--- 🎲 Generating a Surprise Adventure! ---")
        # Randomly select story parameters
        self.user_profile['genre'] = random.choice(list(self._get_options("genre").values()))
        self.user_profile['tone'] = random.choice(list(self._get_options("tone").values()))
        self.user_profile['length'] = random.choice(list(self._get_options("length").values()))
        self.user_profile['twist'] = random.choice(self.twist_options)
        self.user_profile['magical_companion'] = random.choice(list(self.magical_companions.values()))
        
        print(f"Your surprise adventure is a {self.user_profile['tone']} {self.user_profile['genre']} story!")
        print(f"It will feature {self.user_profile['magical_companion']['name']} and a surprise twist!")

        self._intake_character_data() # Still need to know who the hero is!
        # Assign a generic challenge
        self.user_profile['challenge'] = "overcoming an unexpected challenge together"
        self.user_profile['magic'] = "a mysterious and unpredictable new power"
        self.user_profile['hook_style'] = "action"
        
        self._run_story_flow()

    def _reset_story_attributes(self):
        """Resets all story-specific attributes."""
        self.user_profile = {}
        self.story_title = ""
        self.story_text = ""
        self.key_items = []
        self.wisdom_gem = ""
        self.story_analysis = {}

    def _get_options(self, option_type):
        """Central repository for user-facing menu options."""
        options = {
            "genre": {
                "A": "Fantasy Adventure", "B": "Space Explorer", "C": "Underwater Quest", 
                "D": "Superhero Journey", "E": "Animal Friends", "F": "Time Travel"
            },
            "tone": {
                "A": "exciting and adventurous", "B": "gentle and heartwarming", 
                "C": "funny and silly", "D": "mysterious and magical"
            },
            "length": {
                "A": "Short (~400 words)", "B": "Medium (~700 words)", "C": "Long (~1000 words)"
            }
        }
        return options.get(option_type, {})

    def _select_option(self, option_type):
        """Generic function to display options and get user selection."""
        titles = {"genre": "📚 Genre", "tone": "🎭 Tone", "length": "📏 Length"}
        print(f"\n--- {titles[option_type]} Selection ---")
        
        options = self._get_options(option_type)
        for key, value in options.items():
            print(f"{key}) {value}")
        
        choice = input(f"\nChoose an option ({'/'.join(options.keys())}): ").upper()
        return options.get(choice, list(options.values())[0])

    def _intake_character_data(self):
        """Gathers character information from the user (saved or new)."""
        characters = []
        print("\n--- 👥 Character Selection ---")
        if self.saved_characters:
            print("Your saved characters:")
            for i, char in enumerate(self.saved_characters):
                print(f"{i + 1}. {char.name} (Age: {char.age})")
            
            use_saved = input("Enter number to add, 'n' for new, or Enter to continue: ").lower()
            if use_saved.isdigit() and 0 < int(use_saved) <= len(self.saved_characters):
                characters.append(self.saved_characters[int(use_saved) - 1])
                print(f"✓ Added {characters[-1].name}!")

        while True:
            if not characters or input("Add another new character? (y/n): ").lower() == 'y':
                print("\n--- New Character ---")
                name = input("Name: ")
                while True:
                    try: age = int(input("Age: ")); break
                    except ValueError: print("Please enter a valid number.")
                
                personality = input("Personality: ")
                favorites = input("Loves: ")
                special_trait = input("Special trait or object? [Enter to skip]: ")
                
                new_char = Character(name, age, personality, favorites, special_trait or None)
                characters.append(new_char)
                print(f"✓ Added {new_char.name}!")
            else:
                break
        
        self.user_profile['characters'] = characters
        self.save_character_profiles(characters)

    def _intake_story_details(self):
        """Gathers the remaining story details from the user."""
        print("\n--- 🎯 Story Details ---")
        self.user_profile['challenge'] = input("What challenge or lesson should the story explore?: ")
        self.user_profile['magic'] = input("What kind of magic exists in this world?: ")
        self.user_profile['hook_style'] = 'action' if input("Start with action or description? (a/d): ").lower() == 'a' else 'description'
        
        if self.magical_companions and input("Add a magical companion? (y/n): ").lower() == 'y':
            companions_list = list(self.magical_companions.values())
            for i, comp in enumerate(companions_list):
                print(f"{i + 1}. {comp['emoji']} {comp['name']} - {comp['personality']}")
            try:
                choice = int(input("Choose a companion by number: ")) - 1
                if 0 <= choice < len(companions_list):
                    self.user_profile['magical_companion'] = companions_list[choice]
            except (ValueError, IndexError):
                print("Invalid choice, no companion added.")

        if self.twist_options and input("Add a surprise twist? (y/n): ").lower() == 'y':
            self.user_profile['twist'] = random.choice(self.twist_options)
            print("✓ A surprise twist will be added!")
            
    def generate_story_with_ai(self):
        """Builds the master prompt and generates the story using the AI."""
        print("\n✨ Weaving your magical story... (This may take a moment) ✨")
        
        # Build prompt components
        char_descriptions = "\n".join([c.get_description() for c in self.user_profile['characters']])
        companion_text = ""
        if 'magical_companion' in self.user_profile:
            comp = self.user_profile['magical_companion']
            companion_text = f"\nMAGICAL COMPANION:\n- {comp['name']} ({comp['personality']}), whose special ability is {comp['special_ability']}."
        
        twist_text = f"\n- Surprise twist: {self.user_profile['twist']}" if 'twist' in self.user_profile else ""

        master_prompt = f"""
        You are a world-class children's author. Write a complete, {self.user_profile['tone']} {self.user_profile['genre']} story of {self.user_profile['length']}.

        STORY ELEMENTS:
        - Characters:
        {char_descriptions}
        {companion_text}
        - Theme: Explore '{self.user_profile['challenge']}'.
        - Magic System: '{self.user_profile['magic']}'.
        - Opening Hook: Start with {'action' if self.user_profile['hook_style'] == 'action' else 'vivid description'}.
        {twist_text}

        CRITICAL INSTRUCTIONS:
        1.  Start immediately with `[TITLE: Creative Title Here]`.
        2.  Infuse the story with rich sensory details (smells, textures, sounds).
        3.  Show emotions through actions, not just by naming them.
        4.  In the climax, describe **in detail** how the characters solve the problem step-by-step. Do not summarize the solution.
        5.  Include 2-3 `[KEY ITEM: Name of Item]` tags where they are discovered.
        6.  End the entire response with `[WISDOM GEM: A single, powerful sentence lesson.]`.
        """
        
        try:
            response = self.model.generate_content(master_prompt)
            self.parse_ai_response(response.text)
            return True
        except Exception as e:
            print(f"\n❌ ERROR generating story: {e}")
            return False

    def parse_ai_response(self, ai_text):
        """Parses the AI's response to extract structured data."""
        self.story_title = (re.search(r'\[TITLE:(.*?)\]', ai_text, re.I | re.DOTALL) or [None, "Untitled"])[1].strip()
        self.key_items = [item.strip() for item in re.findall(r'\[KEY ITEM:(.*?)\]', ai_text, re.I)]
        self.wisdom_gem = (re.search(r'\[WISDOM GEM:(.*?)\]', ai_text, re.I | re.DOTALL) or [None, ""])[1].strip()
        
        story_text = re.sub(r'\[TITLE:.*?\]\s*', '', ai_text, flags=re.I | re.DOTALL)
        story_text = re.sub(r'\[KEY ITEM:(.*?)\]', r'\1', story_text, flags=re.I)
        self.story_text = re.sub(r'\[WISDOM GEM:.*?\]', '', story_text, flags=re.I | re.DOTALL).strip()

    def analyze_story_content(self):
        """Analyzes the generated story for literary and developmental metrics."""
        print("🔬 Analyzing story depth...")
        if not self.story_text: return

        analysis_prompt = f"""
        As a children's literacy expert, analyze this story: "{self.story_text}"
        Provide a concise report with these exact tags on new lines:
        [TARGET_AGE: e.g., 5-7 years old]
        [READING_LEVEL: Brief description of complexity]
        [THEMES: Core themes in one sentence]
        [ILLUSTRATION_IDEAS: - A list of 2-3 key scenes]
        """
        try:
            response = self.model.generate_content(analysis_prompt)
            text = response.text
            self.story_analysis['target_age'] = (re.search(r'\[TARGET_AGE:(.*)\]', text, re.I) or [None, "N/A"])[1].strip()
            self.story_analysis['reading_level'] = (re.search(r'\[READING_LEVEL:(.*)\]', text, re.I) or [None, "N/A"])[1].strip()
            self.story_analysis['themes'] = (re.search(r'\[THEMES:(.*)\]', text, re.I) or [None, "N/A"])[1].strip()
            ideas_text = (re.search(r'\[ILLUSTRATION_IDEAS:(.*)\]', text, re.I | re.DOTALL) or [None, ""])[1]
            self.story_analysis['illustration_ideas'] = [idea.strip('- ').strip() for idea in ideas_text.strip().split('\n') if idea.strip()]
        except Exception as e:
            print(f"-> Analysis failed: {e}")

    def generate_adventure_report(self):
        """Displays the story and analysis in a beautiful format."""
        print("\n" + "="*70 + f"\n📖 {self.story_title.upper()} 📖".center(70) + "\n" + "="*70 + "\n")
        print(self.story_text)
        
        if self.key_items:
            print("\n" + "~"*50 + "\n" + "✨ MAGICAL ITEMS DISCOVERED ✨".center(50) + "\n" + "~"*50)
            for i, item in enumerate(self.key_items, 1): print(f"{i}. {item}")

        if self.wisdom_gem:
            print("\n" + "~"*50 + "\n" + "💎 WISDOM GEM 💎".center(50) + "\n" + "~"*50 + f"\n{self.wisdom_gem}")
        
        if self.story_analysis:
            print("\n" + "="*70 + "\n" + "📊 STORY ANALYSIS 📊".center(70) + "\n" + "="*70)
            print(f"\n🎯 Target Age: {self.story_analysis.get('target_age', 'N/A')}")
            print(f"📚 Reading Level: {self.story_analysis.get('reading_level', 'N/A')}")
            print(f"🌟 Core Themes: {self.story_analysis.get('themes', 'N/A')}")
            if self.story_analysis.get('illustration_ideas'):
                print("\n🎨 Perfect Moments for Illustrations:")
                for i, idea in enumerate(self.story_analysis['illustration_ideas'], 1): print(f"  {i}. {idea}")

    def save_story_to_file(self):
        """Saves the story with enhanced metadata to a genre-specific subfolder."""
        genre_folder = self.user_profile.get('genre', 'general').lower().replace(" ", "_")
        genre_path = f"stories/{genre_folder}"
        os.makedirs(genre_path, exist_ok=True)
        
        filename_title = re.sub(r'[^\w\s-]', '', self.story_title).strip().replace(' ', '_')[:50]
        filename = f"{genre_path}/{filename_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Title: {self.story_title}\nGenre: {self.user_profile.get('genre', 'N/A')}\n\n")
                f.write(self.story_text)
                # ... Add more metadata to save as needed ...
            print(f"\n📁 Story saved to: {filename}")
        except Exception as e:
            print(f"\n❌ ERROR saving story: {e}")

def main():
    """Main entry point for the application."""
    print("="*70 + "\n" + "🌟 MAGICAL STORY CREATOR v9.0 🌟".center(70) + "\n" + "="*70)
    print("\nCreate personalized adventure stories for children!")
    print("Featuring: Character Saving, Quick Start Mode, and Literary Analysis!\n")
    print("📌 Get a free API key at: aistudio.google.com/app/apikey")
    print("="*70 + "\n")
    
    try:
        api_key = getpass.getpass("🔑 Enter your Google AI API Key (hidden): ")
        if not api_key:
            print("❌ An API Key is required.")
            return
            
        engine = StoryEngine(api_key)
        if engine.api_key_is_valid:
            engine.start()
            
    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()