#!/usr/bin/env python3
"""
Interactive Children's Adventure Engine v10.0
Enhanced with modern Python features and best practices.
"""

import google.generativeai as genai
import re
import getpass
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Union, Any
from enum import Enum
import json
import random
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StoryGenre(Enum):
    """Story genre options with clear mappings."""
    FANTASY = "Fantasy Adventure"
    SPACE = "Space Explorer"
    UNDERWATER = "Underwater Quest"
    SUPERHERO = "Superhero Journey"
    ANIMALS = "Animal Friends"
    TIME_TRAVEL = "Time Travel"


class StoryTone(Enum):
    """Story tone options."""
    EXCITING = "exciting and adventurous"
    GENTLE = "gentle and heartwarming"
    FUNNY = "funny and silly"
    MYSTERIOUS = "mysterious and magical"


class StoryLength(Enum):
    """Story length options with word counts."""
    SHORT = "Short (~400 words)"
    MEDIUM = "Medium (~700 words)"
    LONG = "Long (~1000 words)"


@dataclass
class Character:
    """A character in the story with all necessary attributes."""
    name: str
    age: int
    personality: str
    favorites: str
    special_trait: Optional[str] = None
    
    def __post_init__(self):
        """Validate character data after initialization."""
        if not self.name.strip():
            raise ValueError("Character name cannot be empty")
        if self.age < 1 or self.age > 18:
            raise ValueError("Character age must be between 1 and 18")
    
    def get_description(self) -> str:
        """Returns a formatted description string for AI prompts."""
        desc = f"- {self.name}, age {self.age}, who is {self.personality} and loves {self.favorites}"
        if self.special_trait:
            desc += f". Special: {self.special_trait}"
        return desc


@dataclass
class MagicalCompanion:
    """A magical companion with specific attributes."""
    name: str
    emoji: str
    species: str
    appearance: str
    personality: str
    quirk: str
    special_ability: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MagicalCompanion':
        """Create MagicalCompanion from dictionary data."""
        return cls(**data)


@dataclass
class StoryProfile:
    """Complete story configuration."""
    characters: List[Character] = field(default_factory=list)
    genre: Optional[StoryGenre] = None
    tone: Optional[StoryTone] = None
    length: Optional[StoryLength] = None
    challenge: str = ""
    magic: str = ""
    hook_style: str = "action"
    magical_companion: Optional[MagicalCompanion] = None
    twist: str = ""


@dataclass
class StoryOutput:
    """Complete story output with metadata."""
    title: str = ""
    text: str = ""
    key_items: List[str] = field(default_factory=list)
    wisdom_gem: str = ""
    analysis: Dict[str, str] = field(default_factory=dict)


