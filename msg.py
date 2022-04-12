start_msg = "Hello, I can give you game recommendations or news! " \
            "Please click on the button or type something to get started. " \
            "You can click help or type /help to get more information."

help_msg = "You can click the buttons below to get started. " \
           "Alternatively, you can type commands or something like _I want to query a game_. " \
           "I will try to understand what you want! \n\n" \
           "*Available Commands:*\n" \
           "/start - Start the bot; Back to Main Menu\n" \
           "/help - Display this help message\n" \
           "/teach <intent> -t <text> - Teach the bot to understand a new intent\n\n" \
           "*Game Query:*\n" \
           "1. Follow the prompt to type the game game\n" \
           "2. Click on the game you want to query. If it doesn't appear, please try to type in the full game\n" \
           "3. Click on `Get Recommendations` to get the recommendations of the game\n" \
           "You can always click `Back` and reselect and click on different games to update the information\n\n" \
           "*Game Filtering:*\n" \
           "1. Click on different filters to view the available values\n" \
           "2. Click a desirable value to set for that filter (Currently, only one value is supported)\n" \
           "3. Click `Back` to the go to the previous page and set other filters, if any\n" \
           "4. Click `Done` to view the results\n" \
           "The set filters will be updated in the message above. " \
           "Please set at least one filter before clicking `Done`. " \
           "There can be no results matching your filters. A floating notification will pop up if so." \

ask_game_input_msg = "Please give me a game name! Full names will make better matches.\n\n " \
                     "For example, enter _Counter Strike: Global Offensive_ instead of _CS:GO_ or _cs go_."

confirm_game_input_msg = "Please confirm the game you are looking for."

display_filter_msg = "Hi! I would like to get more information about your preference of the games. " \
                     "You can click the buttons below to set different filters.\n" \
                     "You can click *Done* to get the results after you set all filters. \n\n" \
                     "{}"

filter_msg = "What {} do u prefer?\n\n{}"

