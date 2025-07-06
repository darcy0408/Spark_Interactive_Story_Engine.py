# Interactive Children's Adventure Engine v3.1
# Added a consolidated main loop and robust input validation.

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

    def run_story_creation_cycle(self):
        """Runs one full cycle of creating a story."""
        # Reset attributes for a new story
        self.user_profile = {}
        self.story_title = ""
        # ... other attributes can be reset here if needed

        print("\n✨ Let's create a new personalized adventure! ✨\n")
        
        self.select_genre()
        self.select_tone()
        self.select_story_mode()
        self.select_story_length()
        self.intake_calibration()
        
        if self.generate_story_with_ai():
            self.generate_adventure_report()
            self.save_story_to_file()

    def select_genre(self):
        print("📚 What type of story would you like?")
        # ... (rest of the function is the same as before)
        choice = input("\nChoose your genre (A-F): ").upper()
        genres = {"A": "Fantasy Adventure", "B": "Space Explorer", "C": "Underwater Quest", "D": "Superhero Journey", "E": "Animal Friends", "F": "Time Travel"}
        self.genre = genres.get(choice, "Fantasy Adventure")
        print(f"✓ Selected: {self.genre}\n")

    def select_tone(self):
        print("🎭 What feeling should the story have?")
        # ... (rest of the function is the same as before)
        choice = input("\nChoose the tone (A-D): ").upper()
        tones = {"A": "exciting and adventurous", "B": "gentle and heartwarming", "C": "funny and silly", "D": "mysterious and magical"}
        self.tone = tones.get(choice, "gentle and heartwarming")
        print(f"✓ Selected: {self.tone}\n")

    def select_story_mode(self):
        print("📖 How should the story unfold?")
        # ... (rest of the function is the same as before)
        choice = input("\nChoose your adventure type (A/B): ").upper()
        self.story_mode = "Interactive" if choice == "B" else "Linear"
        if choice == "B":
            print("(Interactive mode coming in a future update - creating a linear story for now)")
            self.story_mode = "Linear"
        print(f"✓ Selected: {self.story_mode}\n")

    def select_story_length(self):
        print("📏 How long should the story be?")
        # ... (rest of the function is the same as before)
        choice = input("\nChoose your story length (A/B/C): ").upper()
        lengths = {"A": "Short (~400 words)", "B": "Medium (~700 words)", "C": "Long (~1000 words)"}
        self.story_length = lengths.get(choice, "Medium (~700 words)")
        print(f"✓ Selected: {self.story_length}\n")

    def intake_calibration(self):
        profile = {}
        characters = []
        
        print("👥 Let's add the heroes of our story!")
        print("(You can add multiple children, friends, or even pets)\n")
        
        while True:
            add_char = input("Add a character to the story? (y/n): ").lower()
            if add_char != 'y':
                break
                
            print("\n--- New Character ---")
            
            ### CHANGE 1: Input Validation for Age ###
            while True:
                age_input = input("Age: ")
                try:
                    # Try to convert the input to an integer
                    age = int(age_input)
                    break # Exit the loop if successful
                except ValueError:
                    # If it fails, print an error and ask again
                    print("❌ Invalid input. Please enter a number for the age.")

            char = {
                'name': input("Name: "),
                'age': age,
                'personality': input("Personality (e.g., 'brave and curious', 'shy but clever', 'funny and energetic'): "),
                'favorites': input("Loves (e.g., 'dinosaurs and puzzles', 'art and butterflies', 'robots and ice cream'): ")
            }
            
            special = input("Any special trait? (e.g., 'wears glasses') [press Enter to skip]: ")
            if special:
                char['special_trait'] = special
                
            characters.append(char)
            print(f"✓ Added {char['name']} to the story!")
            
        if not characters:
            print("Every story needs a hero! Adding a default character.")
            characters.append({'name': 'Alex', 'age': 8, 'personality': "brave and kind", 'favorites': "adventures"})
            
        profile['characters'] = characters

        print("\n🎯 Now for the story's theme and magic!")
        # ... (rest of the function is the same as before)
        print("\nWhat challenge or lesson should the story explore?")
        profile['challenge'] = input("\nYour choice: ")
        print(f"\nWhat kind of magic exists in this {self.genre} world?")
        profile['magic'] = input("\nYour magical element: ")
        
        self.user_profile = profile
    
    # The generate_story_with_ai, parse_ai_response, generate_adventure_report, 
    # and save_story_to_file methods remain the same as v3.0
    # For brevity, they are not repeated here but should be in your final file.
    # (The full code is at the bottom of the response)

# ... [The full code for the other methods is included below] ...

if __name__ == "__main__":
    print("="*60)
    print("🌟 MAGICAL STORY CREATOR v3.1 🌟".center(60))
    print("="*60)
    print("\nThis program creates personalized adventure stories for children!")
    print("(Get a free Google AI API key at: aistudio.google.com/app/apikey)\n")
    
    try:
        api_key = getpass.getpass("Paste your API Key (hidden for security): ")
        if not api_key:
            print("❌ An API Key is required to create stories.")
        else:
            engine = StoryEngine(api_key)
            
            ### CHANGE 2: Consolidated Main Loop ###
            if engine.api_key_is_valid:
                while True:
                    engine.run_story_creation_cycle()
                    another = input("\n\nWould you like to create another story? (y/n): ").lower()
                    if another != 'y':
                        break # Exit the main loop
                
                print("\n\n✨ Thanks for using the Magical Story Creator! ✨")

    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
