Escape Room AI Game


Welcome to the Escape Room AI Game, a Python project where players navigate through an escape room environment with the aid of an AI agent. The AI helps players find their way to the key and escape the room while adhering to a grid-based structure for movement and interactions.


Features

* Grid-based Escape Room: Players and AI agents navigate a grid-based room layout to locate the key and reach the exit.
* Player vs. AI Roles:
o The player controls their character manually to explore the room.
o The AI uses informed search techniques to guide itself to the key and exit.
* Informed AI Search:
o Implements efficient algorithms for navigation and finding objectives within the room.
o Provides a visual and interactive simulation of the AI’s decision-making process.
* Python and Pygame Integration:
o Developed using Python and the Pygame library for rendering the environment and managing interactions.
* Customizable Game Environment:
o Modify the grid size, obstacles, and room layout through configuration.


Project Structure

EscapeRoomGame/
\-- main.py         # Main game logic and loop.
\-- ai.py           # AI agent logic and search algorithms.
\-- assets/         # Assets like sprites and audio files.
\-- config.py       # Configurable parameters (grid size, colors, etc.).
\-- README.md       # Project documentation.
\-- requirements.txt # Python dependencies.

File Descriptions
* main.py: Handles the game loop, rendering, and player controls.
* ai.py: Contains the AI logic for navigating the room and finding the key using informed search algorithms.
* assets/: Stores all graphical and audio assets for the game.
* config.py: Centralized location for modifying grid size, colors, and other game settings.
* requirements.txt: Lists all dependencies required to run the project.

Installation
Clone the repository:
git clone https://github.com/yourusername/EscapeRoomAI.git
cd EscapeRoomAI

Install dependencies: 
Make sure you have Python installed. Install the required Python libraries using
pip install -r requirements.txt

Run the game: 
Execute the following command is main directory to start the game:
python main.py



How to Play
Player Controls
* Arrow Keys: Move the player character.
* Objective: Locate the key and escape through the exit.
AI Agent
* The AI navigates the environment autonomously using informed search techniques to find the key and exit.
* Press A to toggle between Ai and manual

Customization
Room Layout
Modify the config.py file to:
* Change grid size.
* Adjust the placement of obstacles, key, and exit.
* Customize player and AI starting positions.
Visual Assets
Replace assets in the assets/ folder with your own images or sprites for a personalized experience.



