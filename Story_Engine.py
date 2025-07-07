# Interactive Children's Adventure Engine v8.0
# Complete merge of v5.0 features with ChatGPT enhancements and v3.0 user experience improvements

import google.generativeai as genai
import re
import getpass
from datetime import datetime
import os
import json
import random

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

        # Story twist options
        self.twist_options = [
            "The villain turns out to be scared of something silly",
            "A magical mishap makes everyone speak in rhymes",
            "The treasure they seek was inside them all along",
            "The scary monster just wanted a friend",
            "Magic only works when you're laughing",
            "The spell goes hilariously wrong but saves the day",
            "An unexpected animal becomes the hero",
            "The solution involves an act of kindness",
            "Everything turns sparkly at a crucial moment",
            "The antagonist gets transformed into something cute",
            "A simple song defeats the darkness",
            "The magic item works backwards",
            "Friendship breaks an ancient curse",
            "The smallest character has the biggest impact",
            "Laughter becomes a literal superpower",
            "The villain accidentally helps the heroes",
            "A pet saves everyone with unexpected wisdom",
            "The magic portal leads somewhere silly first",
            "Sharing a snack solves the conflict",
            "The ancient prophecy was just a grocery list"
        ]
        
        # Magical companion characters
        self.magical_companions = {
            "Robin": {
                "name": "Robin",
                "emoji": "🐦",
                "species": "Robin bird",
                "appearance": "80s teased feather-do, leg warmers, tiny sunglasses",
                "personality": "Overprotective and anxious but incredibly loving",
                "quirk": "Carries a tiny whistle and uses binoculars too big for her body",
                "special_ability": "Eagle-eyed lookout who spots danger (and snacks) from miles away"
            },
            "Wilma": {
                "name": "Wilma",
                "emoji": "✨",
                "species": "Fairy Godmother",
                "appearance": "Curly red hair, sparkly apron with magical pockets",
                "personality": "Warm, wise, unpredictable; laughs at her own jokes",
                "quirk": "Her gifts always solve problems in unexpected ways",
                "special_ability": "Can pull surprisingly useful items from her apron pockets"
            },
            "Mike": {
                "name": "Mike",
                "emoji": "🍀",
                "species": "Leprechaun",
                "appearance": "Scruffy red beard, toolbelt of odd items, mismatched socks",
                "personality": "Witty, clever, sarcastic, prone to terrible puns",
                "quirk": "Will only help if you can out-rhyme him",
                "special_ability": "Can summon objects from his pockets after a rhyme battle"
            },
            "Bloop": {
                "name": "Bloop",
                "emoji": "🐙",
                "species": "Transparent jellyfish",
                "appearance": "See-through body with glowing magical tattoos",
                "personality": "Gentle, shy but brilliant, speaks in bubbles",
                "quirk": "Gets brighter when happy, dimmer when sad",
                "special_ability": "Can light up memories or dreams in the water"
            },
            "Cogsley": {
                "name": "Cogsley",
                "emoji": "🔧",
                "species": "Clockwork Mouse",
                "appearance": "Brass gears visible through glass panels, tiny monocle",
                "personality": "Nerdy, fast-talking, obsessed with punctuality",
                "quirk": "Always knows exactly what time it is everywhere",
                "special_ability": "Can slow down or rewind time for 30 seconds"
            },
            "Zara Moonwhistle": {
                "name": "Zara Moonwhistle",
                "emoji": "🌙",
                "species": "Night Witch",
                "appearance": "Cloak made of starlight, speaks in mysterious half-riddles",
                "personality": "Mysterious, encouraging, appears when hope is lowest",
                "quirk": "Only appears at night or in the darkest moments",
                "special_ability": "Can whisper dreams into lanterns that come true"
            }
        }

    def load_character_profiles(self):
        """Loads character profiles from a JSON file."""
        if os.path.exists("characters.json"):
            try:
                with open("characters.json", 'r', encoding='utf-8') as f:
                    if os.path.getsize("characters.json") > 0:
                        return json.load(f)
                    else:
                        return []
            except json.JSONDecodeError:
                return []
        return []

    def save_character_profiles(self, characters_in_story):
        """Saves new character profiles to the JSON file, avoiding duplicates."""
        existing_names = {char['name'] for char in self.saved_characters}
        for new_char in characters_in_story:
            if new_char['name'] not in existing_names:
                self.saved_characters.append(new_char)
                existing_names.add(new_char['name'])

        # Limit to 20 saved characters
        if len(self.saved_characters) > 20:
            self.saved_characters = self.saved_characters[-20:]

        with open("characters.json", 'w', encoding='utf-8') as f:
            json.dump(self.saved_characters, f, indent=4)

    def start(self):
        """Main entry point for the story engine."""
        if not self.api_key_is_valid:
            return

        print("\n✨ Welcome to the Magical Story Creator! ✨")
        print("I'll help you create personalized adventure stories.\n")
        
        while True:
            self.run_story_creation_cycle()
            if input("\n\nWould you like to create another story? (y/n): ").lower() != 'y':
                break
        
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")

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

        print("\n" + "="*60)
        print("📖 NEW STORY CREATION 📖".center(60))
        print("="*60 + "\n")

        self.select_genre()
        self.select_tone()
        self.select_story_length()
        self.intake_calibration()

        if self.generate_story_with_ai():
            self.analyze_story_content()
            self.generate_adventure_report()
            self.save_story_to_file()

    def select_genre(self):
        """Allows selection of story genre with examples."""
        print("📚 What type of story would you like?")
        print("A) Fantasy Adventure (dragons, wizards, enchanted forests)")
        print("B) Space Explorer (aliens, planets, spaceships)")
        print("C) Underwater Quest (mermaids, sea creatures, ocean magic)")
        print("D) Superhero Journey (powers, villains, saving the day)")
        print("E) Animal Friends (talking animals, nature magic)")
        print("F) Time Travel (dinosaurs, future worlds, history)")
        
        choice = input("\nChoose your genre (A-F): ").upper()
        genres = {
            "A": "Fantasy Adventure",
            "B": "Space Explorer",
            "C": "Underwater Quest",
            "D": "Superhero Journey",
            "E": "Animal Friends",
            "F": "Time Travel"
        }
        self.genre = genres.get(choice, "Fantasy Adventure")
        print(f"✓ Selected: {self.genre}\n")

    def select_tone(self):
        """Enhanced tone selection with humor dial."""
        print("🎭 What feeling should the story have?")
        print("A) Exciting and adventurous")
        print("B) Gentle and heartwarming")
        print("C) Funny and silly")
        print("D) Mysterious and magical")
        print("E) Emotional with gentle humor")
        
        choice = input("\nChoose the tone (A-E): ").upper()
        tones = {
            "A": "exciting and adventurous",
            "B": "gentle and heartwarming",
            "C": "funny and silly",
            "D": "mysterious and magical",
            "E": "emotional with gentle humor"
        }
        self.tone = tones.get(choice, "gentle and heartwarming")
        
        # Additional humor level for silly tone
        if choice == "C":
            humor_level = input("\nHow silly? (1=a little silly, 2=very silly, 3=absolutely bonkers): ")
            self.user_profile['humor_level'] = humor_level if humor_level in ['1', '2', '3'] else '2'
        
        print(f"✓ Selected: {self.tone}\n")

    def select_story_length(self):
        """Story length selection."""
        print("📏 How long should the story be?")
        print("A) Short - Perfect for bedtime (~400 words, 2-3 minutes)")
        print("B) Medium - A nice adventure (~700 words, 5-7 minutes)")
        print("C) Long - An epic journey (~1000 words, 8-10 minutes)")
        
        choice = input("\nChoose your story length (A/B/C): ").upper()
        lengths = {
            "A": "Short (~400 words)",
            "B": "Medium (~700 words)",
            "C": "Long (~1000 words)"
        }
        self.story_length = lengths.get(choice, "Medium (~700 words)")
        print(f"✓ Selected: {self.story_length}\n")

    def intake_calibration(self):
        """Enhanced character and story element gathering."""
        profile = {}
        characters = []

        print("👥 Let's add the heroes of our story!")
        
        # Show saved characters if any
        if self.saved_characters:
            print("\n📚 Saved Characters:")
            for i, char in enumerate(self.saved_characters):
                print(f"{i + 1}. {char['name']} (Age: {char['age']}) - {char['personality']}")
            
            while True:
                use_saved = input("\nEnter number to add, 'new' for new character, or Enter when done: ").lower()
                if use_saved.isdigit() and 0 < int(use_saved) <= len(self.saved_characters):
                    selected_char = self.saved_characters[int(use_saved) - 1].copy()
                    if not any(c['name'] == selected_char['name'] for c in characters):
                        characters.append(selected_char)
                        print(f"✓ Added {selected_char['name']} to the story!")
                    else:
                        print(f"→ {selected_char['name']} is already in the story.")
                elif use_saved in ['new', 'n', '']:
                    break

        # Add new characters
        while not characters or input("\nAdd a new character? (y/n): ").lower() == 'y':
            print("\n--- New Character ---")
            name = input("Name: ")
            
            # Age with validation
            while True:
                age_input = input("Age: ")
                try:
                    age = int(age_input)
                    if 1 <= age <= 18:
                        break
                    else:
                        print("Please enter an age between 1 and 18.")
                except ValueError:
                    print("Please enter a valid number.")

            personality = input("Personality (e.g., 'brave and curious', 'shy but clever'): ")
            favorites = input("Loves (e.g., 'dinosaurs and puzzles', 'art and butterflies'): ")
            
            char = {
                'name': name,
                'age': age,
                'personality': personality,
                'favorites': favorites
            }
            
            # Special object or trait (ChatGPT suggestion #3)
            special = input("Special object or trait? (e.g., 'lucky penny', 'afraid of dark', 'pet hamster') [Enter to skip]: ")
            if special:
                char['special_trait'] = special
            
            characters.append(char)
            print(f"✓ Added {char['name']} to the story!")

        profile['characters'] = characters
        self.save_character_profiles(characters)

        # Story elements
        print("\n🎯 Now for the story's theme and magic!")
        
        # Hook style (ChatGPT suggestion #1)
        print("\n📖 How should the story begin?")
        print("A) Jump right into the action!")
        print("B) Set the scene first")
        hook_choice = input("Choose (A/B): ").upper()
        profile['hook_style'] = 'action' if hook_choice == 'A' else 'description'
        
        # Challenge with examples
        print("\n💫 What challenge or lesson should the story explore?")
        print("Examples: 'making new friends', 'being brave when scared', 'working together'")
        profile['challenge'] = input("Your choice: ")

        # Magic system with genre-specific examples
        print(f"\n✨ What kind of magic exists in this {self.genre} world?")
        
        genre_examples = {
            "Fantasy Adventure": ["talking forest animals", "magic wands", "enchanted objects", "dragon friends"],
            "Space Explorer": ["alien telepathy", "star-powered gadgets", "planet-hopping portals", "cosmic creatures"],
            "Underwater Quest": ["mermaid songs", "glowing coral", "water-breathing bubbles", "sea creature allies"],
            "Superhero Journey": ["kindness powers", "emotion-based abilities", "helpful gadgets", "animal communication"],
            "Animal Friends": ["animals that talk", "nature magic", "forest wisdom", "magical seeds"],
            "Time Travel": ["time-freeze bubbles", "memory crystals", "dinosaur guides", "future tech"]
        }
        
        examples = genre_examples.get(self.genre, genre_examples["Fantasy Adventure"])
        print("Examples: " + ", ".join(examples))
        profile['magic'] = input("Your magical element: ")
        
        # Magical companion selection
        print("\n🌟 Would you like a magical companion in your story?")
        add_companion = input("Add a magical helper? (y/n): ").lower()
        
        if add_companion == 'y':
            print("\n✨ Choose your magical companion:")
            companions_list = list(self.magical_companions.items())
            for i, (key, comp) in enumerate(companions_list, 1):
                print(f"{i}. {comp['emoji']} {comp['name']} - {comp['species']}")
                print(f"   {comp['personality']}")
            
            print(f"{len(companions_list) + 1}. 🎲 Surprise me!")
            
            comp_choice = input("\nChoose companion (number): ")
            try:
                choice_num = int(comp_choice)
                if 1 <= choice_num <= len(companions_list):
                    chosen_key = companions_list[choice_num - 1][0]
                    profile['magical_companion'] = self.magical_companions[chosen_key]
                    print(f"✓ {profile['magical_companion']['name']} will join your adventure!")
                elif choice_num == len(companions_list) + 1:
                    random_companion = random.choice(list(self.magical_companions.values()))
                    profile['magical_companion'] = random_companion
                    print(f"✓ {random_companion['name']} has been chosen to join your adventure!")
            except:
                pass
        
        # Surprise twist option (ChatGPT suggestion #4)
        use_twist = input("\n🎲 Add a surprise twist to the story? (y/n): ").lower()
        if use_twist == 'y':
            profile['twist'] = random.choice(self.twist_options)
            print("✓ A surprise twist will be added!")
        
        self.user_profile = profile

    def generate_story_with_ai(self):
        """Enhanced story generation with all new features."""
        print("\n✨ Weaving your magical story... ✨")
        print("(This may take 20-30 seconds)")

        # Build character descriptions
        char_descriptions = []
        for c in self.user_profile['characters']:
            desc = f"- {c['name']}, age {c['age']}, who is {c['personality']} and loves {c['favorites']}"
            if 'special_trait' in c:
                desc += f". Special: {c['special_trait']}"
            char_descriptions.append(desc)
        character_text = "\n".join(char_descriptions)
        
        # Add magical companion description if selected
        companion_text = ""
        if 'magical_companion' in self.user_profile:
            comp = self.user_profile['magical_companion']
            companion_text = f"""
        
        MAGICAL COMPANION:
        - {comp['name']} the {comp['species']}
        - Appearance: {comp['appearance']}
        - Personality: {comp['personality']}
        - Special ability: {comp['special_ability']}
        - Quirk: {comp['quirk']}
        
        Make {comp['name']} an important part of the story, using their special ability at a crucial moment.
        """

        # Humor instructions based on tone
        humor_instruction = ""
        if self.tone == "funny and silly":
            level = self.user_profile.get('humor_level', '2')
            if level == '1':
                humor_instruction = "Include gentle humor and wordplay."
            elif level == '2':
                humor_instruction = "Make it quite funny with silly situations and jokes."
            else:
                humor_instruction = "Go absolutely wild with chaos, slapstick, and absurd humor!"

        # Build the master prompt
        master_prompt = f"""
        You are a world-class children's author with the warmth of Kate DiCamillo, 
        the imagination of Roald Dahl, and the heart of Maurice Sendak.
        
        Write a {self.tone} {self.genre} story ({self.story_length}) featuring:
        {character_text}
        {companion_text}

        STORY REQUIREMENTS:
        - Hook: {'Start immediately in the middle of exciting action!' if self.user_profile['hook_style'] == 'action' else 'Begin with vivid scene-setting before the action'}
        - Core theme: '{self.user_profile['challenge']}'
        - Magic system: '{self.user_profile['magic']}'
        {'- Surprise twist: ' + self.user_profile.get('twist', '') if 'twist' in self.user_profile else ''}
        {f'- Humor style: {humor_instruction}' if humor_instruction else ''}

        CRITICAL INSTRUCTIONS:
        1. Start with [TITLE: Creative Title Here]
        2. Write with rich sensory details (smells, textures, sounds, tastes, sights)
        3. Include 2-4 magical items as [KEY ITEM: Item Name]
        4. SHOW the characters solving problems step-by-step in the climax
        5. Make any special objects/traits important to the story
        6. End with [WISDOM GEM: One sentence capturing the story's heart]
        
        The climax must be detailed - show HOW they overcome the challenge, not just that they did.
        """

        try:
            response = self.model.generate_content(master_prompt)
            self.parse_ai_response(response.text)
            return True
        except Exception as e:
            print(f"\n❌ ERROR: Could not generate the story.")
            print(f"This might be due to network issues or API limits.")
            print(f"Details: {e}")
            return False

    def parse_ai_response(self, text):
        """Extracts Title, Key Items, and Wisdom Gem from the AI's response text."""
        # Extract title
        title_match = re.search(r'\[TITLE:\s*(.*?)\]', text, re.IGNORECASE | re.DOTALL)
        self.story_title = title_match.group(1).strip() if title_match else "A Magical Adventure"

        # Extract key items
        self.key_items = [item.strip() for item in re.findall(r'\[KEY ITEM:\s*(.*?)\]', text, re.IGNORECASE)]

        # Extract wisdom gem
        gem_match = re.search(r'\[WISDOM GEM:\s*(.*?)\]', text, re.IGNORECASE | re.DOTALL)
        self.wisdom_gem = gem_match.group(1).strip() if gem_match else "Every day brings new adventures."

        # Clean the story text
        clean_text = re.sub(r'\[TITLE:.*?\]\s*', '', text, flags=re.IGNORECASE | re.DOTALL)
        clean_text = re.sub(r'\[KEY ITEM:\s*(.*?)\]', r'\1', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\[WISDOM GEM:.*?\]', '', clean_text, flags=re.IGNORECASE | re.DOTALL).strip()
        self.story_text = clean_text

    def analyze_story_content(self):
        """Analyzes the story for educational value and reading level."""
        print("\n🔬 Analyzing story depth...")
        
        if not self.story_text:
            return

        analysis_prompt = f"""
        As a children's literacy expert, analyze this story:

        "{self.story_text}"

        Provide concise analysis with these exact tags:
        [TARGET_AGE: e.g., 5-7 years old]
        [READING_LEVEL: Brief description of vocabulary/complexity]
        [THEMES: Core themes in one sentence]
        [ILLUSTRATION_IDEAS: 3 key scenes perfect for illustrations]
        """

        try:
            response = self.model.generate_content(analysis_prompt)
            text = response.text
            
            # Extract analysis components
            age_match = re.search(r'\[TARGET_AGE:\s*(.*?)\]', text, re.IGNORECASE)
            self.story_analysis['target_age'] = age_match.group(1).strip() if age_match else "5-10 years"
            
            level_match = re.search(r'\[READING_LEVEL:\s*(.*?)\]', text, re.IGNORECASE)
            self.story_analysis['reading_level'] = level_match.group(1).strip() if level_match else "Age-appropriate"
            
            themes_match = re.search(r'\[THEMES:\s*(.*?)\]', text, re.IGNORECASE)
            self.story_analysis['themes'] = themes_match.group(1).strip() if themes_match else "Adventure and growth"
            
            # Extract illustration ideas
            ideas_match = re.search(r'\[ILLUSTRATION_IDEAS:\s*(.*?)(?:\[|$)', text, re.IGNORECASE | re.DOTALL)
            if ideas_match:
                ideas_text = ideas_match.group(1).strip()
                self.story_analysis['illustration_ideas'] = [
                    idea.strip().lstrip('- •·').strip() 
                    for idea in ideas_text.split('\n') 
                    if idea.strip()
                ][:3]  # Limit to 3 ideas
            else:
                self.story_analysis['illustration_ideas'] = []
                
        except Exception as e:
            print(f"→ Analysis partially completed. {e}")
            self.story_analysis = {
                'target_age': "5-10 years",
                'reading_level': "Age-appropriate",
                'themes': self.user_profile['challenge'],
                'illustration_ideas': []
            }

    def generate_adventure_report(self):
        """Displays the story and analysis in a beautiful format."""
        print("\n" + "="*70)
        print(f"📖 {self.story_title.upper()} 📖".center(70))
        print("="*70 + "\n")
        
        # Print story with proper paragraph formatting
        paragraphs = self.story_text.split('\n')
        for para in paragraphs:
            if para.strip():
                print(para.strip())
                if len(para.strip()) > 100:  # Add extra space after long paragraphs
                    print()

        # Key items
        if self.key_items:
            print("\n" + "~"*50)
            print("✨ MAGICAL ITEMS DISCOVERED ✨".center(50))
            print("~"*50)
            for i, item in enumerate(self.key_items, 1):
                print(f"{i}. {item}")

        # Wisdom gem
        if self.wisdom_gem:
            print("\n" + "~"*50)
            print("💎 WISDOM GEM 💎".center(50))
            print("~"*50)
            print(f"\n{self.wisdom_gem}")

        # Story analysis
        if self.story_analysis:
            print("\n" + "="*70)
            print("📊 STORY ANALYSIS 📊".center(70))
            print("="*70)
            print(f"\n🎯 Target Age: {self.story_analysis.get('target_age', 'N/A')}")
            print(f"📚 Reading Level: {self.story_analysis.get('reading_level', 'N/A')}")
            print(f"🌟 Core Themes: {self.story_analysis.get('themes', 'N/A')}")
            
            if self.story_analysis.get('illustration_ideas'):
                print("\n🎨 Perfect Moments for Illustrations:")
                for i, idea in enumerate(self.story_analysis['illustration_ideas'], 1):
                    print(f"   {i}. {idea}")

    def save_story_to_file(self):
        """Saves the story with enhanced metadata."""
        # Create stories directory structure
        if not os.path.exists("stories"):
            os.makedirs("stories")
        
        # Create genre subfolder
        genre_folder = self.genre.lower().replace(" ", "_")
        genre_path = f"stories/{genre_folder}"
        if not os.path.exists(genre_path):
            os.makedirs(genre_path)
        
        # Create filename
        filename_title = re.sub(r'[^\w\s-]', '', self.story_title).strip().replace(' ', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{genre_path}/{filename_title}_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("="*70 + "\n")
                f.write(f"{self.story_title}\n")
                f.write("="*70 + "\n\n")
                
                # Metadata
                f.write(f"Genre: {self.genre}\n")
                f.write(f"Tone: {self.tone}\n")
                f.write(f"Length: {self.story_length}\n")
                f.write(f"Created: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
                
                # Characters
                f.write("\nCHARACTERS:\n")
                for c in self.user_profile['characters']:
                    f.write(f"• {c['name']} (Age {c['age']}) - {c['personality']}\n")
                    if 'special_trait' in c:
                        f.write(f"  Special: {c['special_trait']}\n")
                
                # Magical companion
                if 'magical_companion' in self.user_profile:
                    comp = self.user_profile['magical_companion']
                    f.write(f"\nMAGICAL COMPANION:\n")
                    f.write(f"• {comp['emoji']} {comp['name']} the {comp['species']}\n")
                    f.write(f"  {comp['personality']}\n")
                
                f.write("\n" + "-"*70 + "\n\n")
                
                # Story
                f.write(self.story_text)
                f.write("\n\n" + "-"*70 + "\n")
                
                # Items and wisdom
                if self.key_items:
                    f.write("\nMAGICAL ITEMS:\n")
                    for item in self.key_items:
                        f.write(f"✨ {item}\n")
                
                if self.wisdom_gem:
                    f.write(f"\nWISDOM GEM:\n💎 {self.wisdom_gem}\n")
                
                # Analysis
                if self.story_analysis:
                    f.write("\n" + "-"*70 + "\n")
                    f.write("STORY ANALYSIS:\n")
                    f.write(f"Target Age: {self.story_analysis.get('target_age', 'N/A')}\n")
                    f.write(f"Reading Level: {self.story_analysis.get('reading_level', 'N/A')}\n")
                    f.write(f"Themes: {self.story_analysis.get('themes', 'N/A')}\n")
                    
                    if self.story_analysis.get('illustration_ideas'):
                        f.write("\nIllustration Ideas:\n")
                        for i, idea in enumerate(self.story_analysis['illustration_ideas'], 1):
                            f.write(f"{i}. {idea}\n")
            
            print(f"\n📁 Story saved to: {filename}")
            
        except Exception as e:
            print(f"\n❌ ERROR: Could not save the story. Details: {e}")


def main():
    """Main entry point for the application."""
    print("="*70)
    print("🌟 MAGICAL STORY CREATOR v8.0 🌟".center(70))
    print("="*70)
    print("\nCreate personalized adventure stories for children!")
    print("Featuring: Character saving, surprise twists, humor levels, and more!\n")
    print("📌 Get a free API key at: aistudio.google.com/app/apikey")
    print("="*70 + "\n")
    
    try:
        api_key = getpass.getpass("🔑 Enter your Google AI API Key (hidden): ")
        if not api_key:
            print("❌ An API Key is required to create stories.")
            return
            
        engine = StoryEngine(api_key)
        if engine.api_key_is_valid:
            engine.start()
            
    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please try again or check your API key.")


if __name__ == "__main__":
    main()
