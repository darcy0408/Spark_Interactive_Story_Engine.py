# Interactive Children's Adventure Engine v5.0
# NEW: Added a "Show, Don't Tell" command in the prompt to ensure the climax is fully detailed.
# NEW: Added a post-story analysis feature for reading level, themes, and illustration ideas.
# RETAINED: Robust character profile saving and loading.

import google.generativeai as genai
import re
import getpass
from datetime import datetime
import os
import json

class StoryEngine:
    def __init__(self, api_key):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_key_is_valid = True
            self.saved_characters = self.load_character_profiles()
        except Exception as e:
            print(f"❌ ERROR: Could not configure the API. Please check your key. Details: {e}")
            self.api_key_is_valid = False

    def load_character_profiles(self):
        """Loads character profiles from a JSON file."""
        if os.path.exists("characters.json"):
            try:
                with open("characters.json", 'r', encoding='utf-8') as f:
                    # Handle empty file case
                    if os.path.getsize("characters.json") > 0:
                        return json.load(f)
                    else:
                        return []
            except json.JSONDecodeError:
                return [] # Return empty list if file is corrupted
        return []

    def save_character_profiles(self, characters_in_story):
        """Saves new character profiles to the JSON file, avoiding duplicates."""
        existing_names = {char['name'] for char in self.saved_characters}
        for new_char in characters_in_story:
            if new_char['name'] not in existing_names:
                self.saved_characters.append(new_char)
                existing_names.add(new_char['name'])

        with open("characters.json", 'w', encoding='utf-8') as f:
            json.dump(self.saved_characters, f, indent=4)

    def run_story_creation_cycle(self):
        """Runs one full cycle of creating a story."""
        # Reset attributes for a new story
        self.user_profile = {}
        self.genre = ""
        self.tone = ""
        self.story_length = ""
        self.story_title = ""
        self.story_text = ""
        self.key_items = []
        self.wisdom_gem = ""
        self.story_analysis = {}

        print("\n✨ Let's create a new personalized adventure! ✨\n")

        self.select_genre()
        self.select_tone()
        self.select_story_length()
        self.intake_calibration()

        if self.generate_story_with_ai():
            self.analyze_story_content()
            self.generate_adventure_report()
            self.save_story_to_file()

    def select_genre(self):
        print("📚 What type of story would you like?")
        print("A) Fantasy Adventure\nB) Space Explorer\nC) Underwater Quest\nD) Superhero Journey\nE) Animal Friends\nF) Time Travel")
        choice = input("\nChoose your genre (A-F): ").upper()
        genres = {"A": "Fantasy Adventure", "B": "Space Explorer", "C": "Underwater Quest", "D": "Superhero Journey", "E": "Animal Friends", "F": "Time Travel"}
        self.genre = genres.get(choice, "Fantasy Adventure")
        print(f"✓ Selected: {self.genre}\n")

    def select_tone(self):
        print("🎭 What feeling should the story have?")
        print("A) Exciting and adventurous\nB) Gentle and heartwarming\nC) Funny and silly\nD) Mysterious and magical")
        choice = input("\nChoose the tone (A-D): ").upper()
        tones = {"A": "exciting and adventurous", "B": "gentle and heartwarming", "C": "funny and silly", "D": "mysterious and magical"}
        self.tone = tones.get(choice, "gentle and heartwarming")
        print(f"✓ Selected: {self.tone}\n")

    def select_story_length(self):
        print("📏 How long should the story be?")
        print("A) Short (~400 words)\nB) Medium (~700 words)\nC) Long (~1000 words)")
        choice = input("\nChoose your story length (A/B/C): ").upper()
        lengths = {"A": "Short (~400 words)", "B": "Medium (~700 words)", "C": "Long (~1000 words)"}
        self.story_length = lengths.get(choice, "Medium (~700 words)")
        print(f"✓ Selected: {self.story_length}\n")

    def intake_calibration(self):
        profile = {}
        characters = []

        if self.saved_characters:
            print("👥 You have saved characters. Would you like to use one?")
            for i, char in enumerate(self.saved_characters):
                print(f"{i + 1}. {char['name']} (Age: {char['age']})")
            
            while True:
                use_saved = input("Enter number to add, 'n' for a new character, or Enter when done: ").lower()
                if use_saved.isdigit() and 0 < int(use_saved) <= len(self.saved_characters):
                    selected_char = self.saved_characters[int(use_saved) - 1]
                    if selected_char not in characters:
                        characters.append(selected_char)
                        print(f"✓ Added {selected_char['name']} to the story!")
                    else:
                        print(f"-> {selected_char['name']} is already in the story.")
                elif use_saved == 'n' or use_saved == '':
                    break

        while True:
            # Ask to add a new character if the list is empty, or explicitly ask otherwise
            if not characters or input("Add a new character to the story? (y/n): ").lower() == 'y':
                print("\n--- New Character ---")
                while True:
                    age_input = input("Age: ")
                    try: 
                        age = int(age_input)
                        break
                    except ValueError: 
                        print("❌ Invalid input. Please enter a number for the age.")

                char = {
                    'name': input("Name: "), 'age': age,
                    'personality': input("Personality (e.g., 'brave and curious'): "),
                    'favorites': input("Loves (e.g., 'dinosaurs and puzzles'): ")
                }
                special = input("Any special trait or appearance? [press Enter to skip]: ")
                if special: 
                    char['special_trait'] = special
                
                characters.append(char)
                print(f"✓ Added {char['name']} to the story!")
            else:
                break
        
        if not characters:
            print("Every story needs a hero! Adding a default character.")
            characters.append({'name': 'Alex', 'age': 8, 'personality': "brave and kind", 'favorites': "adventures"})

        profile['characters'] = characters
        self.save_character_profiles(characters)

        print("\n🎯 Now for the story's theme and magic!")
        profile['challenge'] = input("What challenge, fear, or lesson should the story explore?: ")
        profile['magic'] = input(f"What kind of magic exists in this {self.genre} world?: ")
        self.user_profile = profile

    def generate_story_with_ai(self):
        print("\n✨ Weaving your magical story... (This may take a moment) ✨")
        char_descriptions = "\n".join([f"- **Name**: {c['name']}, **Age**: {c['age']}, **Personality**: {c['personality']}, **Loves**: {c['favorites']}" + (f", **Trait**: {c['special_trait']}" if 'special_trait' in c else "") for c in self.user_profile['characters']])

        master_prompt = f"""
        **C.R.A.F.T. Meta-Prompt: The Story Weaver**

        **Context:** You are a world-class children's author. Your task is to write a complete, emotionally resonant, and sensorially rich story for a child between 5-10 years old.

        **Role:** As the Story Weaver, you must:
        - Develop a plot with a clear problem, rising action, a thrilling climax, and a satisfying resolution.
        - Infuse the narrative with rich **sensory details** (smell, texture, taste, sound, sight).
        - Focus on the character's emotional journey. **Show, don't just tell**, their feelings.
        - **CRITICAL CLIMAX INSTRUCTION:** The story's climax is the most important part. You **MUST** describe in detail *how* the characters overcome the main challenge. Show their actions, dialogue, and creative thinking step-by-step. **DO NOT** summarize the climax with a single sentence like "they worked together to outwit the dragon." Show the full, interesting process.

        **Action:** Write a complete children's story using these details:
        - **Genre:** {self.genre}
        - **Tone:** {self.tone}
        - **Length:** {self.story_length}
        - **Core Theme:** Subtly explore '{self.user_profile['challenge']}'.
        - **Magical Element:** The world is defined by '{self.user_profile['magic']}'.
        - **Characters:**
        {char_descriptions}

        **Format:** Follow these rules exactly:
        1.  Start immediately with `[TITLE: A Creative and Magical Title]`.
        2.  Write the full story, ensuring the climax is detailed.
        3.  Embed 2-3 special objects directly in the text like this: `[KEY ITEM: The Sun-warmed Courage Stone]`.
        4.  Conclude the entire response with a final, single sentence: `[WISDOM GEM: A single, powerful sentence capturing the story's lesson.]`
        """
        
        # CORRECTED: The try/except block was incorrectly indented.
        try:
            response = self.model.generate_content(master_prompt)
            self.parse_ai_response(response.text)
            return True
        except Exception as e:
            print(f"\n❌ ERROR: Could not generate the story. Details: {e}")
            return False
            
    def parse_ai_response(self, ai_text):
        """
        Parses the AI's response to extract the story title, story text, key items, and wisdom gem.
        """
        # FIXED: This logic correctly preserves Key Item names in the story text.
        title_match = re.search(r'\[TITLE:(.*?)\]', ai_text, re.IGNORECASE | re.DOTALL)
        self.story_title = title_match.group(1).strip() if title_match else "Untitled Story"
        
        self.key_items = [item.strip() for item in re.findall(r'\[KEY ITEM:(.*?)\]', ai_text, re.IGNORECASE)]
        
        wisdom_match = re.search(r'\[WISDOM GEM:(.*?)\]', ai_text, re.IGNORECASE | re.DOTALL)
        self.wisdom_gem = wisdom_match.group(1).strip() if wisdom_match else ""
        
        # Clean the text of all tags for the final story output
        story_text = re.sub(r'\[TITLE:.*?\]\s*', '', ai_text, flags=re.IGNORECASE | re.DOTALL)
        story_text = re.sub(r'\[KEY ITEM:(.*?)\]', r'\1', story_text, flags=re.IGNORECASE) # Replace item tag with just the item name
        story_text = re.sub(r'\[WISDOM GEM:.*?\]', '', story_text, flags=re.IGNORECASE | re.DOTALL).strip()
        self.story_text = story_text

    def analyze_story_content(self):
        """RESTORED: Full implementation of the story analysis feature."""
        print("🔬 Analyzing story for depth and complexity...")
        if not self.story_text:
            return

        analysis_prompt = f"""
        You are a children's literacy expert. Analyze the following story based on several factors. Provide a concise report.

        **Story to Analyze:**
        "{self.story_text}"

        **Format:** Provide your analysis using these exact tags, each on a new line:
        [TARGET_AGE: e.g., 5-7 years old]
        [READING_LEVEL: A brief description of the vocabulary and sentence structure.]
        [THEMATIC_DEPTH: A one-sentence summary of the core themes explored.]
        [ILLUSTRATION_SUGGESTIONS: List 2-3 key moments that would be perfect for illustrations, describing the scene.]
        """
        try:
            response = self.model.generate_content(analysis_prompt)
            # Use findall for robustness, then get the first element or a default
            self.story_analysis['target_age'] = (re.findall(r'\[TARGET_AGE:(.*?)\]', response.text, re.I) or ['N/A'])[0].strip()
            self.story_analysis['reading_level'] = (re.findall(r'\[READING_LEVEL:(.*?)\]', response.text, re.I) or ['N/A'])[0].strip()
            self.story_analysis['thematic_depth'] = (re.findall(r'\[THEMATIC_DEPTH:(.*?)\]', response.text, re.I) or ['N/A'])[0].strip()
            suggestions_text = (re.search(r'\[ILLUSTRATION_SUGGESTIONS:(.*)', response.text, re.I | re.DOTALL) or [None])[0]
            if suggestions_text:
                self.story_analysis['illustration_suggestions'] = [s.strip('- ').strip() for s in suggestions_text.strip().split('\n') if s.strip()]
            else:
                self.story_analysis['illustration_suggestions'] = []
                
        except Exception as e:
            print(f"-> Could not analyze the story. Details: {e}")
            self.story_analysis = {}

    def generate_adventure_report(self):
        """RESTORED: Full implementation for displaying the final report."""
        print("\n" + "="*60)
        print(f"📖 {self.story_title.upper()} 📖".center(60))
        print("="*60 + "\n")
        print(self.story_text)

        if self.key_items:
            print("\n" + "~"*40 + "\n" + "✨ MAGICAL ITEMS DISCOVERED ✨".center(40) + "\n" + "~"*40)
            for i, item in enumerate(self.key_items, 1): print(f"{i}. {item}")

        if self.wisdom_gem:
            print("\n" + "~"*40 + "\n" + "💎 WISDOM GEM 💎".center(40) + "\n" + "~"*40)
            print(f"\n{self.wisdom_gem}\n")

        if self.story_analysis:
            print("\n" + "="*60 + "\n" + "📊 STORY ANALYSIS REPORT 📊".center(60) + "\n" + "="*60)
            print(f"🎯 Target Age: {self.story_analysis.get('target_age', 'N/A')}")
            print(f"📚 Reading Level: {self.story_analysis.get('reading_level', 'N/A')}")
            print(f"🧠 Thematic Depth: {self.story_analysis.get('thematic_depth', 'N/A')}")
            if self.story_analysis.get('illustration_suggestions'):
                print("🎨 Illustration Suggestions:")
                for sug in self.story_analysis.get('illustration_suggestions', []):
                    print(f"  - {sug}")

    def save_story_to_file(self):
        """RESTORED: Full implementation for saving the story and its analysis to a file."""
        if not os.path.exists("stories"): os.makedirs("stories")
        filename_title = re.sub(r'[^\w\s-]', '', self.story_title).strip().replace(' ', '_')
        filename = f"stories/{filename_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Title: {self.story_title}\n\n{self.story_text}\n\n")
                if self.key_items:
                    f.write("--- KEY ITEMS ---\n" + "\n".join([f"* {item}" for item in self.key_items]) + "\n\n")
                if self.wisdom_gem:
                    f.write(f"--- WISDOM GEM ---\n{self.wisdom_gem}\n\n")
                if self.story_analysis:
                    f.write("--- STORY ANALYSIS ---\n")
                    f.write(f"Target Age: {self.story_analysis.get('target_age', 'N/A')}\n")
                    f.write(f"Reading Level: {self.story_analysis.get('reading_level', 'N/A')}\n")
                    f.write(f"Thematic Depth: {self.story_analysis.get('thematic_depth', 'N/A')}\n")
                    if self.story_analysis.get('illustration_suggestions'):
                        f.write("Illustration Suggestions:\n" + "\n".join([f"  - {sug}" for sug in self.story_analysis.get('illustration_suggestions', [])]))
            print("\n" + "-"*50 + f"\n✅ Story successfully saved to: {filename}\n" + "-"*50)
        except Exception as e:
            print(f"\n❌ ERROR: Could not save the story. Details: {e}")


if __name__ == "__main__":
    print("="*60 + "\n" + "🌟 MAGICAL STORY CREATOR v5.0 🌟".center(60) + "\n" + "="*60)
    print("\nThis program creates personalized adventure stories for children!")
    print("(Get a free Google AI API key at: aistudio.google.com/app/apikey)\n")
    try:
        api_key = getpass.getpass("Paste your API Key (hidden for security): ")
        if not api_key:
            print("❌ An API Key is required to create stories.")
        else:
            engine = StoryEngine(api_key)
            if engine.api_key_is_valid:
                while True:
                    engine.run_story_creation_cycle()
                    if input("\n\nWould you like to create another story? (y/n): ").lower() != 'y': break
                print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
