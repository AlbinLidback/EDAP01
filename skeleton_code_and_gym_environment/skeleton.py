import gym
import random
import requests
import numpy as np
import argparse
import sys
import math
import copy
from gym_connect_four import ConnectFourEnv

env: ConnectFourEnv = gym.make("ConnectFour-v0")

# SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["al0235li-s"]  # TODO: fill this list with your stil-id's


def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                           data={
                           "stil_id": STIL_ID,
                           "move": move,  # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                           })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res


def check_stats():
   res = requests.post(SERVER_ADRESS + "stats",
                        data={
                           "stil_id": STIL_ID,
                           "api_key": API_KEY,
                        })

   stats = res.json()
   return stats


"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""


def opponents_move(env):
   env.change_player()  # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player()  # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))
   #action = random.choice(minmax(state, 5, -math.inf, math.inf, True)[0])

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1:  # reward is always in current players view
         reward = -1
   env.change_player()  # change back to student before returning
   return state, reward, done

def student_move(board):
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """

   # choice = random.choice([0, 1, 2, 3, 4, 5, 6])
   choice, score = minmax(board, 5, -math.inf, math.inf, True)
   print("AI Move to return: ", choice, ". With a score of: ", score, "\n")
   if choice == None:
      print("AI CHOICE = None!")
   return choice


def minmax(game, depth, alpha, beta, max_play):
   valid_locations = get_available_moves(game)
   winningPlayer = is_winning_move(game, -1)
   winningAI = is_winning_move(game, 1)
    
   is_terminal = winningPlayer or winningAI or len(valid_locations) == 0

   if depth == 0 or is_terminal:
      if is_terminal:
         if winningAI:
            return None, 100 #math.inf
         elif winningPlayer:
            return None, -100 #-math.inf
      else:
         return None, get_score(game, max_play)

   if max_play:
      value = -math.inf
      column = random.choice(valid_locations)
      for col in valid_locations:
         game_copy = add_disc_in_col(copy.copy(game), col, 1)
         new_score = minmax(game_copy, depth - 1, alpha, beta, False)[1]
         #print("MAX, depth ", depth ," Trying col = ", col, ", score = ", new_score)
         if new_score > value:
            value = new_score
            column = col

         alpha = max(alpha, value)
         if alpha >= beta:
            #print(alpha-beta)
            break
      return column, value

   else:  # minPlay
      value = math.inf
      column = random.choice(valid_locations)
      for col in valid_locations:
         game_copy = add_disc_in_col(copy.copy(game), col, -1)
         new_score = minmax(game_copy, depth - 1, alpha, beta, True)[1]
         #print("MIN, depth ", depth ," Trying col = ", col, ", score = ", new_score)
         if new_score < value:
            value = new_score
            column = col

         beta = min(beta, value)
         if alpha >= beta:
            #print(alpha-beta)
            break
   return column, value


def get_score(board, piece):
   score = 0

   player = -1 if piece else 1
   center_array = list(board[:, 3])
   center_count = center_array.count(player)
   #print("Center board: ", board[:, 3], "player is ", player, "count is ", center_count)
   score += center_count * 2

	# Horizontal
   for r in range(6):
      row_array = board[r, :]
      for c in range(4): # 7-3
         window = row_array[c:c+4]
         score += evaluate_sliding_window(window, player)
         
	# Vertical
   for c in range(7):
      col_array = board[:, c]
      for r in range(6-3):
         window = col_array[r:r+4]
         score += evaluate_sliding_window(window, player)

	# pos diagonal
   for r in range(6-3):
      for c in range(7-3):
         window = [board[r + i, c + i] for i in range(4)]
         score += evaluate_sliding_window(window, player)

   # neg diagonal
   for r in range(6-3):
      for c in range(7-3):
         window = [board[r + 3 - i, c + i] for i in range(4)]
         score += evaluate_sliding_window(window, player)

   return score


def is_winning_move(board, piece):
   # horizontal
   for c in range(4):  # 7-3
      for r in range(6):
         if board[r, c] == piece and board[r, c+1] == piece and board[r, c+2] == piece and board[r, c+3] == piece:
            return True

   # vertical
   for c in range(7):
      for r in range(3):  # 6-3
         if board[r, c] == piece and board[r+1, c] == piece and board[r+2, c] == piece and board[r+3, c] == piece:
            return True

   # pos slope
   for c in range(4): #7-3
      for r in range(3): # 6-3
         if board[r, c] == piece and board[r+1, c+1] == piece and board[r+2, c+2] == piece and board[r+3, c+3] == piece:
            return True

   # neg slope
   for c in range(4): #7-3
      for r in range(3, 6):
         if board[r, c] == piece and board[r-1, c+1] == piece and board[r-2, c+2] == piece and board[r-3, c+3] == piece:
            return True   
   return False

def add_disc_in_col(org_game, col, player:int):
   game = list(org_game[: , col])
   for x in range(6):
      if x < 5:
         if game[x] == 0 and game[x + 1] != 0:
            game[x] = player
      else:
         game[x] = player
   ret_game = org_game
   ret_game[:, col] = np.array(game)
   return ret_game

def get_available_moves(game) -> int:
   available = []
   for col in range(7):
      if game[0, col] == 0:
         available.append(col)
   return available

def evaluate_sliding_window(window, player):
   score = 0
   #player = -1 if max_play else 1
   op_player = player * -1

   array = list(window)
   player_pices = array.count(player)
   op_player_pices = array.count(op_player)
   empty_pices = array.count(int(0))

   #print("Window ", array, ", num of play", player_pices, ", num of op_play", op_player_pices, ", num of fre", empty_pices)

   if player_pices == 4:
      score += 10
   if player_pices == 3 and empty_pices == 1:
      score += 5
   if player_pices == 2 and empty_pices == 2:
      score += 2

   if op_player_pices == 4:
      score -= 30
   if op_player_pices == 3 and empty_pices == 1:
      score -= 20

   return score
      

def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   while not done:
      # Select your move
      stmove = student_move(copy.copy(state)) # TODO: change input here

      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tied to make an illegal move! You have lost the game.")
               break
            state, result, done, _ = env.step(stmove)

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            #state, result, done = student_move2(env)
            state, result, done = opponents_move(env)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   # Parse command line arguments
   parser = argparse.ArgumentParser()
   group = parser.add_mutually_exclusive_group()
   group.add_argument("-l", "--local", help = "Play locally", action="store_true")
   group.add_argument("-o", "--online", help = "Play online vs server", action="store_true")
   parser.add_argument("-s", "--stats", help = "Show your current online stats", action="store_true")
   args = parser.parse_args()

   # Print usage info if no arguments are given
   if len(sys.argv)==1:
      parser.print_help(sys.stderr)
      sys.exit(1)

   if args.local:
      play_game(vs_server = False)
   elif args.online:
      play_game(vs_server = True)

   if args.stats:
      stats = check_stats()
      print(stats)

   # TODO: Run program with "--online" when you are ready to play against the server
   # the results of your games there will be logged
   # you can check your stats bu running the program with "--stats"

if __name__ == "__main__":
    main()