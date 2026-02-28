	def _init_(self):
		super()._init_()
		self.title("Modern Calculator")
		self.resizable(False, False)
		self._create_styles()
		self.memory = 0.0
		self.history = []
		self._build_ui()
		self._bind_keys()

	def _create_styles(self):
		self.style = ttk.Style(self)
		# Basic color themes
		self.themes = {
			"light": {
				"bg": "#f3f4f6",
				"fg": "#0f172a",
				"button_bg": "#ffffff",
				"accent": "#2563eb",
			},
			"dark": {
				"bg": "#0b1220",
				"fg": "#e6eef8",
				"button_bg": "#111827",
				"accent": "#60a5fa",
			},
		}
		self.current_theme = "dark"

	def _build_ui(self):
		t = self.themes[self.current_theme]
		self.configure(bg=t["bg"]) 

		main = ttk.Frame(self, padding=12)
		main.grid(row=0, column=0)

		# Display
		self.display_var = tk.StringVar()
		display_font = font.Font(size=24, weight="bold")
		self.display = tk.Entry(main, textvariable=self.display_var, font=display_font,
								justify="right", bd=0, relief="flat", width=18)
		self.display.grid(row=0, column=0, columnspan=5, pady=(0, 8))

		# Memory and history area
		mem_frame = ttk.Frame(main)
		mem_frame.grid(row=1, column=0, columnspan=5, sticky="ew")
		self.mem_label = ttk.Label(mem_frame, text="M: 0")
		self.mem_label.pack(side="left")
		self.theme_btn = ttk.Button(mem_frame, text="Toggle Theme", command=self._toggle_theme)
		self.theme_btn.pack(side="right")

		# Buttons layout
		buttons = [
			("MC", self.mem_clear), ("MR", self.mem_recall), ("M+", self.mem_add), ("M-", self.mem_sub), ("<-", self.backspace),
			("7", lambda: self._append("7")), ("8", lambda: self._append("8")), ("9", lambda: self._append("9")), ("/", lambda: self._append("/")), ("%", self.percent),
			("4", lambda: self._append("4")), ("5", lambda: self._append("5")), ("6", lambda: self._append("6")), ("", lambda: self._append("")), ("(", lambda: self._append("(")),
			("1", lambda: self._append("1")), ("2", lambda: self._append("2")), ("3", lambda: self._append("3")), ("-", lambda: self._append("-")), (")", lambda: self._append(")")),
			("0", lambda: self._append("0")), (".", lambda: self._append(".")), ("C", self.clear), ("+", lambda: self._append("+")), ("=", self.evaluate),
		]

		r = 2
		c = 0
		for (text, cmd) in buttons:
			btn = ttk.Button(main, text=text, command=cmd)
			btn.grid(row=r, column=c, ipadx=6, ipady=10, padx=4, pady=4, sticky="nsew")
			c += 1
			if c > 4:
				c = 0
				r += 1

		# History listbox
		hist_frame = ttk.Frame(self, padding=(0, 12, 12, 12))
		hist_frame.grid(row=0, column=1, sticky="ns")
		ttk.Label(hist_frame, text="History").pack(anchor="w")
		self.hist_list = tk.Listbox(hist_frame, height=12, width=24)
		self.hist_list.pack()
		self.hist_list.bind("<<ListboxSelect>>", self._on_history_select)

		self._apply_theme()

	# ---------- Actions ----------
	def _append(self, s: str):
		self.display_var.set(self.display_var.get() + s)

	def clear(self):
		self.display_var.set("")

	def backspace(self):
		self.display_var.set(self.display_var.get()[:-1])

	def percent(self):
		expr = self.display_var.get()
		if not expr:
			return

		new_expr = re.sub(r"(\d+(?:\.\d*)?)$", lambda m: str(float(m.group(1)) / 100), expr)
		self.display_var.set(new_expr)

	def evaluate(self):
		expr = self.display_var.get()
		if not expr:
			return
		expr = expr.replace("×", "").replace("÷", "/").replace("^", "*")
		# Only allow safe characters
		if not re.fullmatch(r"[0-9+\-/().%\s]", expr):
			self.display_var.set("ERROR")
			return
		try:
			# Evaluate safely using Python's eval since we've sanitized the input characters
			result = eval(expr)
			self.display_var.set(str(result))
			self._add_history(expr + " = " + str(result))
		except Exception:
			self.display_var.set("ERROR")

	# ---------- Memory ----------
	def mem_clear(self):
		self.memory = 0.0
		self._update_mem_label()

	def mem_recall(self):
		self.display_var.set(self.display_var.get() + str(self.memory))

	def mem_add(self):
		try:
			v = float(self.display_var.get())
			self.memory += v
			self._update_mem_label()
		except Exception:
			pass

	def mem_sub(self):
		try:
			v = float(self.display_var.get())
			self.memory -= v
			self._update_mem_label()
		except Exception:
			pass

	def _update_mem_label(self):
		self.mem_label.config(text=f"M: {self.memory}")

	# ---------- History ----------
	def _add_history(self, text: str):
		self.history.insert(0, text)
		if len(self.history) > 50:
			self.history.pop()
		self._refresh_history()

	def _refresh_history(self):
		self.hist_list.delete(0, tk.END)
		for item in self.history:
			self.hist_list.insert(tk.END, item)

	def _on_history_select(self, event):
		sel = event.widget.curselection()
		if not sel:
			return
		value = event.widget.get(sel[0])
		# take the result part after =
		if "=" in value:
			res = value.split("=")[-1].strip()
			self.display_var.set(res)

	# ---------- Theming ----------
	def _toggle_theme(self):
		self.current_theme = "light" if self.current_theme == "dark" else "dark"
		self._apply_theme()

	def _apply_theme(self):
		t = self.themes[self.current_theme]
		self.configure(bg=t["bg"]) 
		self.display.config(bg=t["button_bg"], fg=t["fg"], insertbackground=t["fg"]) 
		self.hist_list.config(bg=t["button_bg"], fg=t["fg"]) 
		self.mem_label.config(background=t["bg"], foreground=t["fg"]) 

	# ---------- Keyboard ----------
	def _bind_keys(self):
		self.bind("<Return>", lambda e: self.evaluate())
		self.bind("<BackSpace>", lambda e: self.backspace())
		self.bind("<Escape>", lambda e: self.clear())
		for k in "0123456789.+-*/()%":
			self.bind(k, lambda e, ch=k: self._append(ch))


if _name_ == "_main_":
	app = ModernCalculator()
	app.mainloop()

print("hello")