class FileManager:
    """Handles all file operations with proper error handling."""
    
    def __init__(self, base_path: Union[str, Path] = "."):
        self.base_path = Path(base_path)
        self.stories_path = self.base_path / "stories"
        self.characters_file = self.base_path / "characters.json"
        self.companions_file = self.base_path / "companions.json"
        self.twists_file = self.base_path / "twists.json"
        
        # Ensure directories exist
        self.stories_path.mkdir(exist_ok=True)
    
    def load_json_data(self, filepath: Path, default_value: Any = None) -> Any:
        """Load JSON data with comprehensive error handling."""
        try:
            if not filepath.exists():
                logger.warning(f"File {filepath} not found, using default value")
                return default_value or {}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Successfully loaded {filepath}")
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {e}")
            return default_value or {}
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return default_value or {}
    
    def save_json_data(self, filepath: Path, data: Any) -> bool:
        """Save JSON data with error handling."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully saved {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
            return False
    
    def load_characters(self) -> List[Character]:
        """Load character profiles from JSON."""
        data = self.load_json_data(self.characters_file, [])
        try:
            return [Character(**char_data) for char_data in data]
        except Exception as e:
            logger.error(f"Error creating Character objects: {e}")
            return []
    
    def save_characters(self, characters: List[Character]) -> bool:
        """Save character profiles to JSON."""
        # Convert to dictionaries and limit to 20 most recent
        char_data = [asdict(char) for char in characters[-20:]]
        return self.save_json_data(self.characters_file, char_data)
    
    def save_story(self, story: StoryOutput, profile: StoryProfile) -> Optional[Path]:
        """Save story to genre-specific subfolder."""
        genre_name = profile.genre.value.lower().replace(" ", "_") if profile.genre else "general"
        genre_path = self.stories_path / genre_name
        genre_path.mkdir(exist_ok=True)
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', story.title).strip().replace(' ', '_')[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = genre_path / f"{safe_title}_{timestamp}.txt"
        
        try:
            story_content = self._format_story_content(story, profile)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(story_content)
            logger.info(f"Story saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving story: {e}")
            return None
    
    def _format_story_content(self, story: StoryOutput, profile: StoryProfile) -> str:
        """Format story content for file output."""
        content_parts = [
            f"Title: {story.title}",
            f"Genre: {profile.genre.value if profile.genre else 'N/A'}",
            f"Tone: {profile.tone.value if profile.tone else 'N/A'}",
            f"Length: {profile.length.value if profile.length else 'N/A'}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n" + "="*50 + " STORY " + "="*50 + "\n",
            story.text,
        ]
        
        if story.key_items:
            content_parts.extend([
                "\n" + "="*40 + " KEY ITEMS " + "="*40,
                "\n".join(f"• {item}" for item in story.key_items)
            ])
        
        if story.wisdom_gem:
            content_parts.extend([
                "\n" + "="*40 + " WISDOM GEM " + "="*40,
                story.wisdom_gem
            ])
            
        return "\n".join(content_parts)


class UserInterface:
    """Handles all user interaction with improved UX."""
    
    @staticmethod
    def display_header():
        """Display the application header."""
        print("=" * 70)
        print("🌟 MAGICAL STORY CREATOR v10.0 🌟".center(70))
        print("=" * 70)
        print("\nCreate personalized therapeutic adventures for children!")
        print("Enhanced with: Type Safety, Better Error Handling, and Modern Python!")
        print("\n📌 Get a free API key at: aistudio.google.com/app/apikey")
        print("=" * 70 + "\n")
    
    @staticmethod
    def get_enum_choice(enum_class: type, prompt: str) -> Any:
        """Generic function to get user choice for any enum."""
        print(f"\n--- {prompt} ---")
        
        choices = list(enum_class)
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice.value}")
        
        while True:
            try:
                selection = int(input(f"\nChoose (1-{len(choices)}): "))
                if 1 <= selection <= len(choices):
                    return choices[selection - 1]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def get_character_input() -> Character:
        """Get character information with validation."""
        print("\n--- New Character ---")
        
        while True:
            name = input("Name: ").strip()
            if name:
                break
            print("Name cannot be empty. Please try again.")
        
        while True:
            try:
                age = int(input("Age (1-18): "))
                if 1 <= age <= 18:
                    break
                print("Age must be between 1 and 18")
            except ValueError:
                print("Please enter a valid number")
        
        personality = input("Personality: ").strip() or "friendly"
        favorites = input("Loves: ").strip() or "adventures"
        special_trait = input("Special trait or object [Enter to skip]: ").strip() or None
        
        return Character(name, age, personality, favorites, special_trait)
    
    @staticmethod
    def get_yes_no(prompt: str) -> bool:
        """Get yes/no input with validation."""
        while True:
            response = input(f"{prompt} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")
    
    @staticmethod
    def display_story_output(story: StoryOutput):
        """Display the complete story output beautifully."""
        print("\n" + "=" * 70)
        print(f"📖 {story.title.upper()} 📖".center(70))
        print("=" * 70 + "\n")
        print(story.text)
        
        if story.key_items:
            print("\n" + "~" * 50)
            print("✨ MAGICAL ITEMS DISCOVERED ✨".center(50))
            print("~" * 50)
            for i, item in enumerate(story.key_items, 1):
                print(f"{i}. {item}")
        
        if story.wisdom_gem:
            print("\n" + "~" * 50)
            print("💎 WISDOM GEM 💎".center(50))
            print("~" * 50)
            print(f"\n{story.wisdom_gem}")
        
        if story.analysis:
            print("\n" + "=" * 70)
            print("📊 STORY ANALYSIS 📊".center(70))
            print("=" * 70)
            print(f"\n🎯 Target Age: {story.analysis.get('target_age', 'N/A')}")
            print(f"📚 Reading Level: {story.analysis.get('reading_level', 'N/A')}")
            print(f"🌟 Core Themes: {story.analysis.get('themes', 'N/A')}")
            
            if 'illustration_ideas' in story.analysis:
                print("\n🎨 Perfect Moments for Illustrations:")
                ideas = story.analysis['illustration_ideas']
                if isinstance(ideas, list):
                    for i, idea in enumerate(ideas, 1):
                        print(f"  {i}. {idea}")


class StoryEngine:
    """Enhanced story engine with better architecture and error handling."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self.file_manager = FileManager()
        self.ui = UserInterface()
        
        # Initialize AI model
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("AI model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            raise
        
        # Load static data
        self.load_static_data()
        
        # Load saved characters
        self.saved_characters = self.file_manager.load_characters()
        logger.info(f"Loaded {len(self.saved_characters)} saved characters")
    
    def load_static_data(self):
        """Load companions and twists from JSON files."""
        # Load companions
        companions_data = self.file_manager.load_json_data(
            self.file_manager.companions_file, {}
        )
        self.magical_companions = [
            MagicalCompanion.from_dict(comp_data) 
            for comp_data in companions_data.values()
        ]
        
        # Load twists
        self.twist_options = self.file_manager.load_json_data(
            self.file_manager.twists_file, []
        )
        
        logger.info(f"Loaded {len(self.magical_companions)} companions and {len(self.twist_options)} twists")
    
    @contextmanager
    def error_handling(self, operation: str):
        """Context manager for consistent error handling."""
        try:
            yield
        except KeyboardInterrupt:
            print(f"\n\n✨ Operation '{operation}' cancelled. Thanks for using Magical Story Creator! ✨")
            raise
        except Exception as e:
            logger.error(f"Error during {operation}: {e}")
            print(f"\n❌ Error during {operation}: {e}")
            raise
    
    def run(self):
        """Main application loop."""
        self.ui.display_header()
        
        with self.error_handling("application startup"):
            while True:
                print("\n" + "=" * 60)
                print("CHOOSE YOUR ADVENTURE PATH".center(60))
                print("=" * 60)
                print("1. ✍️ Create a Custom Story (Choose all details)")
                print("2. 🎲 Surprise Me! (Random adventure)")
                print("3. 🗂️ View Saved Characters")
                print("4. ❌ Exit")
                
                choice = input("\nSelect option (1-4): ").strip()
                
                if choice == '1':
                    self.create_custom_story()
                elif choice == '2':
                    self.create_surprise_story()
                elif choice == '3':
                    self.view_saved_characters()
                elif choice == '4':
                    break
                else:
                    print("❌ Invalid choice. Please select 1-4.")
                
                if not self.ui.get_yes_no("\nReturn to main menu?"):
                    break
        
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    
    def create_custom_story(self):
        """Create a custom story with user choices."""
        with self.error_handling("custom story creation"):
            profile = StoryProfile()
            
            print("\n--- ✍️ Creating a Custom Story ---")
            
            # Get story parameters
            profile.genre = self.ui.get_enum_choice(StoryGenre, "📚 Genre Selection")
            profile.tone = self.ui.get_enum_choice(StoryTone, "🎭 Tone Selection")
            profile.length = self.ui.get_enum_choice(StoryLength, "📏 Length Selection")
            
            # Get characters
            profile.characters = self.get_story_characters()
            
            # Get story details
            self.get_story_details(profile)
            
            # Generate and display story
            story = self.generate_story(profile)
            if story:
                self.ui.display_story_output(story)
                self.save_story_and_characters(story, profile)
    
    def create_surprise_story(self):
        """Create a random surprise story."""
        with self.error_handling("surprise story creation"):
            profile = StoryProfile()
            
            print("\n--- 🎲 Generating a Surprise Adventure! ---")
            
            # Random selections
            profile.genre = random.choice(list(StoryGenre))
            profile.tone = random.choice(list(StoryTone))
            profile.length = random.choice(list(StoryLength))
            
            if self.magical_companions:
                profile.magical_companion = random.choice(self.magical_companions)
            
            if self.twist_options:
                profile.twist = random.choice(self.twist_options)
            
            # Default story elements
            profile.challenge = "overcoming an unexpected challenge together"
            profile.magic = "mysterious and unpredictable powers"
            profile.hook_style = random.choice(["action", "description"])
            
            print(f"\n✨ Your surprise: A {profile.tone.value} {profile.genre.value} story!")
            if profile.magical_companion:
                print(f"🧚 Featuring: {profile.magical_companion.name}")
            
            # Still need characters
            profile.characters = self.get_story_characters()
            
            # Generate and display story
            story = self.generate_story(profile)
            if story:
                self.ui.display_story_output(story)
                self.save_story_and_characters(story, profile)
    
    def get_story_characters(self) -> List[Character]:
        """Get characters for the story (saved or new)."""
        characters = []
        
        print("\n--- 👥 Character Selection ---")
        
        # Show saved characters
        if self.saved_characters:
            print("\nSaved characters:")
            for i, char in enumerate(self.saved_characters, 1):
                print(f"{i}. {char.name} (Age: {char.age})")
            
            while True:
                choice = input("\nEnter number to add character, 'n' for new, or Enter to continue: ").strip()
                
                if not choice:
                    break
                elif choice.lower() == 'n':
                    characters.append(self.ui.get_character_input())
                    print(f"✓ Added {characters[-1].name}!")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.saved_characters):
                        characters.append(self.saved_characters[idx])
                        print(f"✓ Added {characters[-1].name}!")
                    else:
                        print("Invalid number")
                else:
                    print("Invalid input")
        else:
            characters.append(self.ui.get_character_input())
            print(f"✓ Added {characters[-1].name}!")
        
        # Option to add more characters
        while self.ui.get_yes_no("Add another character?"):
            characters.append(self.ui.get_character_input())
            print(f"✓ Added {characters[-1].name}!")
        
        if not characters:
            print("⚠️ No characters selected. Adding a default character.")
            characters.append(Character("Hero", 8, "brave", "adventures"))
        
        return characters
    
    def get_story_details(self, profile: StoryProfile):
        """Get additional story details from user."""
        print("\n--- 🎯 Story Details ---")
        
        profile.challenge = input("What challenge should the story explore?: ").strip() or "learning to be brave"
        profile.magic = input("What kind of magic exists?: ").strip() or "friendship magic"
        profile.hook_style = "action" if self.ui.get_yes_no("Start with action scene?") else "description"
        
        # Optional magical companion
        if self.magical_companions and self.ui.get_yes_no("Add a magical companion?"):
            print("\nAvailable companions:")
            for i, comp in enumerate(self.magical_companions, 1):
                print(f"{i}. {comp.emoji} {comp.name} - {comp.personality}")
            
            try:
                choice = int(input("Choose companion (number): ")) - 1
                if 0 <= choice < len(self.magical_companions):
                    profile.magical_companion = self.magical_companions[choice]
                    print(f"✓ Added {profile.magical_companion.name}!")
            except (ValueError, IndexError):
                print("Invalid choice, no companion added.")
        
        # Optional twist
        if self.twist_options and self.ui.get_yes_no("Add a surprise twist?"):
            profile.twist = random.choice(self.twist_options)
            print("✓ Surprise twist will be added!")
    
    def generate_story(self, profile: StoryProfile) -> Optional[StoryOutput]:
        """Generate story using AI with comprehensive error handling."""
        print("\n✨ Weaving your magical story... ✨")
        
        try:
            # Build prompt
            prompt = self.build_story_prompt(profile)
            
            # Generate story
            response = self.model.generate_content(prompt)
            
            # Parse response
            story = self.parse_ai_response(response.text)
            
            # Generate analysis
            self.analyze_story(story)
            
            return story
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            print(f"❌ Story generation failed: {e}")
            return None
    
    def build_story_prompt(self, profile: StoryProfile) -> str:
        """Build comprehensive story prompt."""
        char_descriptions = "\n".join([char.get_description() for char in profile.characters])
        
        companion_text = ""
        if profile.magical_companion:
            comp = profile.magical_companion
            companion_text = f"\nMAGICAL COMPANION:\n- {comp.name} ({comp.personality}), special ability: {comp.special_ability}."
        
        twist_text = f"\n- Surprise twist: {profile.twist}" if profile.twist else ""
        
        prompt = f"""
        You are a world-class children's author. Write a complete, {profile.tone.value} {profile.genre.value} story of {profile.length.value}.

        STORY ELEMENTS:
        - Characters:
        {char_descriptions}
        {companion_text}
        - Theme: Explore '{profile.challenge}'.
        - Magic System: '{profile.magic}'.
        - Opening Hook: Start with {'action' if profile.hook_style == 'action' else 'vivid description'}.
        {twist_text}

        CRITICAL INSTRUCTIONS:
        1. Start with [TITLE: Creative Title Here].
        2. Include rich sensory details and show emotions through actions.
        3. Describe problem-solving step-by-step in the climax.
        4. Include 2-3 [KEY ITEM: Item Name] tags.
        5. End with [WISDOM GEM: One powerful lesson sentence.].
        """
        
        return prompt
    
    def parse_ai_response(self, ai_text: str) -> StoryOutput:
        """Parse AI response into structured story output."""
        story = StoryOutput()
        
        # Extract title
        title_match = re.search(r'\[TITLE:(.*?)\]', ai_text, re.I | re.DOTALL)
        story.title = title_match.group(1).strip() if title_match else "Untitled Adventure"
        
        # Extract key items
        story.key_items = [
            item.strip() for item in re.findall(r'\[KEY ITEM:(.*?)\]', ai_text, re.I)
        ]
        
        # Extract wisdom gem
        wisdom_match = re.search(r'\[WISDOM GEM:(.*?)\]', ai_text, re.I | re.DOTALL)
        story.wisdom_gem = wisdom_match.group(1).strip() if wisdom_match else ""
        
        # Clean story text
        story_text = re.sub(r'\[TITLE:.*?\]\s*', '', ai_text, flags=re.I | re.DOTALL)
        story_text = re.sub(r'\[KEY ITEM:(.*?)\]', r'\1', story_text, flags=re.I)
        story.text = re.sub(r'\[WISDOM GEM:.*?\]', '', story_text, flags=re.I | re.DOTALL).strip()
        
        return story
    
    def analyze_story(self, story: StoryOutput):
        """Analyze story for educational and literary metrics."""
        if not story.text:
            return
        
        analysis_prompt = f"""
        Analyze this children's story: "{story.text[:500]}..."
        
        Provide analysis with these exact tags:
        [TARGET_AGE: age range]
        [READING_LEVEL: complexity description]
        [THEMES: core themes sentence]
        [ILLUSTRATION_IDEAS: 
        - Scene 1 description
        - Scene 2 description
        - Scene 3 description]
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            text = response.text
            
            # Parse analysis
            story.analysis = {
                'target_age': self._extract_tag(text, 'TARGET_AGE'),
                'reading_level': self._extract_tag(text, 'READING_LEVEL'),
                'themes': self._extract_tag(text, 'THEMES'),
            }
            
            # Parse illustration ideas
            ideas_match = re.search(r'\[ILLUSTRATION_IDEAS:(.*?)\]', text, re.I | re.DOTALL)
            if ideas_match:
                ideas_text = ideas_match.group(1).strip()
                story.analysis['illustration_ideas'] = [
                    idea.strip('- ').strip() 
                    for idea in ideas_text.split('\n') 
                    if idea.strip() and idea.strip().startswith('-')
                ]
            
        except Exception as e:
            logger.error(f"Story analysis failed: {e}")
    
    def _extract_tag(self, text: str, tag: str) -> str:
        """Extract content between tags."""
        match = re.search(f'\\[{tag}:(.*?)\\]', text, re.I)
        return match.group(1).strip() if match else "N/A"
    
    def save_story_and_characters(self, story: StoryOutput, profile: StoryProfile):
        """Save story and update character database."""
        # Save story
        filepath = self.file_manager.save_story(story, profile)
        if filepath:
            print(f"\n📁 Story saved to: {filepath}")
        
        # Update saved characters
        existing_names = {char.name for char in self.saved_characters}
        new_characters = [
            char for char in profile.characters 
            if char.name not in existing_names
        ]
        
        if new_characters:
            self.saved_characters.extend(new_characters)
            if self.file_manager.save_characters(self.saved_characters):
                print(f"💾 Saved {len(new_characters)} new character(s)")
    
    def view_saved_characters(self):
        """Display all saved characters."""
        if not self.saved_characters:
            print("\n📝 No saved characters yet.")
            return
        
        print("\n--- 🗂️ Saved Characters ---")
        for i, char in enumerate(self.saved_characters, 1):
            print(f"\n{i}. {char.name}")
            print(f"   Age: {char.age}")
            print(f"   Personality: {char.personality}")
            print(f"   Loves: {char.favorites}")
            if char.special_trait:
                print(f"   Special: {char.special_trait}")


def main():
    """Main entry point with enhanced error handling."""
    try:
        ui = UserInterface()
        ui.display_header()
        
        # Get API key
        api_key = getpass.getpass("🔑 Enter your Google AI API Key (hidden): ")
        if not api_key.strip():
            print("❌ API Key is required to use this application.")
            return
        
        # Initialize and run story engine
        engine = StoryEngine(api_key)
        engine.run()
        
    except KeyboardInterrupt:
        print("\n\n✨ Thanks for using the Magical Story Creator! ✨")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check the logs for more details.")


if __name__ == "__main__":
    main()