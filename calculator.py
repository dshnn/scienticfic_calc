import ast
import math
import operator
import tkinter as tk
from tkinter import messagebox

# Scientific Calculator - Python Tkinter
# Safe expression evaluator: no eval() or arbitrary code execution.

class SafeCalculator:
    BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }
    UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    FUNCTIONS = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "abs": abs, "floor": math.floor, "ceil": math.ceil,
        "factorial": math.factorial,
    }
    CONSTANTS = {"pi": math.pi, "e": math.e}

    def __init__(self, angle_mode="DEG"):
        self.angle_mode = angle_mode

    def evaluate(self, expression):
        expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        tree = ast.parse(expression, mode="eval")
        result = self._visit(tree.body)
        if isinstance(result, complex):
            raise ValueError("Complex results are not supported")
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not finite")
        return result

    def _visit(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.CONSTANTS:
                return self.CONSTANTS[node.id]
            raise ValueError(f"Unknown value: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in self.BIN_OPS:
            left, right = self._visit(node.left), self._visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large")
            return self.BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in self.UNARY_OPS:
            return self.UNARY_OPS[type(node.op)](self._visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.FUNCTIONS or len(node.args) != 1 or node.keywords:
                raise ValueError("Unsupported function")
            value = self._visit(node.args[0])
            if name in ("sin", "cos", "tan") and self.angle_mode == "DEG":
                value = math.radians(value)
            elif name in ("asin", "acos", "atan") and self.angle_mode == "DEG":
                result = self.FUNCTIONS[name](value)
                return math.degrees(result)
            if name == "factorial":
                if value < 0 or int(value) != value or value > 170:
                    raise ValueError("Factorial requires an integer from 0 to 170")
                return math.factorial(int(value))
            return self.FUNCTIONS[name](value)
        raise ValueError("Invalid expression")


class ScientificCalculatorApp:
    BG = "#101827"
    PANEL = "#172235"
    DISPLAY = "#0b1220"
    TEXT = "#f1f5f9"
    MUTED = "#94a3b8"
    BLUE = "#2563eb"
    TEAL = "#0f766e"
    BUTTON = "#243248"
    BUTTON_ALT = "#334155"
    RED = "#b91c1c"

    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("460x690")
        self.root.minsize(420, 620)
        self.root.configure(bg=self.BG)
        self.expression = tk.StringVar()
        self.answer = tk.StringVar(value="Ready")
        self.angle_mode = tk.StringVar(value="DEG")
        self.engine = SafeCalculator()
        self.just_calculated = False
        self._build_ui()
        self.root.bind("<Key>", self._on_key)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG, padx=20, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="SCIENTIFIC CALCULATOR", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Python • Mathematics • Precision", bg=self.BG,
                 fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        display = tk.Frame(self.root, bg=self.DISPLAY, padx=16, pady=14)
        display.pack(fill="x", padx=16, pady=(0, 12))
        mode_row = tk.Frame(display, bg=self.DISPLAY)
        mode_row.pack(fill="x")
        tk.Label(mode_row, text="ANGLE MODE", bg=self.DISPLAY, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        self.mode_button = tk.Button(mode_row, textvariable=self.angle_mode,
                 command=self._toggle_mode, bg=self.TEAL, fg="white", relief="flat",
                 activebackground=self.TEAL, activeforeground="white",
                 font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2")
        self.mode_button.pack(side="right")
        tk.Entry(display, textvariable=self.expression, bg=self.DISPLAY, fg=self.TEXT,
                 insertbackground=self.TEXT, relief="flat", justify="right",
                 font=("Consolas", 23), state="normal").pack(fill="x", pady=(14, 8), ipady=6)
        tk.Label(display, textvariable=self.answer, bg=self.DISPLAY, fg="#38bdf8",
                 anchor="e", font=("Segoe UI", 12, "bold")).pack(fill="x")

        grid = tk.Frame(self.root, bg=self.BG, padx=16, pady=2)
        grid.pack(fill="both", expand=True)
        buttons = [
            [("sin", "fn"), ("cos", "fn"), ("tan", "fn"), ("(", "fn"), (")", "fn")],
            [("asin", "fn"), ("acos", "fn"), ("atan", "fn"), ("π", "fn"), ("e", "fn")],
            [("√", "fn"), ("x²", "fn"), ("xʸ", "fn"), ("log", "fn"), ("ln", "fn")],
            [("n!", "fn"), ("abs", "fn"), ("floor", "fn"), ("ceil", "fn"), ("mod", "op")],
            [("AC", "clear"), ("DEL", "delete"), ("%", "op"), ("÷", "op"), ("×", "op")],
            [("7", "num"), ("8", "num"), ("9", "num"), ("−", "op"), ("+", "op")],
            [("4", "num"), ("5", "num"), ("6", "num"), ("1/x", "fn"), ("±", "fn")],
            [("1", "num"), ("2", "num"), ("3", "num"), (".", "num"), ("=", "equals")],
            [("0", "num"), ("00", "num"), ("Ans", "fn"), ("⌫", "delete"), ("=", "equals")],
        ]
        for r, row in enumerate(buttons):
            grid.grid_rowconfigure(r, weight=1, uniform="row")
            for c, (label, kind) in enumerate(row):
                grid.grid_columnconfigure(c, weight=1, uniform="col")
                # Hide the final duplicate equals cell in the last row by making it a history hint button.
                if r == 8 and c == 4:
                    label, kind = ("History", "history")
                color = self._button_color(kind)
                btn = tk.Button(grid, text=label, command=lambda x=label: self._press(x),
                    bg=color, fg=self.TEXT, activebackground=color, activeforeground="white",
                    relief="flat", bd=0, font=("Segoe UI", 10 if len(label) > 3 else 12, "bold"),
                    cursor="hand2", padx=2, pady=10)
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

        footer = tk.Label(self.root, text="Enter = calculate   •   Esc = clear   •   Backspace = delete",
                          bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8), pady=8)
        footer.pack(fill="x")

    def _button_color(self, kind):
        return {
            "fn": self.BUTTON_ALT, "num": self.BUTTON, "op": self.BLUE,
            "clear": self.RED, "delete": "#7f1d1d", "equals": self.TEAL,
            "history": self.PANEL,
        }.get(kind, self.BUTTON)

    def _toggle_mode(self):
        self.angle_mode.set("RAD" if self.angle_mode.get() == "DEG" else "DEG")
        self.engine.angle_mode = self.angle_mode.get()

    def _press(self, key):
        current = self.expression.get()
        if key == "AC":
            self.expression.set("")
            self.answer.set("Ready")
            self.just_calculated = False
            return
        if key in ("DEL", "⌫"):
            self.expression.set(current[:-1])
            return
        if key == "History":
            messagebox.showinfo("History", "Calculation history is not saved in this version.")
            return
        if key == "=":
            self._calculate()
            return
        if key == "π":
            insert = "pi"
        elif key == "√":
            insert = "sqrt("
        elif key == "x²":
            insert = "**2"
        elif key == "xʸ":
            insert = "^"
        elif key == "n!":
            insert = "factorial("
        elif key == "mod":
            insert = "%"
        elif key == "÷":
            insert = "/"
        elif key == "×":
            insert = "*"
        elif key == "−":
            insert = "-"
        elif key == "1/x":
            self.expression.set(f"1/({current})" if current else "1/(")
            return
        elif key == "±":
            self.expression.set(f"-({current})" if current else "-")
            return
        elif key == "Ans":
            prior = self.answer.get()
            if prior not in ("Ready", "Error"):
                insert = prior
            else:
                return
        elif key == "%":
            insert = "/100"
        elif key in ("sin", "cos", "tan", "asin", "acos", "atan", "log", "ln", "abs", "floor", "ceil"):
            insert = key + "("
        else:
            insert = key
        if self.just_calculated and (insert[0].isdigit() or insert in ("pi", "e", "sqrt(")):
            self.expression.set("")
        self.just_calculated = False
        self.expression.set(self.expression.get() + insert)

    def _calculate(self):
        expression = self.expression.get().strip()
        if not expression:
            return
        self.engine.angle_mode = self.angle_mode.get()
        try:
            result = self.engine.evaluate(expression)
            if isinstance(result, float):
                display_result = f"{result:.12g}"
            else:
                display_result = str(result)
            self.answer.set(display_result)
            self.just_calculated = True
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, TypeError) as exc:
            self.answer.set("Error")
            messagebox.showerror("Calculation error", str(exc) or "Please check your expression.")

    def _on_key(self, event):
        if event.keysym == "Return":
            self._calculate()
            return "break"
        if event.keysym == "Escape":
            self._press("AC")
            return "break"
        if event.keysym == "BackSpace":
            self._press("DEL")
            return "break"


if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculatorApp(root)
    root.mainloop()
