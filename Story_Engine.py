# Interactive Children's Adventure Engine v3.0
# Enhanced with better examples, guided prompts, and richer story options

import google.generativeai as genai
import re
import getpass
from datetime import datetime
import os

class StoryEngine:
    def __init__(self, api_key):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_key_is_valid = True
        except Exception as e:
            print(f"❌ ERROR: Could not configure the API. Please check your key. Details: {e}")
            self.api_key_is_valid = False

        # Story attributes
        self.user_profile = {}
        self.story_mode = ""
        self.story_length = ""
        self.story_title = ""
        self.story_text = ""
        self.key_items = []
        self.wisdom_gem = ""
        self.story_map = []
        
        # Enhanced options
        self.genre = ""
        self.tone = ""

    def start(self):
        """Begins the story creation process."""
        if not self.api_key_is_valid:
            return

        print("\n✨ Welcome to the Magical Story Creator! ✨")
        print("I'll help you create a personalized adventure story.\n")
        
        self.select_genre()
        self.select_tone()
        self.select_story_mode()
        self.select_story_length()
        self.intake_calibration()
        
        if self.generate_story_with_ai():
            self.generate_adventure_report()
            self.save_story_to_file()
            self.offer_another_story()

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
        """Allows selection of story tone."""
        print("🎭 What feeling should the story have?")
        print("A) Exciting and adventurous")
        print("B) Gentle and heartwarming")
        print("C) Funny and silly")
        print("D) Mysterious and magical")
        
        choice = input("\nChoose the tone (A-D): ").upper()
        tones = {
            "A": "exciting and adventurous",
            "B": "gentle and heartwarming",
            "C": "funny and silly",
            "D": "mysterious and magical"
        }
        self.tone = tones.get(choice, "gentle and heartwarming")
        print(f"✓ Selected: {self.tone}\n")

    def select_story_mode(self):
        print("📖 How should the story unfold?")
        print("A) Linear - A complete story from beginning to end")
        print("B) Interactive - A story with choices (coming soon!)")
        
        choice = input("\nChoose your adventure type (A/B): ").upper()
        self.story_mode = "Interactive" if choice == "B" else "Linear"
        if choice == "B":
            print("(Interactive mode coming in a future update - creating a linear story for now)")
            self.story_mode = "Linear"
        print(f"✓ Selected: {self.story_mode}\n")

    def select_story_length(self):
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
        """Gathers all details about the child and story elements with helpful examples."""
        profile = {}
        characters = []
        
        print("👥 Let's add the heroes of our story!")
        print("(You can add multiple children, friends, or even pets)\n")
        
        while True:
            add_char = input("Add a character to the story? (y/n): ").lower()
            if add_char != 'y':
                break
                
            print("\n--- New Character ---")
            char = {
                'name': input("Name: "),
                'age': input("Age: "),
                'personality': input("Personality (e.g., 'brave and curious', 'shy but clever', 'funny and energetic'): "),
                'favorites': input("Loves (e.g., 'dinosaurs and puzzles', 'art and butterflies', 'robots and ice cream'): ")
            }
            
            # Optional special trait
            special = input("Any special trait? (e.g., 'wears glasses', 'has a pet hamster', 'loves to sing') [press Enter to skip]: ")
            if special:
                char['special_trait'] = special
                
            characters.append(char)
            print(f"✓ Added {char['name']} to the story!")
            
        if not characters:
            print("Every story needs a hero! Let's add at least one character.")
            char = {
                'name': input("Hero's name: "),
                'age': input("Age: "),
                'personality': "brave and kind",
                'favorites': "adventures"
            }
            characters.append(char)
            
        profile['characters'] = characters

        print("\n🎯 Now for the story's theme and magic!")
        
        # Challenge with examples
        print("\nWhat challenge or lesson should the story explore?")
        print("Examples:")
        print("  • 'making new friends'")
        print("  • 'being brave when scared'")
        print("  • 'sharing with others'")
        print("  • 'believing in yourself'")
        print("  • 'working together as a team'")
        profile['challenge'] = input("\nYour choice: ")

        # Magic system with examples based on genre
        print(f"\nWhat kind of magic exists in this {self.genre} world?")
        
        genre_examples = {
            "Fantasy Adventure": [
                "a magic wand that grants wishes",
                "talking forest animals who give advice",
                "enchanted books that come to life",
                "magical crystals with different powers"
            ],
            "Space Explorer": [
                "alien friends with telepathy",
                "a spaceship that travels through time",
                "planets made of candy",
                "star dust that grants powers"
            ],
            "Underwater Quest": [
                "the ability to breathe underwater",
                "sea shells that play memories",
                "dolphins that can teleport",
                "coral that glows and shows the way"
            ],
            "Superhero Journey": [
                "the power to fly using happy thoughts",
                "super strength from kindness",
                "invisibility when helping others",
                "talking to animals"
            ],
            "Animal Friends": [
                "animals that can speak human language",
                "magical acorns that grow instant trees",
                "butterfly wings that paint rainbows",
                "forest paths that change based on your heart"
            ],
            "Time Travel": [
                "a magical clock that opens time portals",
                "dinosaurs that remember the future",
                "time-freeze bubbles",
                "ancient artifacts with time powers"
            ]
        }
        
        examples = genre_examples.get(self.genre, genre_examples["Fantasy Adventure"])
        print("Examples:")
        for ex in examples:
            print(f"  • {ex}")
            
        profile['magic'] = input("\nYour magical element: ")
        
        # Optional elements
        print("\n🌟 Optional extras (press Enter to skip any):")
        profile['setting'] = input("Specific setting (e.g., 'Crystal Cave', 'Rainbow Galaxy'): ") or ""
        profile['companion'] = input("Magical companion (e.g., 'wise owl', 'friendly dragon'): ") or ""
        
        self.user_profile = profile

    def generate_story_with_ai(self):
        """Builds a detailed prompt and calls the Gemini API with robust error handling."""
        print("\n✨ Weaving your magical story... ✨")
        print("(This may take 20-30 seconds)")

        # Build character descriptions
        char_descriptions = []
        for c in self.user_profile['characters']:
            desc = f"- {c['name']}, age {c['age']}, who is {c['personality']} and loves {c['favorites']}"
            if 'special_trait' in c:
                desc += f" ({c['special_trait']})"
            char_descriptions.append(desc)
        character_text = "\n".join(char_descriptions)

        # Build the master prompt
        master_prompt = f"""
        You are a world-class children's author combining the warmth of Kate DiCamillo, 
        the imagination of Roald Dahl, and the heart of Maurice Sendak.
        
        Write a {self.tone} {self.genre} story ({self.story_length}) featuring:
        {character_text}

        Core theme: '{self.user_profile['challenge']}'
        Magic system: '{self.user_profile['magic']}'
        {"Setting: " + self.user_profile['setting'] if self.user_profile.get('setting') else ""}
        {"Companion: " + self.user_profile.get('companion') if self.user_profile.get('companion') else ""}

        STRICT REQUIREMENTS:
        1. Start with [TITLE: Creative Title Here]
        2. Write an engaging, age-appropriate story that naturally incorporates all characters
        3. Include 2-4 magical items discovered during the adventure as [KEY ITEM: Item Name]
        4. Make the theme emerge naturally through the adventure, not preachily
        5. End with [WISDOM GEM: A single sentence capturing the story's heart]
        6. Use vivid, sensory language appropriate for children
        7. Include dialogue and character interactions
        8. Create a satisfying beginning, middle, and end
        
        Remember: Show the lesson through adventure, don't just tell it.
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
        title_match = re.search(r'\[TITLE: (.*?)\]', text)
        self.story_title = title_match.group(1).strip() if title_match else "A Magical Adventure"

        # Extract key items
        self.key_items = re.findall(r'\[KEY ITEM: (.*?)\]', text)

        # Extract wisdom gem
        gem_match = re.search(r'\[WISDOM GEM: (.*?)\]', text)
        self.wisdom_gem = gem_match.group(1).strip() if gem_match else "Every day brings new adventures and chances to grow."

        # Clean the story text
        clean_text = re.sub(r'\[TITLE: .*?\]|\[KEY ITEM: .*?\]|\[WISDOM GEM: .*?\]', '', text).strip()
        self.story_text = clean_text

    def generate_adventure_report(self):
        """Prints the final story with beautiful formatting."""
        print("\n" + "="*60)
        print(f"📖 {self.story_title.upper()} 📖".center(60))
        print("="*60 + "\n")
        
        # Print story with proper paragraph breaks
        paragraphs = self.story_text.split('\n')
        for para in paragraphs:
            if para.strip():
                print(para.strip())
                print()

        if self.key_items:
            print("\n" + "~"*40)
            print("✨ MAGICAL ITEMS DISCOVERED ✨".center(40))
            print("~"*40)
            for i, item in enumerate(self.key_items, 1):
                print(f"{i}. {item}")

        if self.wisdom_gem:
            print("\n" + "~"*40)
            print("💎 WISDOM GEM 💎".center(40))
            print("~"*40)
            print(f"\n{self.wisdom_gem}\n")

    def save_story_to_file(self):
        """Save the story to a text file in a stories directory."""
        # Create stories directory if it doesn't exist
        if not os.path.exists("stories"):
            os.makedirs("stories")
        
        # Create filename
        filename_title = re.sub(r'[^\w\s-]', '', self.story_title).strip().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stories/{filename_title}_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("="*60 + "\n")
                f.write(f"{self.story_title}\n")
                f.write("="*60 + "\n\n")
                
                # Story info
                f.write(f"Genre: {self.genre}\n")
                f.write(f"Length: {self.story_length}\n")
                f.write(f"Created: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
                
                # Characters
                f.write("STARRING:\n")
                for c in self.user_profile['characters']:
                    f.write(f"• {c['name']} - {c['personality']}\n")
                f.write("\n" + "-"*60 + "\n\n")
                
                # Story
                f.write(self.story_text + "\n\n")
                
                # Items and gem
                if self.key_items:
                    f.write("-"*60 + "\n")
                    f.write("MAGICAL ITEMS DISCOVERED:\n")
                    for item in self.key_items:
                        f.write(f"✨ {item}\n")
                    f.write("\n")
                
                if self.wisdom_gem:
                    f.write("-"*60 + "\n")
                    f.write("WISDOM GEM:\n")
                    f.write(f"💎 {self.wisdom_gem}\n")
            
            print(f"\n📁 Story saved to: {filename}")
            
        except Exception as e:
            print(f"\n❌ ERROR: Could not save the story. Details: {e}")

    def offer_another_story(self):
        """Asks if the user wants to create another story."""
        another = input("\n\nWould you like to create another story? (y/n): ").lower()
        if another == 'y':
            print("\n" + "="*60 + "\n")
            self.start()


if __name__ == "__main__":
    print("="*60)
    print("🌟 MAGICAL STORY CREATOR 🌟".center(60))
    print("="*60)
    print("\nThis program creates personalized adventure stories for children!")
    print("You'll need a Google AI API key to begin.")
    print("(Get one free at: https://makersuite.google.com/app/apikey)\n")
    
    try:
        api_key = getpass.getpass("Paste your API Key (hidden for security): ")
        if not api_key:
            print("❌ An API Key is required to create stories.")
        else:
            engine = StoryEngine(api_key)
            engine.start()
    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
