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

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["da20example-s1"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
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
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

def student_move(env) -> int:
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   
   #choice = random.choice([0, 1, 2, 3, 4, 5, 6])
   #score = None

   choice, score = minmax(env.board.tolist(), 3, -math.inf, math.inf, True)
   print("Choice to return: ", choice,". With a score of: ", score, "\n")
   return choice

def minmax(game, depth, alpha, beta, max_play):
   available_moves = get_available_moves(game)
   
   if depth == 0:
      score = evaluate(game, max_play)
      return None, score

   if max_play:
      value = -math.inf
      column = available_moves.pop()
      
      for col in available_moves:
         row = next_free_row(game, col)
         
         new_game = add_in_col(game, col, 1)

         new_choice, new_score = minmax(new_game, depth - 1, alpha, beta, False)
         if new_score > value:
            value = new_score
            column = col
         
         alpha = max(alpha, value)
         if alpha >= beta:
            break
      return column, value

   else: # minPlay 
      value = math.inf
      column = random.choice(available_moves)

      for col in available_moves:
         row = next_free_row(game, col)
         
         new_game = add_in_col(game, col, -1)

         new_choice, new_score = minmax(new_game, depth - 1, alpha, beta, True)
         if new_score > value:
            value = new_score
            column = col
         
         beta = min(beta, value)
         if alpha >= beta:
            break
      return column, value

def add_in_col(game, col, player):
   for row in game[:][col]:
      if game[row][col] == 0 and game[row + 1][col] == player:
         game[row][col] = player
         return game
   print("-- Fel i add_in_col funktionen! --\n")
   return None

def get_available_moves(board):
   #available = {10, 11}
   #available.clear()
   #for x in range(7):
   #   if board[0][x] == 0:
   #      available.add(x)
   #return available

   return [0, 1, 2, 3, 4, 5, 6]

def next_free_row(board, col):
   for row in range(6):
      if board[row][col].equals == 0:
         return row

def eval_window(window, max_play):
   score = 0
   player = 1 if max_play else -1
   op_player = player * -1

   player_pices = np.count_nonzero(window == player)
   op_player_pices = np.count_nonzero(window == op_player)

   if player_pices == 4:
      score += 100
   elif player_pices == 3 and op_player_pices != 1:
      score += 5
   elif player_pices == 2 and op_player_pices != 2:
      score += 2
   elif player_pices == 1 and op_player_pices != 3:
      score += 1

   if op_player_pices == 3:
      score -= 4
   elif op_player_pices == 2:
      score -= 2
   elif op_player_pices == 1:
      score -= 1

   return score

def evaluate(board, max_play):
   player = 1 if max_play else -1

   score = 0

	## Center   
   center_count = np.count_nonzero(board[:, 3] == player)
   score += center_count * 3

	## Horizontal
   for col in range(7):
      col_array = board[:, col]
      for row in col_array:
         window = col_array[row:row + 4]
         score += eval_window(window, max_play)

	## Vertical
   for row in range(6):
      row_array = board[row, :]
      for col in row_array:
         window = row_array[row:row + 4]
         score += eval_window(window, max_play)

	## Diagonal
   for col in range(4):
      for row in range(3):
         window_1 = [board[row, col], board[row + 1, col + 1], board[row + 2, col + 2], board[row + 3, col + 3]]
         window_2 = [board[5 - row, 6 - col], board[4 - row, 5 - col], board[3 - row, 4 - col], board[2 - row, 3 - col]]
         score += eval_window(window_1, max_play)
         score += eval_window(window_2, max_play)

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
      stmove = student_move(copy.copy(env)) # TODO: change input here

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