import turtle
import time
import random
import pygame
import json
import os
from datetime import datetime

# Initialize pygame mixer for music
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
COLORS = ['red', 'green', 'blue', 'orange', 'yellow', 'purple', 'pink', 'brown', 'cyan', 'gold']
LANE_COUNT = 10
POINTS_PER_RACE = 100
HIGH_SCORE_FILE = "turtle_racing_scores.json"
MOVEMENT_SPEED = 0.03  # Slower movement for better visibility

class TurtleRacingGame:
    def __init__(self):
        self.screen = None
        self.pen = None
        self.winner_pen = None
        self.players = []
        self.betting_points = 1000
        self.current_round = 1
        self.high_scores = self.load_high_scores()
        self.music_playing = True
        self.turtle_objects = []  # Store turtle objects for cleanup
        
    def load_high_scores(self):
        """Load high scores from file"""
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_high_score(self, name, score):
        """Save high score to file"""
        self.high_scores.append({"name": name, "score": score, "date": datetime.now().strftime("%Y-%m-%d")})
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]
        
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(self.high_scores, f)
    
    def play_music(self):
        """Play background music"""
        try:
            pygame.mixer.music.load('music.mp3')
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
        except:
            print("Could not load music file. Continuing without music.")
            self.music_playing = False
    
    def stop_music(self):
        """Stop background music"""
        if self.music_playing:
            pygame.mixer.music.stop()
    
    def draw_racing_lanes(self):
        """Draw detailed racing lanes with decorations"""
        lane_turtle = turtle.Turtle()
        lane_turtle.speed(0)
        lane_turtle.hideturtle()
        
        # Draw track background
        lane_turtle.penup()
        lane_turtle.goto(-WIDTH//2, -HEIGHT//2)
        lane_turtle.pendown()
        lane_turtle.color('dark gray')
        lane_turtle.fillcolor('dark gray')
        lane_turtle.begin_fill()
        for _ in range(2):
            lane_turtle.forward(WIDTH)
            lane_turtle.left(90)
            lane_turtle.forward(HEIGHT)
            lane_turtle.left(90)
        lane_turtle.end_fill()
        
        # Draw start line
        lane_turtle.penup()
        lane_turtle.goto(-WIDTH//2, -HEIGHT//2 + 40)
        lane_turtle.pendown()
        lane_turtle.color('white')
        lane_turtle.width(3)
        lane_turtle.forward(WIDTH)
        
        # Add "START" text
        lane_turtle.penup()
        lane_turtle.goto(0, -HEIGHT//2 + 20)
        lane_turtle.color('white')
        lane_turtle.write("START", align="center", font=("Arial", 16, "bold"))
        
        # Draw finish line (checkered pattern)
        lane_turtle.penup()
        lane_turtle.goto(-WIDTH//2, HEIGHT//2 - 40)
        lane_turtle.width(5)
        
        for i in range(0, WIDTH, 40):
            if i // 40 % 2 == 0:
                lane_turtle.color('black')
            else:
                lane_turtle.color('white')
            lane_turtle.pendown()
            lane_turtle.forward(40)
            lane_turtle.penup()
        
        # Add "FINISH" text
        lane_turtle.penup()
        lane_turtle.goto(0, HEIGHT//2 - 20)
        lane_turtle.color('gold')
        lane_turtle.write("FINISH", align="center", font=("Arial", 20, "bold"))
        
        # Draw lane dividers
        lane_turtle.width(1)
        lane_turtle.color('light gray')
        spacingx = WIDTH // (LANE_COUNT + 1)
        
        for i in range(LANE_COUNT):
            x = -WIDTH//2 + (i + 1) * spacingx
            lane_turtle.penup()
            lane_turtle.goto(x, -HEIGHT//2 + 50)
            lane_turtle.pendown()
            lane_turtle.setheading(90)
            
            # Dashed lane lines
            for _ in range(0, HEIGHT - 100, 20):
                lane_turtle.pendown()
                lane_turtle.forward(10)
                lane_turtle.penup()
                lane_turtle.forward(10)
        
        # Add lane numbers
        lane_turtle.color('white')
        for i in range(LANE_COUNT):
            x = -WIDTH//2 + (i + 1) * spacingx
            lane_turtle.penup()
            lane_turtle.goto(x - 10, -HEIGHT//2 + 20)
            lane_turtle.write(f"Lane {i + 1}", font=("Arial", 10, "normal"))
    
    def create_custom_turtle(self, color, lane_number, x_position, y_position):
        """Create a visually enhanced turtle with custom shell design"""
        racer = turtle.Turtle()
        racer.speed(0)
        racer.color(color)
        racer.shape('turtle')
        racer.shapesize(1.8, 1.8)  # Bigger turtles
        
        # Add shell pattern (dots on the turtle's back)
        shell = turtle.Turtle()
        shell.speed(0)
        shell.hideturtle()
        shell.penup()
        shell.color('black' if color != 'black' else 'white')
        
        # Position the shell pattern
        shell.goto(x_position, y_position + 10)
        shell.dot(15, shell.color()[0])
        
        # Add lane number on turtle's back
        name_tag = turtle.Turtle()
        name_tag.hideturtle()
        name_tag.penup()
        name_tag.goto(x_position - 20, y_position + 25)
        name_tag.color('white')
        name_tag.write(f"#{lane_number}", font=("Arial", 8, "bold"))
        
        # Add turtle name
        turtle_name = turtle.Turtle()
        turtle_name.hideturtle()
        turtle_name.penup()
        turtle_name.goto(x_position - 30, y_position - 20)
        turtle_name.color(color)
        turtle_name.write(f"{color.upper()}", font=("Arial", 9, "bold"))
        
        racer.left(90)
        racer.penup()
        racer.setpos(x_position, y_position)
        racer.pendown()
        
        # Store all created objects
        self.turtle_objects.extend([racer, shell, name_tag, turtle_name])
        
        return racer
    
    def display_winner_message(self, winner_color, round_num=None):
        """Display a prominent winner announcement"""
        # Clear previous winner messages
        self.winner_pen.clear()
        
        # Winner announcement
        self.winner_pen.penup()
        self.winner_pen.goto(0, 0)
        self.winner_pen.color(winner_color)
        self.winner_pen.write(f"🏆 WINNER: {winner_color.upper()} TURTLE! 🏆", 
                             align="center", font=("Arial", 24, "bold"))
        
        # Subtitle
        self.winner_pen.goto(0, -50)
        self.winner_pen.color('white')
        
        if round_num:
            self.winner_pen.write(f"Round {round_num} Complete!", 
                                 align="center", font=("Arial", 18, "normal"))
        else:
            self.winner_pen.write(f"Congratulations {winner_color.upper()}!", 
                                 align="center", font=("Arial", 18, "normal"))
        
        self.screen.update()
        time.sleep(2)
    
    def race(self, colors, round_num):
        """Conduct a single race with slower, visible movement"""
        turtles = []
        spacingx = WIDTH // (len(colors) + 1)
        
        # Create enhanced turtles
        for i, color in enumerate(colors):
            x_pos = -WIDTH//2 + (i + 1) * spacingx
            y_pos = -HEIGHT//2 + 50
            racer = self.create_custom_turtle(color, i + 1, x_pos, y_pos)
            turtles.append(racer)
        
        # Display race start message
        self.pen.clear()
        self.pen.penup()
        self.pen.goto(0, HEIGHT//2 - 100)
        self.pen.color('yellow')
        self.pen.write(f"🏁 ROUND {round_num} - READY, SET, GO! 🏁", 
                      align="center", font=("Arial", 20, "bold"))
        self.screen.update()
        time.sleep(1.5)
        self.pen.clear()
        
        # Get bet for this race
        if self.betting_points > 0:
            bet_amount, bet_color = self.get_bet(self.betting_points, colors)
        else:
            bet_amount = 0
            bet_color = None
            self.display_message("You're out of points! Watching for fun...", 2)
        
        # Race animation
        race_complete = False
        frame = 0
        winner_color = None
        winner_turtle = None
        
        # Race progress bars
        progress_bars = {}
        for i, color in enumerate(colors):
            bar = turtle.Turtle()
            bar.hideturtle()
            bar.penup()
            bar.goto(-WIDTH//2 + (i + 1) * spacingx - 20, -HEIGHT//2 + 30)
            progress_bars[color] = bar
        
        while not race_complete:
            self.draw_animated_background(frame)
            frame += 1
            
            for racer in turtles:
                # Slower, more consistent movement
                distance = random.randrange(3, 8)  # Reduced range for slower speed
                racer.forward(distance)
                
                # Update progress bar
                x, y = racer.pos()
                progress = (y + HEIGHT//2 - 50) / (HEIGHT - 100) * 100
                
                x, y = racer.pos()
                if y >= HEIGHT//2 - 50:
                    winner_color = colors[turtles.index(racer)]
                    winner_turtle = racer
                    race_complete = True
                    break
            
            self.screen.update()
            time.sleep(MOVEMENT_SPEED)  # Slower animation
        
        # Winner celebration animation
        if winner_turtle:
            for _ in range(5):
                winner_turtle.shapesize(2.2, 2.2)
                self.screen.update()
                time.sleep(0.1)
                winner_turtle.shapesize(1.8, 1.8)
                self.screen.update()
                time.sleep(0.1)
        
        # Display winner message
        self.display_winner_message(winner_color, round_num)
        
        # Calculate betting results
        if bet_color == winner_color and bet_amount > 0:
            winnings = bet_amount * 2
            self.betting_points += winnings
            self.display_message(f"🎉 YOU WON! +{winnings} points! (Total: {self.betting_points})", 3)
        elif bet_amount > 0:
            self.betting_points -= bet_amount
            self.display_message(f"😢 You lost {bet_amount} points. (Remaining: {self.betting_points})", 3)
        
        # Award participation points
        self.betting_points += POINTS_PER_RACE // round_num
        self.display_message(f"Participation bonus: +{POINTS_PER_RACE // round_num} points", 2)
        
        return winner_color, turtles
    
    def display_message(self, message, duration):
        """Display a temporary message on screen"""
        msg_turtle = turtle.Turtle()
        msg_turtle.hideturtle()
        msg_turtle.penup()
        msg_turtle.goto(0, -HEIGHT//2 + 80)
        msg_turtle.color('white')
        msg_turtle.write(message, align="center", font=("Arial", 14, "bold"))
        self.screen.update()
        time.sleep(duration)
        msg_turtle.clear()
    
    def get_bet(self, max_bet, colors):
        """Get betting points from player with visual feedback"""
        # Display betting UI
        bet_turtle = turtle.Turtle()
        bet_turtle.hideturtle()
        bet_turtle.penup()
        bet_turtle.goto(0, HEIGHT//2 - 50)
        bet_turtle.color('gold')
        bet_turtle.write(f"💰 Points: {self.betting_points}", 
                        align="center", font=("Arial", 16, "bold"))
        self.screen.update()
        
        print(f"\n💰 You have {self.betting_points} points")
        print(f"Available turtles: {', '.join(colors[:5])}...")
        
        while True:
            try:
                bet_amount = input(f"Enter your bet amount (1-{min(self.betting_points, 500)}): ")
                bet_amount = int(bet_amount)
                
                if 1 <= bet_amount <= min(self.betting_points, 500):
                    bet_color = input(f"Enter the color you want to bet on: ").lower()
                    
                    if bet_color in colors:
                        bet_turtle.clear()
                        bet_turtle.color('green')
                        bet_turtle.write(f"Bet placed: {bet_amount} points on {bet_color} turtle!", 
                                       align="center", font=("Arial", 14, "bold"))
                        self.screen.update()
                        time.sleep(1.5)
                        bet_turtle.clear()
                        return bet_amount, bet_color
                    else:
                        print("Invalid color! Try again.")
                else:
                    print(f"Invalid bet amount! Must be between 1 and {min(self.betting_points, 500)}")
            except ValueError:
                print("Please enter a valid number!")
    
    def get_number_of_racers(self):
        """Get number of racers from user"""
        racers = 0
        while True:
            racers = input('Enter the number of racers (2 - 10): ')
            if racers.isdigit():
                racers = int(racers)
            else:
                print('Input is not numeric... Try Again!')
                continue

            if 2 <= racers <= 10:
                return racers
            else:
                print('Number not in range 2-10. Try Again!')
    
    def draw_animated_background(self, frame=0):
        """Draw animated background effects"""
        if frame % 30 == 0:  # Less frequent animations
            if random.random() < 0.3:  # 30% chance
                bg_turtle = turtle.Turtle()
                bg_turtle.hideturtle()
                bg_turtle.speed(0)
                bg_turtle.penup()
                
                x = random.randint(-WIDTH//2, WIDTH//2)
                y = random.randint(HEIGHT//4, HEIGHT//2)
                bg_turtle.goto(x, y)
                bg_turtle.dot(random.randint(5, 15), 'light yellow')
                self.turtle_objects.append(bg_turtle)
    
    def tournament(self):
        """Run multiple rounds of racing"""
        print("\n🏆 WELCOME TO THE TURTLE RACING TOURNAMENT! 🏆")
        player_name = input("Enter your name for the high score: ")
        
        # Initialize screen
        self.init_turtle()
        
        # Start music
        self.play_music()
        
        # Draw racing lanes
        self.draw_racing_lanes()
        
        total_racers = self.get_number_of_racers()
        
        # Tournament rounds
        round_winners = []
        round_num = 1
        
        while round_num <= 3 and self.betting_points > 0:
            print(f"\n{'='*50}")
            print(f"ROUND {round_num} - Points: {self.betting_points}")
            print(f"{'='*50}")
            
            # Display round banner
            self.pen.clear()
            self.pen.penup()
            self.pen.goto(0, HEIGHT//2 - 50)
            self.pen.color('gold')
            self.pen.write(f"ROUND {round_num}", align="center", font=("Arial", 30, "bold"))
            self.screen.update()
            time.sleep(1.5)
            self.pen.clear()
            
            # Shuffle colors for this round
            round_colors = random.sample(COLORS, total_racers)
            
            # Run race
            winner, racers = self.race(round_colors, round_num)
            round_winners.append((round_num, winner))
            
            # Clean up turtles from this round
            for racer in racers:
                racer.hideturtle()
            
            # Display round results
            results_turtle = turtle.Turtle()
            results_turtle.hideturtle()
            results_turtle.penup()
            results_turtle.goto(0, -HEIGHT//2 + 100)
            results_turtle.color('light blue')
            results_turtle.write(f"Round {round_num} Winner: {winner.upper()}!", 
                               align="center", font=("Arial", 16, "bold"))
            self.screen.update()
            time.sleep(2)
            results_turtle.clear()
            
            if round_num < 3 and self.betting_points > 0:
                play_again = input("\nContinue to next round? (yes/no): ").lower()
                if play_again != 'yes':
                    break
            
            round_num += 1
        
        # Tournament results
        self.display_tournament_results(round_winners)
        
        # Check if it's a high score
        self.check_high_score(player_name)
        
        self.stop_music()
        time.sleep(5)
    
    def display_tournament_results(self, round_winners):
        """Display tournament results on screen"""
        result_turtle = turtle.Turtle()
        result_turtle.hideturtle()
        result_turtle.speed(0)
        result_turtle.penup()
        
        # Clear screen for results
        self.pen.clear()
        self.winner_pen.clear()
        
        # Tournament champion
        champion = max(set([w[1] for w in round_winners]), 
                      key=lambda x: [w[1] for w in round_winners].count(x))
        
        result_turtle.goto(0, 100)
        result_turtle.color('gold')
        result_turtle.write("🏆 TOURNAMENT CHAMPION 🏆", 
                          align="center", font=("Arial", 24, "bold"))
        
        result_turtle.goto(0, 40)
        result_turtle.color(champion)
        result_turtle.write(f"{champion.upper()} TURTLE!", 
                          align="center", font=("Arial", 28, "bold"))
        
        # Round results
        result_turtle.goto(0, -20)
        result_turtle.color('white')
        result_turtle.write("Round Results:", align="center", font=("Arial", 18, "bold"))
        
        y_pos = -60
        for round_num, winner in round_winners:
            result_turtle.goto(0, y_pos)
            result_turtle.color(winner)
            result_turtle.write(f"Round {round_num}: {winner.capitalize()}", 
                              align="center", font=("Arial", 16, "normal"))
            y_pos -= 30
        
        result_turtle.goto(0, y_pos - 20)
        result_turtle.color('white')
        result_turtle.write(f"Final Score: {self.betting_points} points", 
                          align="center", font=("Arial", 16, "bold"))
        
        self.screen.update()
    
    def check_high_score(self, player_name):
        """Check and save high scores"""
        high_score_threshold = 0
        if self.high_scores:
            high_score_threshold = self.high_scores[-1]["score"] if len(self.high_scores) >= 10 else 0
        
        if self.betting_points > high_score_threshold or len(self.high_scores) < 10:
            print("\n🎉 NEW HIGH SCORE! 🎉")
            self.save_high_score(player_name, self.betting_points)
            self.display_message(f"NEW HIGH SCORE! {self.betting_points} points", 3)
        
        # Display high scores
        self.display_high_scores()
    
    def display_high_scores(self):
        """Display high scores on screen"""
        score_turtle = turtle.Turtle()
        score_turtle.hideturtle()
        score_turtle.speed(0)
        score_turtle.penup()
        
        score_turtle.goto(0, -HEIGHT//2 + 150)
        score_turtle.color('light blue')
        score_turtle.write("🏆 HIGH SCORES 🏆", align="center", font=("Arial", 18, "bold"))
        
        y_pos = -HEIGHT//2 + 120
        for i, score in enumerate(self.high_scores[:5], 1):
            score_turtle.goto(0, y_pos)
            score_turtle.color('white')
            score_turtle.write(f"{i}. {score['name']}: {score['score']} pts ({score['date']})", 
                            align="center", font=("Arial", 12, "normal"))
            y_pos -= 25
        
        self.screen.update()
    
    def init_turtle(self):
        """Initialize turtle screen"""
        self.screen = turtle.Screen()
        self.screen.setup(WIDTH, HEIGHT)
        self.screen.title('🐢 Turtle Racing Tournament 🏁')
        self.screen.bgcolor('#1a472a')  # Dark green track
        self.screen.tracer(0)
        
        # Create pens for different purposes
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.color('white')
        
        self.winner_pen = turtle.Turtle()
        self.winner_pen.hideturtle()
        self.winner_pen.speed(0)

def main():
    """Main game function"""
    while True:
        game = TurtleRacingGame()
        game.tournament()
        
        play_again = input("\nPlay another tournament? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing! 🐢")
            print("Final High Scores:")
            game.display_high_scores()
            break

if __name__ == "__main__":
    main()