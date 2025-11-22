from random import randint
from game_logic.spaces import CardSpace
from game_logic.cards import Hand, Card, DeckCard
from game_logic.player import Player



RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS = ["H","D","C","S"]

def print_game(board: CardSpace, player:Player):
    print("\nBoard:")
    board.print_space()
    print("Player Hand:")
    player.print_hand()



def create_deck() -> DeckCard:
    sorted_cards = []
    for suit in SUITS:
        for rank in RANKS:
            sorted_cards.append(Card(rank, suit))

    head = None

    while len(sorted_cards) > 0:
        head = DeckCard(sorted_cards.pop(randint(0,len(sorted_cards)-1)), head)

    return head

def deal_cards(playerList: list[Player], deck: DeckCard):
    card_count = 0

    while card_count < 7:
        for player in playerList:
            player.add_to_hand(deck.draw_card())

        card_count += 1



if __name__ == "__main__":
    deck = create_deck()

    board = CardSpace()


    while True:
        try:
            num_of_players = input("Enter a number between 2-4 to define the number of players in the game: ")
            num_of_players = int(num_of_players)
        except ValueError:
            print("Error")
            print("Please only input a number")
            continue
        break



    player_list = [Player(i+1) for i in range(num_of_players)]
    deal_cards(player_list, deck)

    gameloop = True
    winner = None

    while gameloop:
        for player in player_list:

            playerloop = True
            hands_moved = []
            temp_board = board
            temp_player = player
            has_moved = False
            

            while playerloop:

                print_game(board,player)
                question1 = input("Do you want to make a MOVE or do you want to DRAW a card: ")

                if question1 == "MOVE":
                    question2 = input("Type in the index of the cards that you want to play or type in done to finish your move: ")
                    

                    # This function is missing the validation of the game
                    # when the player types in done we need a function that 
                    # checks the player's hand and the board to ensure that 
                    # all of the hands are valid and if they aren't it should 
                    # reset everything and go back to the beginning of the 
                    # player's turn
                    if question2 == "done":

                        # Check to see if player has moved
                        if not has_moved:
                            print("You need to make a move before finishing your turn.")
                            continue

                        #Check to see if moves are valid
                        for idx in range(len(hands_moved)):
                            valid_hand = hands_moved[idx].checkValidity()
                            
                            if valid_hand:
                                hands_moved.pop(idx)

                        if len(hands_moved) > 0:
                            print("The following hands are invalid: ")
                            for hand in hands_moved:
                                print(hand)

                            temp_board = board
                            temp_player = player
                            hands_moved = []

                        else:
                            print("Valid move")
                            board = temp_board
                            player = temp_player

                            if player.has_finished():
                                winner = player.order
                                gameloop = False

                            playerloop = False


                    else:
                        try:

                            hand = Hand()
                            idx_list = question2.split(",")


                            # HERE THERE IS A BUG WHERE THE INDEXES OF THE CARDS BEING REMOVED ARE BEING SKIPPED
                            # For example:
                            # if the user inputs H/0,H/1,H/2 the code will remove indexes 0,2,4.
                            # This is because we are extracting cards from a hand that is being actively modified
                            for idx in idx_list:
                                card = None
                                card_idx = idx.split("/")
                                if card_idx[0] == "H":
                                    card = temp_player.remove_from_hand(int(card_idx[1]))

                                elif card_idx[0] == "B":
                                    card = temp_board.get_card_from_hand(int(card_idx[1]), int(card_idx[2]))

                                else:
                                    raise ValueError

                                hand.add_card(card)

                            question3 = input("Do you want to add these cards to an existing hand or to a new hand. Type in either the index of the hand or NEW")

                            if question3 == "NEW":
                                temp_board.add_new_hand(hand)

                            else:
                                board.mix_hands(int(question3), hand)

                            



                        except ValueError:
                            print("The input that you put in is invalid please enter a move in the following manner:")
                            print("For a card from hand: H/INDEX_OF_CARD")
                            print("For a card from board: B/INDEX_OF_HAND_IN_BOARD/INDEX_OF_CARD")
                            continue



                if question1 == "SORT":
                    player.hand.sort_hand()


                elif question1 == "DRAW":
                    player.add_to_hand(deck.draw_card())
                    playerloop = False

                else:
                    print("Invalid Input")
                    print("(Valid inputs are MOVE or DRAW)")
