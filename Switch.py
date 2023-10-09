import tkinter as tk


class Switch(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, width=40, height=20, *args, **kwargs)
        self.value = False  # Переключатель выключен по умолчанию
        self.configure(borderwidth=0, highlightthickness=0)  # Убираем рамку

        # Сам переключатель
        self.rect = self.create_rectangle(1, 1, 40, 20, outline='black', fill='red', width=1, tags='rect')

        # Белый кругляш
        self.oval = self.create_oval(2, 2, 18, 18, outline='black', fill='white', tags='oval')

        self.tag_bind('oval', '<1>', self.toggle)
        self.tag_bind('rect', '<1>', self.toggle)

    # Метод для переключения состояния Switch
    def toggle(self, event=None):
        self.value = not self.value
        fill_color = 'green' if self.value else 'red'
        oval_x0, oval_y0, oval_x1, oval_y1 = (22, 2, 38, 18) if self.value else (2, 2, 18, 18)
        self.coords(self.oval, oval_x0, oval_y0, oval_x1, oval_y1)
        self.itemconfig(self.rect, fill=fill_color)
        self.event_generate('<<SwitchToggled>>')  # Генерируем событие при переключении

    @property
    def is_on(self):
        return self.value
