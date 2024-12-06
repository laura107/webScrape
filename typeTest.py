import pyautogui
import time
import threading
import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import markovify

# Global flags to stop typing or force quit
stop_typing = False
force_quit = False

# Function to stop typing
def stop_typing_function():
    global stop_typing
    stop_typing = True

# Function to force quit the program
def force_quit_function():
    global force_quit
    force_quit = True
    exit()

# Function to perform a Google search and get relevant URLs
def search_web(query):
    search_results = []
    for url in search(query, num_results=5):
        search_results.append(url)
    return search_results

# Function to scrape the main text content from a URL
def scrape_web_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract only the main content from the page, removing cookie messages and banners
        paragraphs = soup.find_all('p')
        text_content = " ".join([para.get_text() for para in paragraphs if not "cookie" in para.get_text().lower()])
        
        return text_content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# Function to generate more meaningful text using web scraping and Markov Chain model
def generate_text_from_web_and_scraping(prompt, num_words=100):
    # Perform a web search to get URLs related to the prompt
    search_results = search_web(prompt)
    full_text = ""

    # Scrape text from the first few URLs
    for url in search_results:
        full_text += scrape_web_page(url) + " "

    # Use Markovify to generate coherent sentences from scraped content
    text_model = markovify.Text(full_text)
    generated_text = ""
    for _ in range(num_words // 10):  # Generate several sentences (10 words each)
        sentence = text_model.make_sentence()
        if sentence:
            generated_text += sentence + " "

    return generated_text.strip()

# Function to update the Text widget in the main thread
def update_text_area(text, text_area):
    text_area.insert(tk.END, text + " ")
    text_area.yview(tk.END)  # Scroll to the bottom

# Type generated text with optional typo behavior and dynamic speed
def type_generated_text(text, delay=0.2, text_area=None):
    global stop_typing, force_quit

    # Type the generated text with human-like delays
    word_count = 0
    max_words = 200  # Set a cap of 200 words

    for word in text.split():
        if stop_typing:
            print("Typing stopped by user.")
            messagebox.showinfo("Typing Stopped", "Typing was stopped by the user.")
            return
        if force_quit:
            print("Force quit initiated.")
            return

        pyautogui.write(word + " ", interval=delay)  # Type each word with a delay
        word_count += 1
        
        # Stop if we've typed the maximum number of words
        if word_count >= max_words:
            print(f"Typing stopped. {max_words} words reached.")
            break

        # Update the text area using `root.after` to schedule the update in the main thread
        if text_area:
            text_to_insert = word + " "
            text_area.after(0, update_text_area, text_to_insert, text_area)

# Function to start typing the generated text in a separate thread
def start_typing(prompt, num_words=100, delay=0.2, text_area=None):
    global stop_typing, force_quit
    stop_typing = False
    force_quit = False
    generated_text = generate_text_from_web_and_scraping(prompt, num_words)
    
    # Update the Text Widget with the generated text before typing
    text_area.delete(1.0, tk.END)  # Clear previous text
    text_area.insert(tk.END, generated_text)  # Insert the generated text

    typing_thread = threading.Thread(target=type_generated_text, args=(generated_text, delay, text_area))
    typing_thread.start()

# Function to display and manage the GUI
def create_gui():
    global stop_typing, force_quit

    # Create the root window
    root = tk.Tk()
    root.title("Typing Control")
    root.attributes('-fullscreen', True)  # Full screen mode
    root.configure(bg="#2e2e2e")  # Dark background color

    # Use custom font styles for better appearance
    font_style = ("Helvetica", 12)
    heading_font = ("Helvetica", 16, "bold")

    # Prompt Entry
    tk.Label(root, text="Enter Prompt:", font=heading_font, fg="white", bg="#2e2e2e").pack(pady=5)
    prompt_entry = tk.Entry(root, width=60, font=font_style)
    prompt_entry.pack(pady=5)

    # Typing Delay
    tk.Label(root, text="Typing Delay (seconds):", font=heading_font, fg="white", bg="#2e2e2e").pack(pady=5)
    delay_entry = tk.Entry(root, font=font_style)
    delay_entry.insert(0, "0.2")  # Default to 0.2 seconds
    delay_entry.pack(pady=5)

    # Output Text Field (Text Widget)
    tk.Label(root, text="Generated Text:", font=heading_font, fg="white", bg="#2e2e2e").pack(pady=10)
    text_area = tk.Text(root, height=10, width=60, font=font_style, fg="white", bg="#333333", insertbackground='white')
    text_area.pack(pady=5)

    # Start and Stop Buttons
    start_button = tk.Button(root, text="Start Typing", command=lambda: start_typing(
        prompt_entry.get(),
        100,  # Default to 100 words
        float(delay_entry.get()),
        text_area
    ), font=font_style, bg="#4CAF50", fg="white")
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Typing", command=stop_typing_function, font=font_style, bg="#f44336", fg="white")
    stop_button.pack(pady=10)

    force_quit_button = tk.Button(root, text="Force Quit", command=force_quit_function, font=font_style, bg="#FF5722", fg="white")
    force_quit_button.pack(pady=10)

    # Run the main loop
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
