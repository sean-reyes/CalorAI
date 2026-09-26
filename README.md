# CalorAI: An AI fitness app
_A fitness app that finally works. No more guessing, let AI do the work for you._

## Overview

- Personalized Macro Calculations: Automatically calculates Daily Energy Expenditure (TDEE) and macro ratios based on target weight, activity level, and goals (cutting, maintaining, or bulking).

- AI-Powered Meal Generation: Suggests tailored recipes fitting exact calorie budgets using natural language understanding.

- Dietary Preferences & Allergens: Full support for Keto, Vegan, Vegetarian, Paleo, Gluten-Free, and custom ingredient exclusions.

- Dynamic Swap: Don't like a suggested meal? Swap individual meals on the fly without breaking your daily macro balance.

- Smart Grocery List: Automatically aggregates ingredients across weekly meal plans into categorized shopping lists.

## Features

- Meal selection across breakfast, morning tea, lunch, dessert and dinner menus
- Meat-type filtering for each meal category
- Real-time nutrition calculation for calories, protein, fats and carbs
- Visual graphs comparing total intake with recommended daily intake
- Custom meal creation and deletion
- BMR-based calorie target estimation using sex, height and weight
- AI meal-planning assistant powered by Google Gemini
- Persisted menu and selection state using local JSON files

## Project Structure

```text
CalorAI/
├── prog/
│   ├── ai_assistant.py      # Gemini-based AI meal-planning assistant
│   ├── calculator.py        # Nutrition calculations and chart generation
│   ├── main.py              # Main Tkinter application entry point
│   ├── meal.py              # Meal dropdown/filter logic
│   ├── menus.json           # Predefined menu data
│   ├── last_selections.json # Saved user meal selections
│   ├── storage.py           # JSON load/save helpers
│   └── .env                 # Optional local environment file for API key
├── .gitignore
├── README.md
└── .env.example            # Optional example if you choose to add one
```

## Requirements

- Python 3.9+
- Tkinter (usually included with Python on desktop installs)
- matplotlib
- python-dotenv

Install dependencies with:

```bash
pip install matplotlib python-dotenv
```

## Setup

1. Clone or download the project.
2. Open a terminal in the project root.
3. Create a `.env` file in the project root with your Gemini API key:

```env
API_KEY=your_google_gemini_api_key_here
```

4. Run the app:

```bash
python prog/main.py
```

If you are already inside the `prog` folder, you can also run:

```bash
python main.py
```

## How the App Works

### 1. Selecting meals
The app displays menus for each meal slot. Each category includes a meat filter, allowing users to narrow down meals by protein type.

### 2. Calculating nutrition
When the user clicks “Calculate Nutrition”, the app totals calories, protein, fats and carbs for the selected meals and generates a summary with charts.

### 3. Setting calorie goals
The app includes a “Set Max Calories” section that estimates a daily calorie target from the user’s sex, height and weight using a simplified BMR formula.

### 4. Adding custom meals
Users can add custom meals with nutritional values and assign them to a menu category.

### 5. AI assistant
The AI assistant sends the current selected meals, remaining calories and available menu data to Gemini and helps with suggestions or meal planning guidance.

## Data Files

- `prog/menus.json`: stores the meal library for each menu category.
- `prog/last_selections.json`: stores the user’s previously selected meals so they persist between sessions.

## Notes

- The AI assistant requires a valid `API_KEY` and internet access.
- The app is designed as a desktop GUI and is best run on a local machine with a graphical desktop environment.
- Nutrition values are based on the menu data in the project, so they are only as accurate as the data in `menus.json`.

## Example Workflow

1. Pick meals for breakfast, lunch, dinner and snacks.
2. Apply meat filters if needed.
3. Click “Calculate Nutrition”.
4. Review the charts and totals.
5. Adjust the maximum calories target if needed.
6. Ask the AI assistant for suggestions based on the current selections and remaining calories.

## License

This project is currently unlicensed. (work in progress hold on)
