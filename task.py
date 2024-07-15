import tkinter as tk
from tkinter import simpledialog
import time
from tkinter import Menu


class GanttChartApp:
    def __init__(self, root_w):
        self.hovering_over_edge = None
        self.pos = None
        self.offset_x = None
        self.timeline = None
        self.root = root_w
        self.root.title("工作流程（甘特）图绘制软件")

        self.create_menu()
        self.create_timeline()
        self.create_task_canvas()
        self.task_canvas.bind("<Motion>", self.on_mouse_motion)
        self.tasks = []
        self.selected_task = None
        self.last_click_time = 0
        self.last_clicked_task = None

    def on_mouse_motion(self, event):
        self.hovering_over_edge = False
        for task in self.tasks:
            if self.task_canvas.coords(task["rect"])[0] <= event.x <= self.task_canvas.coords(task["rect"])[2] and \
                    self.task_canvas.coords(task["rect"])[1] <= event.y <= self.task_canvas.coords(task["rect"])[3]:
                self.selected_task = task
            x1, y1, x2, y2 = self.task_canvas.coords(task["rect"])
            if (x2 - 10 <= event.x <= x2 and y1 <= event.y <= y2) or (x1 - 10 <= event.x <= x1 and y1 <= event.y <= y2):
                if x2 - 10 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.pos = "right"
                if x1 - 10 <= event.x <= x1 and y1 <= event.y <= y2:
                    self.pos = "left"
                self.task_canvas.config(cursor="sb_h_double_arrow")
                self.hovering_over_edge = True
                break
        if not self.hovering_over_edge:
            self.task_canvas.config(cursor="")

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        task_menu = tk.Menu(menu_bar, tearoff=0)
        task_menu.add_command(label="Add Task", command=self.add_task)
        # task_menu.add_command(label="Delete Task", command=self.delete_task)
        # 多级菜单组合
        menu_bar.add_cascade(label="Tasks", menu=task_menu)
        # 将菜单栏添加到主窗口中
        self.root.config(menu=menu_bar)

    def create_timeline(self):
        self.timeline = tk.Canvas(self.root, height=40, bg='lightgrey')
        self.timeline.pack(fill=tk.X)
        # pack()方法在一个特定的方向（TOP, BOTTOM, LEFT, RIGHT）上是排他的，
        # 这意味着在同一方向上只能有一个控件使用pack()。如果你在同一个方向上多次调用pack()，后一个控件将覆盖前一个控件的位置
        self.timeline.create_line(25, 0, 25, 40, fill="black", dash=(2, 2))
        for i in range(50):  # Example: Natural number timeline
            x = 50 + i * 50
            self.timeline.create_text(x, 20, text=f"{i}")
            self.timeline.create_line(x + 25, 0, x + 25, 40, fill="black", dash=(2, 2))

    def create_task_canvas(self):
        self.task_canvas = tk.Canvas(self.root, bg='white')
        self.task_canvas.pack(fill=tk.BOTH, expand=True)  # Canvas控件的背景色为白色，通过pack()方法将其填满root窗口
        self.task_canvas.create_line(25, 0, 25, 2000, fill="grey", dash=(4, 4))
        for i in range(50):  # Example: Natural number timeline
            x = 50 + i * 50
            self.task_canvas.create_line(x + 25, 0, x + 25, 2000, fill="grey", dash=(4, 4))
        # self.timeline.pack(fill=tk.X)
        # 相比之下，Timeline小部件仅会填充父容器的水平空间。这意味着当窗口变宽时，Timeline也会变宽，但它不会在垂直方向上扩展，即使有额外的垂直空间可用。
        self.task_canvas.bind("<Button-1>", self.on_canvas_click)
        self.task_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.popup_menu = Menu(root, tearoff=0)
        self.popup_menu.add_command(label="delete", command=self.delete_task)
        self.task_canvas.bind("<Button-3>", self.task_right_click)

    def add_task(self):
        task_name = simpledialog.askstring("task name", "input:")
        if task_name:
            if self.tasks != [] and self.tasks[-1] is not None:
                start = self.task_canvas.coords(self.tasks[-1]["rect"])[2] + self.tasks[-1]["length"]
            else:
                start = len(self.tasks) * 150 + 25
            task = {"name": task_name, "start": start, "length": 100, "rect": None, "text": None,
                    "dependency": None, "back": None, "arrow": None}
            if self.tasks:
                task["dependency"] = self.tasks[-1]
                self.tasks[-1]["back"] = task
            self.tasks.append(task)
            self.draw_task(task)

    def task_right_click(self, event):
        if self.selected_task:
            self.task_canvas.itemconfig(self.selected_task["rect"], outline="red")
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()

    def delete_task(self):
        if self.selected_task:
            task = self.selected_task
            while task is not None:
                self.task_canvas.delete(task["rect"])
                self.task_canvas.delete(task["text"])
                if task["arrow"]:
                    self.task_canvas.delete(task["arrow"])
                self.tasks.remove(task)
                self.selected_task = None
                task = task["back"]

    def draw_task(self, task):
        y = 50 + self.tasks.index(task) * 50
        task["rect"] = self.task_canvas.create_rectangle(task["start"], y, task["start"] + task["length"], y + 20,
                                                         fill="white", outline="blue", width=2)
        task["text"] = self.task_canvas.create_text((task["start"] + task["start"] + task["length"]) // 2, y + 10,
                                                    text=task["name"], fill="black")
        if task["dependency"]:
            self.draw_dependency_arrow(task)

    def draw_dependency_arrow(self, task):
        """绘制当前task与下一个任务的箭头"""
        if task["arrow"]:
            # **删除旧箭头**
            self.task_canvas.delete(task["arrow"])
        dep_task = task["dependency"]
        if dep_task:
            dep_coords = self.task_canvas.coords(dep_task["rect"])
            task_coords = self.task_canvas.coords(task["rect"])
            arrow_x_start = dep_coords[2]
            arrow_y_start = (dep_coords[1] + dep_coords[3]) / 2
            arrow_x_end = task_coords[0]
            arrow_y_end = (task_coords[1] + task_coords[3]) / 2
            task["arrow"] = self.task_canvas.create_line(arrow_x_start, arrow_y_start,
                                                         arrow_x_start + 10, arrow_y_start,
                                                         arrow_x_start + 10, arrow_y_end,
                                                         arrow_x_end, arrow_y_end, arrow=tk.LAST, fill="blue")
            # 创建出一条从(arrow_x_start, arrow_y_start)到(arrow_x_end, arrow_y_end)的蓝色箭头线条
            # 其中，(arrow_x_start + 10, arrow_y_start)和(arrow_x_start + 10, arrow_y_end)是箭头的两个控制点，用于绘制箭头的形状。
            # 最后，该函数将创建的线条对象保存在task字典的"arrow"键中。

    # def redraw_tasks(self):
    #     self.task_canvas.delete("all")
    #     for task in self.tasks:
    #         self.draw_task(task)

    def on_canvas_click(self, event):
        current_time = time.time()
        # 获取当前系统时间的时间戳
        for task in self.tasks:
            if self.task_canvas.coords(task["rect"])[0] <= event.x <= self.task_canvas.coords(task["rect"])[2] and \
                    self.task_canvas.coords(task["rect"])[1] <= event.y <= self.task_canvas.coords(task["rect"])[3]:
                # self.task_canvas.itemconfig(self.selected_task["rect"], outline="blue")
                # - 如果之前有选中的任务（`self.selected_task`），将其边框颜色恢复为黑色
                if self.last_clicked_task == task and (current_time - self.last_click_time) < 0.5:
                    # - 如果连续两次点击的是同一个任务，并且两次点击之间的时间间隔小于0.5秒，视为双击操作。
                    new_name = simpledialog.askstring("Edit Task Name", "Enter new task name:",
                                                      initialvalue=task["name"])
                    if new_name:
                        task["name"] = new_name
                        self.task_canvas.itemconfig(task["text"], text=new_name)
                self.last_click_time = current_time
                self.last_clicked_task = task
                break
            else:
                self.task_canvas.itemconfig(self.selected_task["rect"], outline="blue")

    def on_canvas_drag(self, event):
        if self.hovering_over_edge:
            new_start = event.x
            if self.pos == "left":
                if event.x >= self.task_canvas.coords(self.selected_task["rect"])[2] - 10:
                    new_start = self.task_canvas.coords(self.selected_task["rect"])[2] - 10
                length = new_start - self.task_canvas.coords(self.selected_task["rect"])[0]
                self.task_canvas.coords(self.selected_task["rect"], new_start,
                                        self.task_canvas.coords(self.selected_task["rect"])[1],
                                        self.task_canvas.coords(self.selected_task["rect"])[2],
                                        self.task_canvas.coords(self.selected_task["rect"])[3])
                self.task_canvas.coords(self.selected_task["text"],
                                        (new_start + self.task_canvas.coords(self.selected_task["rect"])[2]) // 2,
                                        self.task_canvas.coords(self.selected_task["text"])[1])
                if self.selected_task["dependency"]:
                    self.draw_dependency_arrow(self.selected_task)
            elif self.pos == "right":
                if event.x <= self.task_canvas.coords(self.selected_task["rect"])[0] + 10:
                    new_start = self.task_canvas.coords(self.selected_task["rect"])[0] + 10
                length = new_start - self.task_canvas.coords(self.selected_task["rect"])[2]
                self.task_canvas.coords(self.selected_task["rect"],
                                        self.task_canvas.coords(self.selected_task["rect"])[0],
                                        self.task_canvas.coords(self.selected_task["rect"])[1],
                                        new_start,
                                        self.task_canvas.coords(self.selected_task["rect"])[3])
                self.task_canvas.coords(self.selected_task["text"],
                                        (self.task_canvas.coords(self.selected_task["rect"])[0] + new_start) // 2,
                                        self.task_canvas.coords(self.selected_task["text"])[1])
                if self.selected_task["back"]:
                    self.draw_dependency_arrow(self.selected_task["back"])
                self.update_dependent_tasks(self.selected_task, forward=False, length=length)
            # task_index = self.tasks.index(self.selected_task)
            #
            # if task_index > 0 and new_start < self.task_canvas.coords(self.tasks[task_index - 1]["rect"])[2]:
            #     new_start = self.task_canvas.coords(self.tasks[task_index - 1]["rect"])[2]
            # self.selected_task["start"] = new_start
            # self.task_canvas.coords(self.selected_task["rect"], new_start,
            #                         self.task_canvas.coords(self.selected_task["rect"])[1],
            #                         new_start + self.selected_task["length"],
            #                         self.task_canvas.coords(self.selected_task["rect"])[3])
            # self.task_canvas.coords(self.selected_task["text"],
            #                         (new_start + new_start + self.selected_task["length"]) // 2,
            #                         self.task_canvas.coords(self.selected_task["text"])[1])
            # if self.selected_task["dependency"]:
            #     self.draw_dependency_arrow(self.selected_task)
            # self.update_dependent_tasks(self.selected_task)

    def update_dependent_tasks(self, task, forward: False, length):
        if forward:
            task_ = task["dependency"]
            while task_ is not None:
                self.task_canvas.coords(task_["rect"], self.task_canvas.coords(task_["rect"])[0] + length,
                                        self.task_canvas.coords(task_["rect"])[1],
                                        self.task_canvas.coords(task_["rect"])[2] + length,
                                        self.task_canvas.coords(task_["rect"])[3])
                self.task_canvas.coords(task_["text"],
                                        (self.task_canvas.coords(task_["rect"])[0] +
                                         self.task_canvas.coords(task_["rect"])[2]) // 2,
                                        self.task_canvas.coords(task_["text"])[1])

                if task_["dependency"]:
                    self.draw_dependency_arrow(task_)
                task_ = task_["dependency"]
        else:
            # 向后更新
            task_ = task["back"]
            while task_ is not None:
                self.task_canvas.coords(task_["rect"], self.task_canvas.coords(task_["rect"])[0] + length,
                                        self.task_canvas.coords(task_["rect"])[1],
                                        self.task_canvas.coords(task_["rect"])[2] + length,
                                        self.task_canvas.coords(task_["rect"])[3])
                self.task_canvas.coords(task_["text"],
                                        (self.task_canvas.coords(task_["rect"])[0] +
                                         self.task_canvas.coords(task_["rect"])[2]) // 2,
                                        self.task_canvas.coords(task_["text"])[1])
                if task_["back"]:
                    self.draw_dependency_arrow(task_["back"])
                task_ = task_["back"]


if __name__ == "__main__":
    root = tk.Tk()
    # Tk类：
    # 主窗口：它是任何Tkinter应用的基础，每个应用至少有一个Tk实例，通常用来作为所有其他控件的容器。
    # 事件循环：Tk对象负责处理事件循环，这意味着它可以响应用户的输入，如鼠标点击和键盘按键，并更新界面以反映这些动作。
    # 窗口属性：你可以使用Tk对象的方法来控制窗口的属性，例如标题、大小、位置、图标等。
    # 控件管理：你可以在Tk窗口中添加各种控件，如按钮、标签、文本框等，这些控件可以使用不同的布局管理器（如pack, grid, 或 place）进行定位。
    # 启动应用：通常，在创建Tk对象之后，你需要调用mainloop()方法来开始事件循环，这会让窗口持续显示直到用户关闭它。
    app = GanttChartApp(root)
    root.mainloop()
