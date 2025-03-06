import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import wikipediaapi
import re
import sympy as sp
import random
from nltk.tokenize import sent_tokenize
from gtts import gTTS
import os
import pygame
import threading

MATH_WORDS_TO_SYMBOLS = {
    'plus': '+',
    'minus': '-',
    'times': '*',
    'divided by': '/',
    'over': '/',
    'to the power of': '**',
    'equals': '=',
    'raised to': '**',
    'modulus': '%',
    'mod': '%'
}

RESTRICTED_CATEGORIES = [
    'Sexuality', 'Violence', 'Pornography', 'Gambling', 'Drugs', 'Weapons',
    'Disallowed content', 'Self-harm', 'Extremism', 'Harassment and hate', 'Illegal activities'
]

def replace_math_words_with_symbols(query):
    for word, symbol in MATH_WORDS_TO_SYMBOLS.items():
        query = re.sub(rf'\b{word}\b', symbol, query, flags=re.IGNORECASE)
    return query

def is_content_restricted(page):
    page_categories = [category.title for category in page.categories.values()]
    return any(restricted.lower() in (cat.lower() for cat in page_categories) for restricted in RESTRICTED_CATEGORIES)

def get_wikipedia_content(query):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent="BubbaQuizBot/1.0 (https://example.com; contact@example.com)"
    )
    page = wiki_wiki.page(query)
    if page.exists():
        if is_content_restricted(page):
            return "Sorry, I cannot provide information on that topic due to content restrictions."
        return page.text
    else:
        return "Sorry, no content found for that topic."

def extractive_summary(text, n=3):
    sentences = sent_tokenize(text)
    return ' '.join(sentences[:n])

def solve_math_expression(expression):
    try:
        result = sp.sympify(expression)
        return f"Result: {result}"
    except Exception:
        return "Invalid mathematical expression."

def text_to_speech(text, filename="output.mp3"):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save(filename)
        print(f"Audio file saved: {filename}")
        return filename
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate audio: {e}")
        return None

def play_audio(filename):
    if filename and os.path.exists(filename):
        pygame.mixer.init()
        print(f"Playing audio file: {filename}")
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        pygame.mixer.quit()

        try:
            os.remove(filename)
            print(f"Deleted audio file: {filename}")
        except Exception as e:
            print(f"Error deleting audio file: {e}")
    else:
        messagebox.showwarning("Warning", "Audio file not found.")

game_total = 0

def reset_game():
    global game_total
    game_total = 0
    game_output.delete("1.0", tk.END)
    game_output.insert(tk.END, "Game reset. Total: 0\n")
    game_output.yview_scroll(1, "units") 

def submit_game_move():
    global game_total
    try:
        user_move = int(game_input.get())
        if not (1 <= user_move <= 10):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a number between 1 and 10.")
        return

    game_total += user_move
    game_output.insert(tk.END, f"You added {user_move}. Total: {game_total}\n")
    game_output.yview_scroll(1, "units") 
    if game_total >= 100:
        game_output.insert(tk.END, "Congratulations, you win!\n")
        game_output.yview_scroll(1, "units") 
        return

    computer_move_value = random.randint(1, min(10, 100 - game_total))
    game_total += computer_move_value
    game_output.insert(tk.END, f"Computer added {computer_move_value}. Total: {game_total}\n")
    game_output.yview_scroll(1, "units") 
    if game_total >= 100:
        game_output.insert(tk.END, "Computer wins! Better luck next time.\n")
        game_output.yview_scroll(1, "units")  

root = tk.Tk()
root.title("Bubba: Educational Chatbot")
root.geometry("600x500")

tab_control = ttk.Notebook(root)

tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Topic Search")
topic_label = tk.Label(tab1, text="Enter a topic:", font=("Arial", 12))
topic_label.pack(pady=10)
topic_input = tk.Entry(tab1, width=50, font=("Arial", 12))
topic_input.pack(pady=5)
topic_output = scrolledtext.ScrolledText(tab1, height=10, width=70, wrap=tk.WORD)
topic_output.pack(pady=10)

def search_topic():
    topic = topic_input.get().strip()
    if not topic:
        messagebox.showerror("Error", "Please enter a topic.")
        return
    processed_topic = replace_math_words_with_symbols(topic)
    content = get_wikipedia_content(processed_topic)
    if content:
        summary = extractive_summary(content)
        topic_output.delete("1.0", tk.END)
        topic_output.insert(tk.END, f"Summary:\n{summary}")
        topic_output.yview_scroll(1, "units") 

        def play_audio_thread():
            audio_file = text_to_speech(summary)
            if audio_file:
                play_audio(audio_file)

        threading.Thread(target=play_audio_thread, daemon=True).start()
    else:
        messagebox.showinfo("Info", "No content found for the given topic.")

search_button = tk.Button(tab1, text="Search", command=search_topic)
search_button.pack(pady=5)

tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="Math Solver")
math_label = tk.Label(tab2, text="Enter a math expression:", font=("Arial", 12))
math_label.pack(pady=10)
math_input = tk.Entry(tab2, width=50, font=("Arial", 12))
math_input.pack(pady=5)
math_output = tk.Label(tab2, text="", font=("Arial", 12), fg="green")
math_output.pack(pady=10)

def solve_math():
    expression = math_input.get().strip()
    if not expression:
        messagebox.showerror("Error", "Please enter a math expression.")
        return
    result = solve_math_expression(replace_math_words_with_symbols(expression))
    math_output.config(text=result)

solve_button = tk.Button(tab2, text="Solve", command=solve_math)
solve_button.pack(pady=5)

tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text="100 Game")
game_label = tk.Label(tab3, text="Enter a number (1 to 10):", font=("Arial", 12))
game_label.pack(pady=10)
game_input = tk.Entry(tab3, width=10, font=("Arial", 12))
game_input.pack(pady=5)
game_output = scrolledtext.ScrolledText(tab3, height=10, width=70, wrap=tk.WORD)
game_output.pack(pady=10)
game_button = tk.Button(tab3, text="Submit Move", command=submit_game_move)
game_button.pack(pady=5)
reset_button = tk.Button(tab3, text="Reset Game", command=reset_game)
reset_button.pack(pady=5)

game_rules = tk.Label(tab3, text=(
    "Game Rules:\n"
    "1. The objective is to reach exactly 100.\n"
    "2. Players take turns to add a number between 1 and 10 (inclusive) to the total.\n"
    "3. If you make the total reach 100, you win!\n"
    "4. If the computer makes the total reach 100, it wins."
), font=("Arial", 10), wraplength=500, justify="left")
game_rules.pack(pady=10)

tab_control.pack(expand=1, fill="both")

root.mainloop()