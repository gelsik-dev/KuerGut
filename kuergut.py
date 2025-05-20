# If you put this = RaInBoW!
# abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?¿¡:;@#$%&()[]{}+-*/=<>_~`|•√π÷×§∆£¥$¢^°=©®™✓áéíóúüñÁÉÍÓÚÜÑ

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageDraw, ImageTk, PngImagePlugin
import colorsys, math, os

# Character...
ALL_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n\t.,!?¿¡:;@#$%&()[]{}+-*/=<>_~`|•√π÷×§∆£¥$¢^°=©®™✓\"'áéíóúüñÁÉÍÓÚÜÑ"
CELL_SIZE = 100
BLOCK_SIZE = 1
MAX_CHARS = 100000


def center_window(win, width=960, height=720):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def generate_colors(n):
    colors = []
    for i in range(n):
        h = i / n
        r, g, b = colorsys.hls_to_rgb(h, 0.5, 0.8)
        colors.append(
            "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
        )
    return colors


char_list = list(ALL_CHARS)
char_to_color = dict(zip(char_list, generate_colors(len(char_list))))
color_to_char = {
    Image.new("RGB", (1, 1), v).getpixel((0, 0)): k for k, v in char_to_color.items()
}


def draw_text_grid(text):
    global CELL_SIZE, BLOCK_SIZE
    text = text[:MAX_CHARS]
    total_chars = len(text)
    if total_chars == 0:
        return Image.new("RGB", (10, 10), "black"), 1, 1
    grid_size = (
        math.ceil(math.sqrt(total_chars / (BLOCK_SIZE * BLOCK_SIZE))) * BLOCK_SIZE
    )
    cols = rows = max(grid_size, 1)
    img = Image.new("RGB", (cols * CELL_SIZE, rows * CELL_SIZE), "black")
    draw = ImageDraw.Draw(img)

    for idx, char in enumerate(text):
        x = (idx % cols) * CELL_SIZE
        y = (idx // cols) * CELL_SIZE
        color = "white" if char == " " else char_to_color.get(char, "#000001")
        draw.rectangle([x, y, x + CELL_SIZE, y + CELL_SIZE], fill=color)

    return img, cols, rows


def set_status(text, delay=3000):
    status_var.set(text)
    if delay:
        root.after(delay, lambda: status_var.set("Ready."))


def update_image(event=None):
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        left_panel.pack_forget()
        return
    if not left_panel.winfo_ismapped():
        left_panel.pack(side="left", fill="both", expand=True, padx=10)
    set_status("Generating...")
    img, _, _ = draw_text_grid(text)
    img_label.original = img
    resized = img.resize((480, int(img.height * (480 / img.width))))
    tk_img = ImageTk.PhotoImage(resized)
    img_label.config(image=tk_img)
    img_label.image = tk_img
    result_text.set(text)
    set_status("Updated.")


def save_image():
    if not hasattr(img_label, "original"):
        messagebox.showerror("Error", "No image to save.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".png", filetypes=[("PNG", "*.png")]
    )
    if path:
        try:
            set_status("Saving...")
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Author", "Gelsik ©")
            img_label.original.save(path, pnginfo=meta)
            set_status("Saved.")
            messagebox.showinfo(
                "Saved",
                "Code image saved.\n\n⚠️ Result may vary depending on Cell/Block Size configuration.\nContact the code distributor for more info.",
            )
        except Exception as e:
            set_status("Save error")
            messagebox.showerror("Error", str(e))


def import_image():
    path = filedialog.askopenfilename(filetypes=[("Images", "*.png")])
    if not path:
        return
    try:
        set_status("Importing...")
        img = Image.open(path)
        if img.info.get("Author") != "Gelsik ©":
            set_status("No metadata.")
            messagebox.showerror("Invalid", "Missing Gelsik © metadata.")
            return
        width, height = img.size
        cols = width // CELL_SIZE
        rows = height // CELL_SIZE
        pixels = img.load()
        result = ""

        for y in range(rows):
            for x in range(cols):
                px = x * CELL_SIZE + CELL_SIZE // 2
                py = y * CELL_SIZE + CELL_SIZE // 2
                if px >= width or py >= height:
                    continue
                color = pixels[px, py]
                if color == (255, 255, 255):
                    result += " "
                else:
                    char = color_to_char.get(color)
                    if char:
                        result += char

        result_text.set(result)
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", result)
        root.after(100, update_image)
        set_status("Imported.")
        messagebox.showinfo(
            "Success",
            "Code loaded.\n\n⚠️ Result may vary depending on Cell/Block Size configuration.\nContact the code distributor for more info.",
        )
    except Exception as e:
        set_status("Import error")
        messagebox.showerror("Error", str(e))


def copy_text():
    root.clipboard_clear()
    root.clipboard_append(result_text.get())
    set_status("Copied.")
    messagebox.showinfo("Copied", "Text copied to clipboard.")


def clear_text():
    text_box.delete("1.0", tk.END)
    result_text.set("")
    img_label.config(image="")
    img_label.image = None
    if left_panel.winfo_ismapped():
        left_panel.pack_forget()
    set_status("Reset.")


def update_params(*args):
    global CELL_SIZE, BLOCK_SIZE
    try:
        new_cell = int(cell_size_var.get())
        new_block = int(block_size_var.get())

        if new_cell > 100:
            new_cell = 100
            cell_size_var.set("100")
            set_status("Max cell size is 100.")
        if new_block > 100:
            new_block = 100
            block_size_var.set("100")
            set_status("Max block size is 100.")

        CELL_SIZE = new_cell
        BLOCK_SIZE = new_block
        update_image()
    except:
        set_status("Parameter error")


def reset_params():
    cell_size_var.set("100")
    block_size_var.set("1")
    set_status("Parameters reset.")


root = tk.Tk()
root.title("KuerGut - Visual Encoder")
center_window(root)

if os.path.exists("_internal/icon.ico"):
    root.iconbitmap("_internal/icon.ico")

root.configure(bg="#1e1e1e")

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(padx=20, pady=20, fill="both", expand=True)


title_img = Image.open("_internal/icon.png")
title_img = title_img.resize((600, 150), Image.Resampling.LANCZOS)
title_photo = ImageTk.PhotoImage(title_img)
title_label = tk.Label(main_frame, image=title_photo, bg="#1e1e1e")
title_label.image = title_photo
title_label.pack(pady=(0, 5))
tk.Label(
    main_frame,
    text="Visual encoder by Gelsik © - Version 1.2.6",
    font=("Segoe UI", 10),
    fg="#cccccc",
    bg="#1e1e1e",
).pack()

param_frame = tk.Frame(main_frame, bg="#1e1e1e")
param_frame.pack(pady=10)
tk.Label(param_frame, text="Cell Size:", bg="#1e1e1e", fg="white").grid(row=0, column=0)
cell_size_var = tk.StringVar(value=str(CELL_SIZE))
tk.Entry(param_frame, textvariable=cell_size_var, width=4).grid(
    row=0, column=1, padx=10
)
tk.Label(param_frame, text="Block Size:", bg="#1e1e1e", fg="white").grid(
    row=0, column=2
)
block_size_var = tk.StringVar(value=str(BLOCK_SIZE))
tk.Entry(param_frame, textvariable=block_size_var, width=4).grid(
    row=0, column=3, padx=10
)
tk.Button(
    param_frame, text="Reset Values", command=reset_params, bg="#ff9800", fg="white"
).grid(row=0, column=4, padx=10)

cell_size_var.trace_add("write", update_params)
block_size_var.trace_add("write", update_params)

container = tk.Frame(main_frame, bg="#1e1e1e")
container.pack(fill="both", expand=True, pady=10)

left_panel = tk.Frame(container, bg="#121212", bd=1, relief="groove")
img_label = tk.Label(left_panel, bg="#121212")
img_label.pack(padx=10, pady=10)

right_panel = tk.Frame(container, bg="#eeeeee")
right_panel.pack(side="right", fill="both", expand=True)

tk.Label(
    right_panel,
    text="Write text to encode",
    font=("Segoe UI", 12, "bold"),
    bg="#eeeeee",
).pack(pady=(10, 5))

text_box = scrolledtext.ScrolledText(
    right_panel, height=10, font=("Segoe UI", 12), wrap="word", bg="white"
)
text_box.pack(fill="both", expand=True, padx=10, pady=5)
text_box.bind("<KeyRelease>", update_image)

result_text = tk.StringVar()
tk.Button(
    right_panel, text="Copy Text", command=copy_text, bg="#4caf50", fg="white"
).pack(pady=5)

button_bar = tk.Frame(main_frame, bg="#1e1e1e")
button_bar.pack(pady=10)
tk.Button(
    button_bar, text="Save Code", command=save_image, bg="#4caf50", fg="white", width=12
).pack(side="left", padx=5)
tk.Button(
    button_bar,
    text="Import Image",
    command=import_image,
    bg="#2196f3",
    fg="white",
    width=12,
).pack(side="left", padx=5)
tk.Button(
    button_bar, text="Clear", command=clear_text, bg="#f44336", fg="white", width=12
).pack(side="left", padx=5)

status_var = tk.StringVar(value="Ready.")
tk.Label(
    root, textvariable=status_var, bg="#1e1e1e", fg="white", font=("Segoe UI", 10)
).pack(side="bottom", pady=5)

root.mainloop()
