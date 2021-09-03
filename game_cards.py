import sqlite3
from time import time
from random import randint
import os.path

# This is finding the path to the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "computer_cards.db")

#This is connecting the database
conn = sqlite3.connect(db_path) 

#This counts how many wins and it starts with 0 
winnercount = 0

#This is getting the player information from the terminal/prompt
choosing_player = input("Are you player (1) or (2) > ")

#This saves the card that has been picked into a new row under 'card1' of the results database
def savecard1(card1):
    insert_sql = "INSERT INTO result(card1) VALUES ('{}')".format(card1)
    conn.execute(insert_sql)
    conn.commit()

#This updates the card2 to the previous row that was made above 
def savecard2(card2):
    result = conn.execute("SELECT * FROM result ORDER BY rowid DESC")
    onerow = result.fetchone()
    if onerow[1] is None and onerow[2] is None:
        update_sql = "UPDATE result set card2 = '{}' WHERE card1 = '{}'".format(card2,onerow[0])
        conn.execute(update_sql)
        conn.commit()

#This updates the previous result with the winner value 
def savewinner(winnercard):
    result = conn.execute("SELECT * FROM result ORDER BY rowid DESC")
    onerow = result.fetchone()
    if onerow[0] is not None and onerow[1] is not None and onerow[2] is None : # this checks if the 'card1' column and 'card2' column is not empty
        update_sql = "UPDATE result set winner = '{}' WHERE card1 = '{}'".format(winnercard,onerow[0]) # this updates the winner column with the result you put in the prompt. For example, you won with the Fedora card against Raspberry Pi 4 Model B 4GB so that is now Fedora is in the column "winner"
        conn.execute(update_sql)
        conn.commit()

# This reads all the cards available that you can play
def read_all_cards():
    result = conn.execute("SELECT * FROM computer")
    return result.fetchall()


# saves the selected card in the picked table 
def insert_picked(name):
    insert_sql = "INSERT INTO picked(name, time) VALUES ('{}', {})".format(name, time())
    conn.execute(insert_sql)
    conn.commit()

# this selects the last card from the picked table
def read_last_picked():
    result = conn.execute("SELECT * FROM picked ORDER BY time DESC")
    return result.fetchone()

# this reads the last card picked in order to not have the same card as your opponent 
def pick_card():
    cards = read_all_cards()

    last_picked_card = read_last_picked()

    random_card = cards[randint(0, len(cards) - 1)]

    while random_card[0] == last_picked_card[0]:
        random_card = cards[randint(0, len(cards) - 1)]

    insert_picked(random_card[0])
    return random_card

# this checks if the card1 has already been saved in the results table
def Is_card1_saved():
    query_sql = "SELECT * FROM result ORDER BY rowid DESC"
    result = conn.execute(query_sql)
    resultcardOne = result.fetchone()
    last_picked_card = read_last_picked()
    
    if resultcardOne[0] != last_picked_card[0]:
        return False
    else:
        return True
# this removes any cards that resulted in a draw so that it doesnt appear in the result table
def removeDraw():
    result = conn.execute("SELECT rowid FROM result ORDER BY rowid DESC")
    onerow = result.fetchone()
    delete_sql = "DELETE FROM result WHERE rowid = {} AND winner is NULL".format(onerow[0])
    conn.execute(delete_sql)
    conn.commit()


print("This game is best of 5")
for round in range(5): # this will loop 5 so that you play five cards each round
    input("Press enter to pick a card when player 1 is ready > ")
    isCard1saved = Is_card1_saved()
    # this makes sure player 1 always goes first, if this doesn't happen the program exits
    if isCard1saved == False and choosing_player == '2':
        print("Out of courtesy, let player 1 go first, just like chess! Start Again!!!")
        exit()

# this picks up a card
    card = pick_card()
    if choosing_player == '1':
        savecard1(card[0]) # this saves the player 1's card which is card1 in the result table
    else:
        savecard2(card[0])# this saves the player 2's card which is card2 in the result table
# this is the format of the values in the card and makes it actually look like a card
    card_text1 = '''
+------------------------------------------+
 '''+card[0] +'''                         
                                         
  Cores            '''+str(card[1])+'''  
  CPU speed        '''+str(card[2])+'''GHz      
  RAM              '''+str(card[3])+'''MB        
  Cost             £'''+str(card[1])+'''    
                                            
+------------------------------------------+ 
'''

# prints the card that was selected in a card format
    print(card_text1)

    print("Player " + str(choosing_player) + " picks.") # prints which player is currently playing
    winner = input("Did you win? (Y)es, (N)o, (D)raw > ").lower()# receives the information of which player's card won
    if winner == "y":
        print("You won? Good. life's all about winning after all")
        savewinner(card[0]) # saves the winner's card in the winner column of the result table
        winnercount = winnercount + 1 # counts the number of time the player has won
    elif winner == "n":
        print("You lost? That's okay, life's about the journey, not the destination")
    elif winner == "d":
        removeDraw() # calls the function that removes all draws that happened in the game

# this prints the results of each player. For example: You won: 3
print("You won : ",winnercount)
conn.close() # this closes the database connection so an error doesn't occur