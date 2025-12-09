import customtkinter
from functools import partial
from view.charts_view import ChartsFrame

class SchoolView(customtkinter.CTk):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.presenter.set_view(self)

        self.geometry("1120x700")
        self.title("School Management System")
        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("blue")

        self.selected = set()           # (person_type, id)
        self.checkbox_widgets = {}
        self.input_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ----- LEFT -----
        self.left_frame = customtkinter.CTkFrame(self.main_frame, width=560)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        self.left_frame.pack_propagate(False)

        header = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        header.pack(fill="x", pady=(10, 0))
        self.header = customtkinter.CTkLabel(header, text="School Management", font=("Arial", 28, "bold"))
        self.header.pack(side="left", padx=10)

        # Sort controls (fără “Role”)
        sortbar = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        sortbar.pack(fill="x", pady=(6, 0), padx=14)
        customtkinter.CTkLabel(sortbar, text="Sort:", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
        self.sort_menu = customtkinter.CTkOptionMenu(
            sortbar,
            values=self.presenter.get_sort_options(),
            command=self.on_sort_changed,
            width=220
        )
        self.sort_menu.set("Name")
        self.sort_menu.pack(side="left")

        self.data_type_label = customtkinter.CTkLabel(self.left_frame, text="Select Type:", font=("Arial", 16))
        self.data_type_label.pack(pady=(10, 0))

        self.data_type = customtkinter.CTkOptionMenu(self.left_frame, values=["Teacher", "Student", "Assistant"], command=self.on_type_changed)
        self.data_type.pack(pady=5)

        self.inputs_frame = customtkinter.CTkFrame(self.left_frame, corner_radius=15)
        self.inputs_frame.pack(pady=10, padx=20, fill="x")
        self.create_inputs("Teacher")

        self.button_frame = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.add_btn = customtkinter.CTkButton(self.button_frame, text="Add", command=self.on_add_clicked, width=120)
        self.add_btn.grid(row=0, column=0, padx=8)

        self.save_btn = customtkinter.CTkButton(self.button_frame, text="Save", command=self.on_save_clicked, width=120)
        self.save_btn.grid(row=0, column=1, padx=8)

        self.view_btn = customtkinter.CTkButton(self.button_frame, text="View All", command=self.on_view_clicked, width=120)
        self.view_btn.grid(row=0, column=2, padx=8)

        # Charts în loc de “Edit Selected (1)”
        self.actions_frame = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        self.actions_frame.pack(pady=(6, 10))
        self.charts_btn = customtkinter.CTkButton(self.actions_frame, text="Charts", command=self.on_charts_clicked, width=160)
        self.charts_btn.grid(row=0, column=0, padx=6)

        self.bulk_delete_btn = customtkinter.CTkButton(self.actions_frame, text="Delete Selected",
                                                       command=self.on_delete_selected, width=160,
                                                       fg_color="#ef4444", hover_color="#f97373")
        self.bulk_delete_btn.grid(row=0, column=1, padx=6)

        # --- View All output (LEFT BOTTOM) ---
        self.viewall_frame = customtkinter.CTkFrame(self.left_frame, corner_radius=12)
        self.viewall_frame.pack(padx=20, pady=(4, 10), fill="x")

        self.viewall_label = customtkinter.CTkLabel(self.viewall_frame, text="View All Output", font=("Arial", 12, "bold"))
        self.viewall_label.pack(anchor="w", padx=10, pady=(8, 4))

        self.viewall_box = customtkinter.CTkTextbox(self.viewall_frame, width=520, height=160, wrap="word")
        self.viewall_box.pack(padx=10, pady=(0, 10), fill="x")
        self.viewall_box.configure(state="disabled")

        # ----- RIGHT -----
        self.right_frame = customtkinter.CTkFrame(self.main_frame, width=520, corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)
        self.right_frame.pack_propagate(False)

        topbar = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        topbar.pack(fill="x", pady=(8, 0), padx=10)

        self.listbox_label = customtkinter.CTkLabel(topbar, text="Records", font=("Arial", 16, "bold"))
        self.listbox_label.pack(side="left")

        self.status_label = customtkinter.CTkLabel(topbar, text="", font=("Arial", 11))
        self.status_label.pack(side="right")

        self.dbbar = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        self.dbbar.pack(fill="x", padx=10, pady=(6, 6))
        try:
            db_path = self.presenter.get_db_path()
        except Exception:
            db_path = ""
        self.db_label = customtkinter.CTkLabel(self.dbbar, text=f"DB: {db_path}", font=("Consolas", 10))
        self.db_label.pack(side="left")
        self.reload_btn = customtkinter.CTkButton(self.dbbar, text="Reload from DB", width=130, command=self.render_cards)
        self.reload_btn.pack(side="right", padx=(6, 0))

        self.selectbar = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        self.selectbar.pack(fill="x", padx=10)
        self.select_all_btn = customtkinter.CTkButton(self.selectbar, text="Select All", width=100, command=self.on_select_all)
        self.select_all_btn.pack(side="left", padx=(0, 6))
        self.clear_sel_btn = customtkinter.CTkButton(self.selectbar, text="Clear Selection", width=130, command=self.on_clear_selection)
        self.clear_sel_btn.pack(side="left", padx=6)

        self.cards_frame = customtkinter.CTkScrollableFrame(self.right_frame, width=480, height=540)
        self.cards_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.render_cards()

    # -------- helpers --------
    def _set_viewall_text(self, text: str):
        self.viewall_box.configure(state="normal")
        self.viewall_box.delete("1.0", "end")
        self.viewall_box.insert("1.0", text or "")
        self.viewall_box.configure(state="disabled")

    def show_message(self, message):
        try:
            self.status_label.configure(text=message)
        except Exception:
            pass
        print(message)

    # -------- inputs --------
    def create_inputs(self, person_type):
        for w in self.inputs_frame.winfo_children():
            w.destroy()
        self.input_widgets.clear()
        fields = self.presenter.get_field_definitions(person_type)
        for field in fields:
            label = customtkinter.CTkLabel(self.inputs_frame, text=field[0]+":", font=("Arial", 13))
            label.pack(pady=(8, 0), anchor="w", padx=10)
            if field[1] == "entry":
                entry = customtkinter.CTkEntry(self.inputs_frame, placeholder_text=f"Enter {field[0]}", width=420)
                entry.pack(pady=2, padx=10)
                self.input_widgets[field[0]] = entry
            elif field[1] == "optionmenu":
                option = customtkinter.CTkOptionMenu(self.inputs_frame, values=field[2], width=420)
                option.pack(pady=2, padx=10)
                self.input_widgets[field[0]] = option

    def get_input_values(self):
        values = {}
        for field, widget in self.input_widgets.items():
            if isinstance(widget, customtkinter.CTkEntry):
                values[field] = widget.get()
            elif isinstance(widget, customtkinter.CTkOptionMenu):
                values[field] = widget.get()
        return values

    def clear_inputs(self):
        for widget in self.input_widgets.values():
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, "end")

    # -------- cards --------
    def clear_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.checkbox_widgets.clear()

    def render_cards(self):
        self.clear_cards()
        try:
            snap = self.presenter._snapshot()
        except Exception as e:
            self.show_message(f"Reload error: {e}")
            return

        for person_type, objs in snap.items():
            if not objs:
                continue
            header = customtkinter.CTkLabel(self.cards_frame, text=f"— {person_type}s —", font=("Arial", 14, "bold"))
            header.pack(anchor="w", padx=8, pady=(12, 6))

            for obj in objs:
                row = customtkinter.CTkFrame(self.cards_frame, fg_color="transparent")
                row.pack(fill="x", pady=6, padx=6)

                key = (person_type, getattr(obj, "id", ""))
                var = customtkinter.StringVar(value="1" if key in self.selected else "0")
                chk = customtkinter.CTkCheckBox(row, text="", variable=var, width=24, command=partial(self._on_toggle_select, key, var))
                chk.pack(side="left", padx=(2, 6))
                self.checkbox_widgets[key] = chk

                card = customtkinter.CTkFrame(row, corner_radius=8, fg_color="#2f2f2f")
                card.pack(side="left", fill="x", expand=True, padx=(0, 8))

                name = getattr(obj, "name", ""); idv = getattr(obj, "id", "")
                grade = getattr(obj, "grade", ""); speciality = getattr(obj, "speciality", "")
                salary = getattr(obj, "salary", ""); department = getattr(obj, "department", ""); subject = getattr(obj, "subject", "")

                line1 = customtkinter.CTkLabel(card, text=f"{name}  •  ID: {idv}", font=("Arial", 13, "bold"))
                line1.pack(anchor="w", padx=10, pady=(8, 0))

                sort_label = self.sort_menu.get()
                if sort_label == "Grade" and grade != "":
                    extra = f"Grade={grade}"
                elif sort_label == "Salary" and salary != "":
                    extra = f"Salary={salary}"
                else:
                    extra = f"{'Grade='+str(grade) if grade!='' else 'Salary='+str(salary)}"

                right_ctx = speciality or department or subject
                line2 = customtkinter.CTkLabel(card, text=f"{extra}   |   {right_ctx}", font=("Consolas", 12))
                line2.pack(anchor="w", padx=10, pady=(4, 10))

                actions = customtkinter.CTkFrame(row, fg_color="transparent")
                actions.pack(side="right")

                edit_btn = customtkinter.CTkButton(actions, text="Edit", width=64, command=partial(self._on_card_edit_id, person_type, idv))
                edit_btn.pack(pady=2)

                del_btn = customtkinter.CTkButton(actions, text="Delete", width=64, fg_color="#ef4444", hover_color="#f97373",
                                                  command=partial(self._on_card_delete_id, person_type, idv))
                del_btn.pack(pady=2)

        self._refresh_bulk_buttons_state()

    # -------- selection --------
    def _on_toggle_select(self, key, var):
        if var.get() == "1":
            self.selected.add(key)
        else:
            self.selected.discard(key)
        self._refresh_bulk_buttons_state()

    def on_select_all(self):
        for key, chk in self.checkbox_widgets.items():
            self.selected.add(key)
            try: chk.select()
            except Exception: pass
        self._refresh_bulk_buttons_state()

    def on_clear_selection(self):
        self.selected.clear()
        for chk in self.checkbox_widgets.values():
            try: chk.deselect()
            except Exception: pass
        self._refresh_bulk_buttons_state()

    def _refresh_bulk_buttons_state(self):
        n = len(self.selected)
        self.save_btn.configure(state=("normal" if n == 1 else "disabled"))
        self.bulk_delete_btn.configure(state=("normal" if n >= 1 else "disabled"))

    # -------- card actions --------
    def _on_card_delete_id(self, person_type, idv):
        ok, msg = self.presenter.delete_by_id(person_type, idv)
        self.show_message(msg)
        if ok:
            self.selected.discard((person_type, idv))
            self.render_cards()

    def _on_card_edit_id(self, person_type, idv):
        obj = self.presenter.find_by_id(person_type, idv)
        if not obj:
            self.show_message(f"{person_type} id={idv} not found for edit")
            return
        mapping = {
            "Name": getattr(obj, "name", ""),
            "ID": getattr(obj, "id", ""),
            "Grade": getattr(obj, "grade", ""),
            "Speciality": getattr(obj, "speciality", ""),
            "Salary": getattr(obj, "salary", ""),
            "Department": getattr(obj, "department", ""),
            "Subject": getattr(obj, "subject", "")
        }
        try:
            self.data_type.set(person_type)
            self.create_inputs(person_type)
        except Exception:
            pass
        for key, widget in self.input_widgets.items():
            val = mapping.get(key, "")
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, "end"); widget.insert(0, str(val))
            elif isinstance(widget, customtkinter.CTkOptionMenu):
                try: widget.set(val)
                except Exception: pass
        self.selected = {(person_type, idv)}
        self._refresh_bulk_buttons_state()

    # -------- bulk actions --------
    def on_delete_selected(self):
        if not self.selected:
            return
        errors = []
        for person_type, idv in list(self.selected):
            ok, msg = self.presenter.delete_by_id(person_type, idv)
            if not ok: errors.append(msg)
            else: self.selected.discard((person_type, idv))
        if errors: self.show_message(" | ".join(errors))
        else: self.show_message("Deleted selected")
        self.render_cards()

    # -------- save --------
    def on_save_clicked(self):
        if len(self.selected) != 1:
            self.show_message("Select exactly one record for Save")
            return
        (person_type, original_id) = next(iter(self.selected))
        values = self.get_input_values()
        ok, msg, new_id = self.presenter.apply_changes(person_type, original_id, values)
        self.show_message(msg)
        self.selected.clear()
        if ok:
            self.render_cards()
            self.on_view_clicked()

    # -------- top actions --------
    def on_type_changed(self, person_type):
        self.create_inputs(person_type)

    def on_sort_changed(self, label):
        self.presenter.set_sort_mode(label)
        self.render_cards()

    def on_add_clicked(self):
        person_type = self.data_type.get()
        values = self.get_input_values()
        if not self.presenter.validate_fields(values):
            self.show_message("Fill all fields")
            return
        ok, msg = self.presenter.add_person(person_type, values)
        self.show_message(msg)
        if ok:
            self.clear_inputs()
            self.render_cards()
            self.on_view_clicked()

    def on_view_clicked(self):
        try:
            dump = self.presenter.get_all_data()
        except Exception as e:
            dump = f"[ERROR] {e}"
        self._set_viewall_text(dump)
        self.show_message("Dump refreshed")

    def on_charts_clicked(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Charts")
        win.geometry("900x600")
        frame = ChartsFrame(win, self.presenter, width=860, height=540)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
