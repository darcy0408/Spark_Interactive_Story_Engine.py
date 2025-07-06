# Interactive Children's Adventure Engine v0.2
# This version handles multiple children and companions gracefully.

def get_character_details():
    """Gathers details for multiple children and their companions."""
    
    children = []
    companions = []
    
    # --- Gather Child Info ---
    while True:
        add_child = input("Would you like to add a child to the story? (y/n): ").lower()
        if add_child != 'y':
            break
        child = {
            "name": input("  What is this child's name? "),
            "age": input("  What is their age? "),
        }
        children.append(child)

    # --- Gather Companion Info ---
    while True:
        add_companion = input("Would you like to add a magical companion? (y/n): ").lower()
        if add_companion != 'y':
            break
        companion = {
            "name": input("  What is the companion's name? "),
            "type": input("  What kind of companion is it (e.g., 'a trickster elf', 'a wise fairy')? "),
        }
        companions.append(companion)
        
    problem = input("What is a challenge the children are facing? ")
    
    return children, companions, problem

def format_names(character_list):
    """Takes a list of characters and formats their names for the story."""
    if not character_list:
        return ""
    names = [char['name'] for char in character_list]
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        # For more than two, it joins with commas and a final "and"
        return ", ".join(names[:-1]) + ", and " + names[-1]

def generate_story(children, companions, problem):
    """Generates the story text, adventure report, and wisdom gem."""
    
    child_names = format_names(children)
    companion_names = format_names(companions)
    
    # Get the age of the first child for the story text
    age = children[0]['age'] if children else 'a certain'

    story_text = f"""
Once upon a time, in a cozy little town, lived {child_names}, who were {age} years old.
They were kind and smart, but sometimes struggled with {problem}.

One sunny afternoon, while sitting in the park, some magical friends appeared! It was {companion_names}.
"{child_names}!" they chirped, "We are here to go on an adventure with you to help you with {problem}."

Together, they all embarked on a quest through the Whispering Woods. They worked as a team, and {child_names} discovered a hidden strength they never knew they had.
They found a special item along the way!
"""

    adventure_report = f"""
--- Adventure Report ---
* Key Item Found: The Crystal of Courage
* This story explored the theme of: Overcoming {problem}.
"""

    wisdom_gem = f"""
--- Wisdom Gem ---
[Wisdom Gem for this story:] Believing in yourself is the first step to any great adventure.
"""

    full_output = story_text + adventure_report + wisdom_gem
    return full_output

def main():
    """Main function to run the story engine."""
    print("--- Welcome to the Interactive Children's Adventure Engine! ---")
    children_data, companions_data, problem_data = get_character_details()
    
    if not children_data:
        print("You need at least one child to create a story. Please try again.")
        return

    final_story = generate_story(children_data, companions_data, problem_data)
    
    print("\n" + "="*50)
    print("✨ Here is your personalized story! ✨")
    print("="*50 + "\n")
    print(final_story)

if __name__ == "__main__":
    main()
    
