import tkinter as tk

# Function to handle button click event
def submit_url():
    global youtube_url
    global output_mp4
    youtube_url = url_entry.get()
    output_mp4 = url_entry.get()
    print("Entered URL:", youtube_url)

    # display the entered URL
    url_label.config(text="Entered URL: " + youtube_url)

# Create the main window
root = tk.Tk()
root.title("URL Entry App")
root.minsize(width=250, height=400)

# Title
label = tk.Label(root, text="Extract the most popular part of a Youtube Video", font=("Arial", 16))
label.pack(pady=0)
label = tk.Label(root, text="Warning: This is only applys to videos that have the 'most replayed' activated", font=("Arial", 10), fg="red")
label.pack(pady=5)

# Create a label and input boxes
label = tk.Label(root, text="Enter the entire YouTube video URL: ", font=("Arial", 10))
label.pack(pady=10)
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=10)

label = tk.Label(root, text="Enter the desired name for the new video: ", font=("Arial", 10))
label.pack(pady=10)
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=10)

# Create a button to submit the URL
submit_button = tk.Button(root, text="Submit", command=submit_url)
submit_button.pack(pady=10)

# Initialize the youtube_url variable
youtube_url = ""
output_mp4 = ""

# Create a label to display the entered URL
url_label = tk.Label(root, text="", font=("Arial", 12))
url_label.pack(pady=10)

# Start the event loop
root.mainloop()

# Now you can access the entered URL using the youtube_url variable.
print("Saved URL:", youtube_url)
