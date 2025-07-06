# Interactive Children's Adventure Engine v0.1
# This version runs in the terminal and builds a story based on user input.

def get_user_input():
    """Gathers all the necessary information from the user to build the story."""
    
    print("--- Welcome to the Interactive Children's Adventure Engine! ---")
    
    # In a real app, this data would be stored in a profile.
    story_data = {
        "name": input("What is the child's name? "),
        "age": input("What is the child's age? "),
        "problem": input("What is a challenge they're facing (e.g., 'being shy', 'making friends')? "),
        "companion_type": input("What kind of magical companion should they have (e.g., 'a talking squirrel', 'a tiny robot')? "),
        "companion_name": input("What is the companion's name? ")
    }
    return story_data

def generate_story(data):
    """Generates the story text, adventure report, and wisdom gem from the data."""
    
    # This is a simple template. The real magic will come when we connect this to an AI model.
    story_text = f"""
Once upon a time, in a cozy little town, lived a {data['age']}-year-old named {data['name']}.
{data['name']} was kind and smart, but sometimes struggled with {data['problem']}.

One sunny afternoon, while sitting in the park, a magical friend appeared! It was {data['companion_name']}, the {data['companion_type']}.
"{data['name']}!" said {data['companion_name']}, "I'm here to go on an adventure with you to help you with {data['problem']}."

Together, they embarked on a quest through the Whispering Woods. They worked as a team, and {data['name']} discovered a hidden strength they never knew they had.
They found a special item along the way!
"""

    adventure_report = f"""
--- Adventure Report ---
* Key Item Found: The Crystal of Courage
* This story explored the theme of: Overcoming {data['problem']}.
"""

    wisdom_gem = f"""
--- Wisdom Gem ---
[Wisdom Gem for this story:] Believing in yourself is the first step to any great adventure.
"""

    # Combine all parts of the output
    full_output = story_text + adventure_report + wisdom_gem
    return full_output

def main():
    """Main function to run the story engine."""
    story_details = get_user_input()
    final_story = generate_story(story_details)
    print("\n" + "="*50)
    print("✨ Here is your personalized story! ✨")
    print("="*50 + "\n")
    print(final_story)

if __name__ == "__main__":
    main()