import customtkinter
from typing import List, Tuple
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CATEGORICAL_STYLES = ["Bar", "Horizontal Bar", "Pie"]
SERIES_STYLES      = ["Histogram", "Line"]
GROUPS_STYLES      = ["Boxplot"]

class ChartsFrame(customtkinter.CTkFrame):
    def __init__(self, master, presenter, width=800, height=520):
        super().__init__(master, width=width, height=height, corner_radius=12)
        self.presenter = presenter
        self.pack_propagate(False)

        header = customtkinter.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(8, 4), padx=12)

        title = customtkinter.CTkLabel(header, text="Charts", font=("Arial", 24, "bold"))
        title.pack(side="left")

        self.chart_selector = customtkinter.CTkOptionMenu(
            header, values=self.presenter.get_chart_types(),
            width=320, dynamic_resizing=True, command=self._on_selector_change
        )
        self.chart_selector.set(self.presenter.get_chart_types()[0])
        self.chart_selector.pack(side="left", padx=(12, 0))

        self.style_selector = customtkinter.CTkOptionMenu(
            header, values=CATEGORICAL_STYLES,
            width=200, dynamic_resizing=True, command=lambda _=None: self.render_chart()
        )
        self.style_selector.set("Bar")
        self.style_selector.pack(side="right")

        self.canvas_frame = customtkinter.CTkFrame(self, corner_radius=8)
        self.canvas_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.figure = Figure(figsize=(7.5, 4.8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.render_chart()

    def _on_selector_change(self, _):
        payload = self.presenter.get_chart_payload(self.chart_selector.get())
        t = payload.get("type", "categorical")
        if t == "categorical":
            styles = CATEGORICAL_STYLES; default = "Bar"
        elif t == "series":
            styles = SERIES_STYLES; default = "Histogram"
        else:
            styles = GROUPS_STYLES; default = styles[0]
        self.style_selector.configure(values=styles)
        self.style_selector.set(default)
        self.render_chart()

    def render_chart(self):
        payload = self.presenter.get_chart_payload(self.chart_selector.get())
        t = payload.get("type", "categorical")
        style = self.style_selector.get()
        self.ax.clear()

        if t == "categorical":
            labels = payload["labels"]; values = payload["values"]; xs = range(len(labels))
            if style == "Bar":
                self.ax.bar(xs, values); self._xticks(labels)
            elif style == "Horizontal Bar":
                self.ax.barh(xs, values); self.ax.set_yticks(list(xs)); self.ax.set_yticklabels(labels)
            elif style == "Pie":
                total = sum(values)
                if total <= 0:
                    self.ax.text(0.5, 0.5, "No data", ha="center", va="center")
                else:
                    self.ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90); self.ax.axis("equal")
            self.ax.set_title(payload.get("title", ""))
            if style != "Pie":
                self.ax.set_ylabel(payload.get("ylabel", ""))
                self.ax.grid(True, axis=("y" if style != "Horizontal Bar" else "x"), alpha=0.3)

        elif t == "series":
            series = payload["series"]
            if not series:
                self.ax.text(0.5, 0.5, "No data", ha="center", va="center")
            else:
                if style == "Histogram":
                    self.ax.hist(series, bins=min(10, max(5, int(len(series) ** 0.5))))
                    self.ax.set_ylabel("Frecvență"); self.ax.grid(True, axis="y", alpha=0.3)
                elif style == "Line":
                    self.ax.plot(series, marker="o"); self.ax.set_ylabel(payload.get("ylabel", "")); self.ax.grid(True, alpha=0.3)
            self.ax.set_title(payload.get("title", ""))

        else:
            groups: List[Tuple[str, List[float]]] = payload["groups"]
            if not groups:
                self.ax.text(0.5, 0.5, "No data", ha="center", va="center")
            else:
                labels = [g[0] for g in groups]; data = [g[1] for g in groups]
                self.ax.boxplot(data, labels=labels, showmeans=True)
                self.ax.set_ylabel(payload.get("ylabel", "")); self.ax.grid(True, axis="y", alpha=0.3)
            self.ax.set_title(payload.get("title", ""))

        self.figure.tight_layout()
        self.canvas.draw()

    def _xticks(self, labels):
        xs = range(len(labels))
        self.ax.set_xticks(xs)
        self.ax.set_xticklabels(labels, rotation=20, ha="right")
