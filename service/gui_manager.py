from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .operation_manager import OperationManager as op


class Widget:
    # Precated Types
    Type = {  # noqa: RUF012
        # Command [O]
        "Button": lambda parent: tk.Button(parent),
        "Checkbutton": lambda parent: tk.Checkbutton(parent),
        "Radiobutton": lambda parent: tk.Radiobutton(parent),
        "Scale": lambda parent: tk.Scale(parent),
        "Spinbox": lambda parent: tk.Spinbox(parent),
        # Command [X]
        "Label": lambda parent: tk.Label(parent),
        "Entry": lambda parent: tk.Entry(parent),
        "Text": lambda parent: tk.Text(parent),
        "Frame": lambda parent: tk.Frame(parent),
        "Canvas": lambda parent: tk.Canvas(parent),
        "ListBox": lambda parent: tk.Listbox(parent),
        "Scrollbar": lambda parent: tk.Scrollbar(parent),
    }

    isItCommand = {  # noqa: RUF012
        "Button": True,
        "Checkbutton": True,
        "Radiobutton": True,
        "Scale": True,
        "Spinbox": True,
        "Label": False,
        "Entry": False,
        "Text": False,
        "Frame": False,
        "Canvas": False,
        "ListBox": False,
        "Scrollbar": False,
    }

    # Info

    def __init__(
        self,
        parent: (Page | Widget),
        name: str = "",
        widgetType: str = None,
        style: dict[str, any] = None,
        placeType: str = None,
        placeAttribute: dict[str, any] = None,
        sync=None,
        event=None,
    ):
        # Set Attributes

        if widgetType not in Widget.Type:
            raise ValueError(f"Unknown widget type: {widgetType}")
        self._obj: tk.Widget = Widget.Type[widgetType](parent.obj)
        self._parent: Page | Widget = parent
        self._name: str = name
        self._widgetType: str = widgetType
        self._style: dict[str, any] = style or {}
        self._placeType: str = placeType
        self._placeAttribute: dict[str, any] = placeAttribute or {}
        self._sync = sync
        self._event = event

        self.__activated = False

        self.childWidgets: dict[str, Widget] = {}

        # Initalize

        widget = self._obj
        widget.cls = self
        if Widget.isItCommand[self._widgetType] == True:
            if self._event != None:
                widget.config(command=self.__command(self._event))
        if self._style:
            widget.config(self._style)
        self.placeWidget()

    # Attribute Changes

    @property
    def obj(self):  # Read Only
        return self._obj

    @property
    def parent(self):  # Read Only
        return self._parent

    @property
    def widgetType(self):  # Read Only
        return self._widgetType

    @property
    def placeType(self):  # Read Only
        return self._placeType

    @property
    def placeAttribute(self):  # Read Only
        return self._placeAttribute

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if self._name != new_name:
            old_name = self._name
            self._name = new_name
            if isinstance(self._parent, Page):
                self._parent.widgets[self._name] = self._parent.widgets.pop(old_name)
            elif isinstance(self._parent, Widget):
                self._parent.childWidgets[self._name] = self._parent.childWidgets.pop(
                    old_name
                )

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, new_style):
        self._style = new_style
        self._obj.config(**self._style)

    @property
    def sync(self):
        return self._sync.__name__

    @sync.setter
    def sync(self, new_sync):
        if self._sync__name__ != new_sync.__name__:
            self._sync = new_sync

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, new_event):
        if self._event is not new_event:
            self._event = new_event
            if Widget.isItCommand[self._widgetType] == True:
                self._obj.config(command=self.__command(self._event))

    # Inner Member Methods

    def __command(self, event):
        def command():
            if self.__activated:
                return

            self.__activated = True
            event(self)
            self.__activated = False

        return command

    # Member Methods

    def hideWidget(self):
        match self.placeType:
            case "pack":
                self.obj.pack_forget()
            case "grid":
                self.obj.grid_forget()
            case "place":
                self.obj.place_forget()

    def placeWidget(self):
        match self.placeType:
            case "pack":
                self.obj.pack(**self.placeAttribute)
            case "grid":
                self.obj.grid(**self.placeAttribute)
            case "place":
                self.obj.place(**self.placeAttribute)

    def addChildWidget(
        self,
        name: str,
        widgetType: str = None,
        style: dict[str, any] = None,
        placeType: str = None,
        placeAttribute: dict[str, any] = None,
        sync=lambda: None,
        event=lambda: None,
    ):
        if name not in self.childWidgets:
            self.childWidgets[name] = Widget(
                self, name, widgetType, style, placeType, placeAttribute, sync, event
            )

    def removeChildWidget(self, name: str):
        if name in self.childWidgets:
            del self.childWidgets[name]

    def changePlaceAttribute(self, new_placeType, new_placeAttribute):
        self._placeType = new_placeType
        self._placeAttribute = new_placeAttribute
        self.placeWidget()

    def syncWidget(self):
        for child in self.childWidgets.values():
            child.syncWidget()
        if self._sync != None:
            self._sync(self)

    def destroy(self):
        for widget in list(self.childWidgets.values()):
            widget.destroy()

        self.childWidgets.clear()
        self._obj.destroy()


class Page:
    # Info

    def __init__(self, parent: Window, name: str = "", style: dict[str, any] = None):
        # Set Attributes

        self._obj: tk.Frame = tk.Frame(parent.obj)
        self._name: str = name
        self._parent = parent
        self._style = style or {}

        self.widgets: dict[str, Widget] = {}

        # Initalize

        page = self._obj
        page.cls = self
        page.config(**self._style)

    # Attribute Changes

    @property
    def obj(self):  # Read Only
        return self._obj

    @property
    def parent(self):  # Read Only
        return self._parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        if self._name != new_name:
            old_name = self._name
            self._name = new_name
            self._parent.pages[self._name] = self._parent.pages.pop(old_name)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, new_Style: dict[str, any]):
        self._style = new_Style
        self._obj.config(**self._style)
        if self.parent.currentPage is self:
            self.placePage()

    # Member Methods

    def hidePage(self):
        self.obj.pack_forget()

    def placePage(self):
        for widget in self.widgets.values():
            widget.syncWidget()
        self.obj.pack(fill="both", expand=1)

    def addWidget(
        self,
        name: str,
        widgetType: str = None,
        style: dict[str, any] = None,
        placeType: str = None,
        placeAttribute: dict[str, any] = None,
        sync=None,
        event=None,
    ):
        if name not in self.widgets:
            self.widgets[name] = Widget(
                self, name, widgetType, style, placeType, placeAttribute, sync, event
            )

    def removeWidget(self, name: str):
        if name in self.widgets:
            del self.widgets[name]

    def destroy(self):
        for widget in list(self.widgets.values()):
            widget.destroy()

        self.widgets.clear()
        self._obj.destroy()


class Window:
    # Info

    def __init__(
        self,
        name: str = "",
        size: str = "100x100",
        icon: any = None,
        resizable: list[bool] = [False, False],
    ):
        # Set Attributes

        self._obj: tk.Tk = tk.Tk()
        self._name: str = name
        self._size: str = size
        self._icon: any = icon
        self._resizable: list[bool] = resizable

        self.pages: dict[str, Page] = {}
        self.currentPage: Page = None

        # Initalize

        window = self.obj
        window.cls = self
        window.title(self._name)
        window.geometry(self._size)
        window.resizable(*self._resizable)
        if icon is not None:
            window.iconbitmap(icon)

    # Attribute Changes

    @property  # Read Only
    def obj(self):
        return self._obj

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        if self._name != new_name:
            self._name = new_name
            self._obj.title(self._name)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size: str):
        if self._size != new_size:
            self._size = new_size
            self._obj.geometry(self._size)

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, new_icon: any):
        self._icon = new_icon
        self._obj.iconbitmap(self._icon)

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, new_resizable: list[bool]):
        self._resizable = new_resizable
        self._obj.resizable(*self._resizable)

    # Member Methods

    def addPage(self, name: str):
        if name not in self.pages:
            self.pages[name] = Page(self, name)

    def removePage(self, name: str):
        if name in self.pages:
            page = self.pages.pop(name)
            page.destroy()

    def changePage(self, name: str):
        if name not in self.pages:
            return
        if self.currentPage is not self.pages[name]:
            old_page = self.currentPage
            new_page = self.pages[name]
            self.currentPage = new_page
            if old_page is not None:
                old_page.hidePage()
            self.currentPage.placePage()

    def destroy(self):
        for page in list(self.pages.values()):
            page.destroy()

        self.pages.clear()
        self._obj.destroy()


# 메인 클래스 (자바 생각하면 편함)
class GUI:
    def __init__(self):
        main_window = Window(
            size="600x820",
            icon=op.GetSource("icon"),
            resizable=[False, False],
            name="청춘 일상 다이어트 총력전",
        )

        main_window.addPage("defaultPage")
        main_window.addPage("calendarReadPage")
        main_window.addPage("recordManagePage")
        main_window.addPage("calendarWritePage")
        main_window.addPage("foodManagePage")

        for page in main_window.pages.values():
            page.style = {"bg": "#B7BEFF"}

        defaultpage = main_window.pages["defaultPage"]
        main_meal_scroll_targets = {}

        def no_sync(widget):
            return None

        def sync_main_date(widget):
            widget.style = {
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
                "text": op.getDate(op.getSelectedDate()),
                "font": ("Malgun Gothic", 16, "bold"),
                "fg": "#919CFD",
                "justify": "left",
            }

        def sync_main_meal_list(widget, meal):
            meal_data = op.getManagementData(op.getSelectedDate())["meals"][meal]
            for child in list(widget.childWidgets.values()):
                child.destroy()
            widget.childWidgets.clear()

            if not meal_data:
                widget.addChildWidget(
                    name="등록된 음식 없음",
                    widgetType="Label",
                    style={
                        "text": "등록된 음식이 없습니다.",
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 9),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={"fill": "x", "padx": 3, "pady": 1},
                    sync=no_sync,
                )
            else:
                for index, item in enumerate(meal_data):
                    widget.addChildWidget(
                        name=f"음식 {index}",
                        widgetType="Label",
                        style={
                            "text": item["text"],
                            "bg": "#D1D6FF",
                            "fg": "#626FCB",
                            "font": ("Malgun Gothic", 9),
                            "anchor": "w",
                        },
                        placeType="pack",
                        placeAttribute={"fill": "x", "padx": 3, "pady": 1},
                        sync=no_sync,
                    )

            scroll_target = main_meal_scroll_targets.get(meal)
            if scroll_target is not None:

                def refresh_scroll_region():
                    canvas_obj = scroll_target["canvas"]
                    canvas_obj.update_idletasks()
                    content_height = max(scroll_target["content"].winfo_reqheight(), 1)
                    canvas_obj.itemconfigure(
                        scroll_target["window"], height=content_height
                    )
                    canvas_obj.configure(scrollregion=canvas_obj.bbox("all"))

                scroll_target["canvas"].after_idle(refresh_scroll_region)

        def make_main_meal_scrollable_area(parent, meal):
            parent.addChildWidget(
                name="음식 목록 영역",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1, "padx": 3, "pady": 2},
                sync=no_sync,
            )
            outer = parent.childWidgets["음식 목록 영역"]
            outer.addChildWidget(
                name="스크롤 프레임",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1},
                sync=no_sync,
            )
            scroll_frame = outer.childWidgets["스크롤 프레임"]
            scroll_frame.obj.grid_rowconfigure(0, weight=1)
            scroll_frame.obj.grid_columnconfigure(0, weight=1)
            scroll_frame.addChildWidget(
                name="목록 캔버스",
                widgetType="Canvas",
                style={"bg": "#D1D6FF", "highlightthickness": 0},
                placeType="grid",
                placeAttribute={"row": 0, "column": 0, "sticky": "nsew"},
                sync=no_sync,
            )
            scroll_frame.addChildWidget(
                name="세로 스크롤",
                widgetType="Scrollbar",
                style={
                    "orient": "vertical",
                    "width": 14,
                    "bg": "#8C62FF",
                    "activebackground": "#653CD6",
                    "troughcolor": "#B7BEFF",
                    "borderwidth": 1,
                    "highlightthickness": 0,
                },
                placeType="grid",
                placeAttribute={"row": 0, "column": 1, "sticky": "ns"},
                sync=no_sync,
            )
            canvas = scroll_frame.childWidgets["목록 캔버스"]
            scrollbar = scroll_frame.childWidgets["세로 스크롤"]
            canvas.obj.configure(yscrollcommand=scrollbar.obj.set)
            scrollbar.obj.configure(command=canvas.obj.yview)
            canvas.addChildWidget(
                name="목록 내용",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType=None,
                placeAttribute={},
                sync=lambda widget, selected_meal=meal: sync_main_meal_list(
                    widget, selected_meal
                ),
            )
            content = canvas.childWidgets["목록 내용"]
            canvas_window = canvas.obj.create_window(
                (0, 0), window=content.obj, anchor="nw"
            )
            content.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj: target.configure(
                    scrollregion=target.bbox("all")
                ),
            )
            canvas.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj, item=canvas_window: (
                    target.itemconfigure(item, width=event.width)
                ),
            )
            main_meal_scroll_targets[meal] = {
                "canvas": canvas.obj,
                "content": content.obj,
                "window": canvas_window,
            }
            return content

        def sync_main_meal_summary(widget):
            data = op.getManagementData(op.getSelectedDate())
            weight = data["weight"]
            weight_text = "미입력" if weight is None or weight == "" else f"{weight} kg"
            widget.style = {
                "text": (
                    f"총 섭취 열량: {data['total_calories']:g} kcal     "
                    f"체중: {weight_text}"
                ),
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 12, "bold"),
                "anchor": "w",
            }

        def sync_main_weight_status(widget):
            widget.style = {
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
                "text": op.getRecentWeightSummary(),
                "font": ("Malgun Gothic", 16, "bold"),
                "fg": "#919CFD",
                "justify": "center",
                "anchor": "n",
            }

        def sync_main_result(widget):
            result = op.getDailyResult(op.getSelectedDate())
            if result["success"] is True:
                background, border, foreground = "#D1FFE6", "#91FDC2", "#41A169"
            elif result["success"] is False:
                background, border, foreground = "#FFE0E5", "#F5A3B2", "#B53C55"
            else:
                background, border, foreground = "#D1D6FF", "#919CFD", "#626FCB"
            widget.style = {
                "bg": background,
                "highlightbackground": border,
                "highlightthickness": 3,
                "text": result["text"],
                "font": ("Malgun Gothic", 18, "bold"),
                "fg": foreground,
                "justify": "left",
                "anchor": "w",
            }

        def sync_main_target_calories(widget):
            widget.style = {
                "text": f"현재 목표: {op.getTargetCalories():g} kcal",
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 12, "bold"),
                "anchor": "e",
            }

        def confirm_main_target_calories(widget):
            target_entry = (
                main_window.pages["defaultPage"]
                .widgets["목표 열량 프레임"]
                .childWidgets["목표 열량 입력"]
            )
            result = op.setTargetCalories(target_entry.obj.get())
            if not result["ok"]:
                messagebox.showerror("목표 열량", result["message"])
                return
            target_entry.obj.delete(0, "end")
            main_window.pages["defaultPage"].widgets["목표 열량 프레임"].childWidgets[
                "현재 목표 열량"
            ].syncWidget()
            main_window.pages["defaultPage"].widgets["결과"].syncWidget()
            if result.get("warning"):
                messagebox.showinfo("목표 열량", result["warning"])

        defaultpage.addWidget(
            name="날짜 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 60},
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (10, 6)},
            sync=no_sync,
        )
        date_menu = defaultpage.widgets["날짜 메뉴"]
        date_menu.obj.pack_propagate(False)
        date_menu.addChildWidget(
            name="날짜 제목",
            widgetType="Label",
            style={
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
                "text": "날짜",
                "font": ("Malgun Gothic", 22, "bold"),
                "fg": "#919CFD",
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "y", "padx": (0, 8)},
            sync=no_sync,
        )
        date_menu.addChildWidget(
            name="날짜",
            widgetType="Label",
            style={
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
                "text": "Loading",
                "font": ("Malgun Gothic", 15, "bold"),
                "fg": "#919CFD",
                "justify": "left",
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "both", "expand": 1},
            sync=sync_main_date,
        )
        date_menu.addChildWidget(
            name="관리",
            widgetType="Button",
            style={
                "bg": "#D1D6FF",
                "text": "식단 관리",
                "font": ("Malgun Gothic", 12, "bold"),
                "fg": "#919CFD",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="pack",
            placeAttribute={"side": "right", "fill": "y", "padx": (6, 0)},
            sync=no_sync,
        )
        date_menu.addChildWidget(
            name="조회",
            widgetType="Button",
            style={
                "bg": "#D1D6FF",
                "text": "식단 조회",
                "font": ("Malgun Gothic", 12, "bold"),
                "fg": "#919CFD",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="pack",
            placeAttribute={"side": "right", "fill": "y", "padx": (6, 0)},
            sync=no_sync,
        )

        def onRecordReadButton(widget: Widget):
            window = widget.parent
            while True:
                if isinstance(window, Window):
                    break
                else:
                    window = window.parent

            if window.currentPage == window.pages["defaultPage"]:
                selected_date["value"] = op.getSelectedDate()
                draw_calendar(op.showCalendarMonth(selected_date["value"]))
                show_food_for_date(selected_date["value"])
                window.changePage("calendarReadPage")

        date_menu.childWidgets["조회"].event = onRecordReadButton

        def onRecordManageButton(widget: Widget):
            window = widget.parent
            while True:
                if isinstance(window, Window):
                    break
                else:
                    window = window.parent

            if window.currentPage == window.pages["defaultPage"]:
                managed_date["value"] = op.getSelectedDate()
                op.beginRecordManage(managed_date["value"])
                window.changePage("recordManagePage")

        date_menu.childWidgets["관리"].event = onRecordManageButton

        defaultpage.addWidget(
            name="식단표 타이틀",
            widgetType="Label",
            style={
                "bg": "#8C62FF",
                "highlightbackground": "#653CD6",
                "highlightthickness": 3,
                "text": "식  단  표",
                "font": ("Malgun Gothic", 22, "bold"),
                "fg": "#D9DDFF",
                "height": 1,
            },
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (0, 5)},
        )

        defaultpage.addWidget(
            name="식단표 프레임",
            widgetType="Frame",
            style={
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
            },
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "padx": 12, "pady": 5},
            sync=no_sync,
        )
        main_diet_frame = defaultpage.widgets["식단표 프레임"]
        main_diet_frame.addChildWidget(
            name="일일 요약",
            widgetType="Label",
            style={
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 12, "bold"),
                "height": 1,
            },
            placeType="pack",
            placeAttribute={"side": "bottom", "fill": "x", "padx": 2, "pady": (3, 0)},
            sync=sync_main_meal_summary,
        )
        main_diet_frame.addChildWidget(
            name="시간대 식단",
            widgetType="Frame",
            style={"bg": "#D1D6FF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1},
            sync=no_sync,
        )
        main_meal_grid = main_diet_frame.childWidgets["시간대 식단"]
        for meal_layout in op.getMealCardLayout():
            meal = meal_layout["name"]
            main_meal_grid.addChildWidget(
                name=meal,
                widgetType="Frame",
                style={
                    "bg": "#D1D6FF",
                    "highlightbackground": "#919CFD",
                    "highlightthickness": 2,
                },
                placeType="place",
                placeAttribute=meal_layout["place"],
                sync=no_sync,
            )
            meal_card = main_meal_grid.childWidgets[meal]
            meal_card.addChildWidget(
                name="제목",
                widgetType="Label",
                style={
                    "text": meal,
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "font": ("Malgun Gothic", 11, "bold"),
                    "anchor": "w",
                },
                placeType="pack",
                placeAttribute={"fill": "x", "padx": 3, "pady": (2, 0)},
                sync=no_sync,
            )
            make_main_meal_scrollable_area(meal_card, meal)

        defaultpage.addWidget(
            name="체중 현황 타이틀",
            widgetType="Label",
            style={
                "bg": "#8C62FF",
                "highlightbackground": "#653CD6",
                "highlightthickness": 3,
                "text": "최근 체중 변화",
                "font": ("Malgun Gothic", 22, "bold"),
                "fg": "#D9DDFF",
                "height": 1,
            },
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (4, 3)},
        )

        defaultpage.addWidget(
            name="체중 현황",
            widgetType="Label",
            style={
                "bg": "#D1D6FF",
                "highlightbackground": "#919CFD",
                "highlightthickness": 3,
                "text": "7일전 88.8(Kg) -> 현재 65.4(Kg) / ▼23.4 (Kg)▼",
                "font": ("Malgun Gothic", 16, "bold"),
                "fg": "#919CFD",
                "anchor": "n",
                "justify": "center",
                "height": 3,
            },
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (0, 6)},
            sync=sync_main_weight_status,
        )

        defaultpage.addWidget(
            name="목표 열량 프레임",
            widgetType="Frame",
            style={
                "bg": "#8C62FF",
                "highlightbackground": "#653CD6",
                "highlightthickness": 3,
            },
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (0, 6)},
            sync=no_sync,
        )
        target_calorie_frame = defaultpage.widgets["목표 열량 프레임"]
        target_calorie_frame.obj.configure(height=58)
        target_calorie_frame.obj.pack_propagate(False)
        target_calorie_frame.addChildWidget(
            name="목표 열량 안내",
            widgetType="Label",
            style={
                "text": "목표(kcal)",
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 5},
            sync=no_sync,
        )
        target_calorie_frame.addChildWidget(
            name="목표 열량 입력",
            widgetType="Entry",
            style={
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 11),
                "width": 8,
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "y", "padx": 3},
            sync=no_sync,
        )
        target_calorie_frame.addChildWidget(
            name="목표 열량 확인",
            widgetType="Button",
            style={
                "text": "확인",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10, "bold"),
                "activebackground": "#8997FF",
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "y", "padx": 3},
            sync=no_sync,
            event=confirm_main_target_calories,
        )
        target_calorie_frame.addChildWidget(
            name="현재 목표 열량",
            widgetType="Label",
            style={"bg": "#8C62FF", "fg": "#D9DDFF"},
            placeType="pack",
            placeAttribute={"side": "right", "fill": "x", "expand": 1, "padx": 8},
            sync=sync_main_target_calories,
        )

        defaultpage.addWidget(
            name="결과",
            widgetType="Label",
            style={
                "bg": "#D1FFE6",
                "highlightbackground": "#91FDC2",
                "highlightthickness": 3,
                "text": "목표 달성 성공!",
                "font": ("Malgun Gothic", 20, "bold"),
                "fg": "#41A169",
                "justify": "left",
                "height": 3,
            },
            placeType="pack",
            placeAttribute={"fill": "x", "padx": 12, "pady": (0, 10)},
            sync=sync_main_result,
        )

        calendarReadPage = main_window.pages["calendarReadPage"]
        selected_date = {"value": None}
        calendar_data = op.getCalendar()
        calendar_meal_list_widgets = {}
        calendar_meal_scroll_targets = {}

        calendarReadPage.addWidget(
            name="달력 프레임",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "padx": 10, "pady": (34, 14)},
        )
        calendar_frame = calendarReadPage.widgets["달력 프레임"]
        calendar_frame.addChildWidget(
            name="달력 월",
            widgetType="Label",
            style={
                "text": "",
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 24, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (0, 14)},
            sync=no_sync,
        )
        calendar_frame.addChildWidget(
            name="요일 및 날짜",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1},
            sync=no_sync,
        )
        days_frame = calendar_frame.childWidgets["요일 및 날짜"]
        for weekday in calendar_data["weekdays"]:
            days_frame.addChildWidget(
                name=f"요일 {weekday['text']}",
                widgetType="Label",
                style={
                    "text": weekday["text"],
                    "bg": "#8C62FF",
                    "fg": "white",
                    "font": ("Malgun Gothic", 13, "bold"),
                },
                placeType="place",
                placeAttribute=weekday["place"],
                sync=no_sync,
            )
        for cell in calendar_data["days"]:
            days_frame.addChildWidget(
                name=f"날짜 {cell['row']}-{cell['column']}",
                widgetType="Button",
                style={
                    "text": cell["text"],
                    "state": cell["state"],
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "font": ("Malgun Gothic", 14, "bold"),
                },
                placeType="place",
                placeAttribute=cell["place"],
                sync=no_sync,
                event=lambda widget: None,
            )
        calendar_frame.addChildWidget(
            name="달력 이동 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 44},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (14, 0)},
            sync=no_sync,
        )
        navigation = calendar_frame.childWidgets["달력 이동 메뉴"]
        navigation.addChildWidget(
            name="이전 달",
            widgetType="Button",
            style={
                "text": "◀",
                "bg": "#D1D6FF",
                "font": ("Malgun Gothic", 14, "bold"),
                "fg": "#626FCB",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda widget: change_month(-1),
        )
        navigation.addChildWidget(
            name="다음 달",
            widgetType="Button",
            style={
                "text": "▶",
                "bg": "#D1D6FF",
                "font": ("Malgun Gothic", 14, "bold"),
                "fg": "#626FCB",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda widget: change_month(1),
        )

        def show_food_for_date(selected):
            selected_date["value"] = selected
            calendar_frame.childWidgets["조회 식단 제목"].syncWidget()
            for meal_list in calendar_meal_list_widgets.values():
                meal_list.syncWidget()
            calendar_frame.childWidgets["조회 식단 요약"].syncWidget()

        def change_month(offset):
            draw_calendar(op.changeCalendarMonth(offset))

        def draw_calendar(calendar_data):
            calendar_frame.childWidgets["달력 월"].style = {
                "text": calendar_data["title"],
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 24, "bold"),
            }
            previous_button = navigation.childWidgets["이전 달"]
            if calendar_data["can_previous"]:
                previous_button.style = {
                    "text": "◀",
                    "state": "normal",
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "disabledforeground": "#626FCB",
                    "activebackground": "#8997FF",
                    "activeforeground": "#3140B3",
                    "font": ("Malgun Gothic", 14, "bold"),
                }
                previous_button.event = lambda widget: change_month(-1)
            else:
                previous_button.style = {
                    "text": "◀",
                    "state": "disabled",
                    "bg": "#858CAD",
                    "fg": "#515A86",
                    "disabledforeground": "#515A86",
                    "font": ("Malgun Gothic", 14, "bold"),
                }
                previous_button.event = lambda widget: None

            weekday_colors = {
                "weekday": "#626FCB",
                "saturday": "#4E79C7",
                "sunday": "#C45B74",
            }
            for cell in calendar_data["days"]:
                day_widget = days_frame.childWidgets[
                    f"날짜 {cell['row']}-{cell['column']}"
                ]
                if not cell["in_range"]:
                    background = "#858CAD"
                elif cell["has_record"]:
                    background = "#D1D6FF"
                else:
                    background = "#E6E9FF"
                day_widget.style = {
                    "text": cell["text"],
                    "state": cell["state"],
                    "bg": background,
                    "fg": weekday_colors[cell["weekday_type"]],
                    "disabledforeground": weekday_colors[cell["weekday_type"]],
                    "activebackground": "#8997FF",
                    "font": ("Malgun Gothic", 11, "bold"),
                    "anchor": "nw",
                    "justify": "left",
                }
                if cell["in_range"] and cell["date"] is not None:
                    day_widget.event = lambda widget, selected=cell["date"]: (
                        show_food_for_date(selected)
                    )
                else:
                    day_widget.event = lambda widget: None

        draw_calendar(calendar_data)

        def sync_calendar_food_title(widget):
            widget.style = {
                "text": op.getFoodTitle(selected_date["value"]),
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 18, "bold"),
            }

        def sync_calendar_meal_summary(widget):
            if selected_date["value"] is None:
                text = "날짜를 선택해 주세요."
            else:
                data = op.getManagementData(selected_date["value"])
                weight = data["weight"]
                weight_text = (
                    "미입력" if weight is None or weight == "" else f"{weight} kg"
                )
                text = (
                    f"총 섭취 열량: {data['total_calories']:g} kcal     "
                    f"체중: {weight_text}"
                )
            widget.style = {
                "text": text,
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 12, "bold"),
                "anchor": "w",
            }

        def sync_calendar_meal_list(widget, meal):
            for child in list(widget.childWidgets.values()):
                child.destroy()
            widget.childWidgets.clear()

            meal_items = []
            if selected_date["value"] is not None:
                meal_items = op.getManagementData(selected_date["value"])["meals"][meal]

            if not meal_items:
                empty_text = (
                    "날짜를 선택해 주세요."
                    if selected_date["value"] is None
                    else "등록된 음식이 없습니다."
                )
                widget.addChildWidget(
                    name="등록된 음식 없음",
                    widgetType="Label",
                    style={
                        "text": empty_text,
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 9),
                        "anchor": "nw",
                        "justify": "left",
                        "wraplength": 105,
                    },
                    placeType="pack",
                    placeAttribute={"fill": "x", "padx": 3, "pady": 2},
                    sync=no_sync,
                )
            else:
                for index, item in enumerate(meal_items):
                    widget.addChildWidget(
                        name=f"음식 {index}",
                        widgetType="Label",
                        style={
                            "text": item["text"],
                            "bg": "#D1D6FF",
                            "fg": "#626FCB",
                            "font": ("Malgun Gothic", 9),
                            "anchor": "nw",
                            "justify": "left",
                            "wraplength": 105,
                        },
                        placeType="pack",
                        placeAttribute={"fill": "x", "padx": 3, "pady": 2},
                        sync=no_sync,
                    )

            scroll_target = calendar_meal_scroll_targets.get(meal)
            if scroll_target is not None:

                def refresh_scroll_region():
                    canvas_obj = scroll_target["canvas"]
                    canvas_obj.update_idletasks()
                    content_height = max(scroll_target["content"].winfo_reqheight(), 1)
                    canvas_obj.itemconfigure(
                        scroll_target["window"], height=content_height
                    )
                    canvas_obj.configure(scrollregion=canvas_obj.bbox("all"))

                scroll_target["canvas"].after_idle(refresh_scroll_region)

        def make_calendar_meal_scrollable_area(parent, meal):
            parent.addChildWidget(
                name="음식 목록 영역",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1, "padx": 2, "pady": 2},
                sync=no_sync,
            )
            outer = parent.childWidgets["음식 목록 영역"]
            outer.addChildWidget(
                name="스크롤 프레임",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1},
                sync=no_sync,
            )
            scroll_frame = outer.childWidgets["스크롤 프레임"]
            scroll_frame.obj.grid_rowconfigure(0, weight=1)
            scroll_frame.obj.grid_columnconfigure(0, weight=1)
            scroll_frame.addChildWidget(
                name="목록 캔버스",
                widgetType="Canvas",
                style={"bg": "#D1D6FF", "highlightthickness": 0},
                placeType="grid",
                placeAttribute={"row": 0, "column": 0, "sticky": "nsew"},
                sync=no_sync,
            )
            scroll_frame.addChildWidget(
                name="세로 스크롤",
                widgetType="Scrollbar",
                style={
                    "orient": "vertical",
                    "width": 10,
                    "bg": "#8C62FF",
                    "activebackground": "#653CD6",
                    "troughcolor": "#B7BEFF",
                    "borderwidth": 1,
                    "highlightthickness": 0,
                },
                placeType="grid",
                placeAttribute={"row": 0, "column": 1, "sticky": "ns"},
                sync=no_sync,
            )
            canvas = scroll_frame.childWidgets["목록 캔버스"]
            scrollbar = scroll_frame.childWidgets["세로 스크롤"]
            canvas.obj.configure(yscrollcommand=scrollbar.obj.set)
            scrollbar.obj.configure(command=canvas.obj.yview)
            canvas.addChildWidget(
                name="목록 내용",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType=None,
                placeAttribute={},
                sync=lambda widget, selected_meal=meal: sync_calendar_meal_list(
                    widget, selected_meal
                ),
            )
            content = canvas.childWidgets["목록 내용"]
            canvas_window = canvas.obj.create_window(
                (0, 0), window=content.obj, anchor="nw"
            )
            content.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj: target.configure(
                    scrollregion=target.bbox("all")
                ),
            )
            canvas.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj, item=canvas_window: (
                    target.itemconfigure(item, width=event.width)
                ),
            )
            calendar_meal_scroll_targets[meal] = {
                "canvas": canvas.obj,
                "content": content.obj,
                "window": canvas_window,
            }
            return content

        calendar_frame.addChildWidget(
            name="조회 식단 제목",
            widgetType="Label",
            style={
                "text": "날짜별 식단표",
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 18, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (10, 0)},
            sync=sync_calendar_food_title,
        )
        calendar_frame.addChildWidget(
            name="조회 식단 목록",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "pady": (4, 0)},
            sync=no_sync,
        )
        calendar_meal_grid = calendar_frame.childWidgets["조회 식단 목록"]
        for meal_layout in op.getMealReadColumnLayout():
            meal = meal_layout["name"]
            calendar_meal_grid.addChildWidget(
                name=meal,
                widgetType="Frame",
                style={
                    "bg": "#D1D6FF",
                    "highlightbackground": "#919CFD",
                    "highlightthickness": 2,
                },
                placeType="place",
                placeAttribute=meal_layout["place"],
                sync=no_sync,
            )
            meal_card = calendar_meal_grid.childWidgets[meal]
            meal_card.addChildWidget(
                name="제목",
                widgetType="Label",
                style={
                    "text": meal,
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "font": ("Malgun Gothic", 11, "bold"),
                    "anchor": "w",
                },
                placeType="pack",
                placeAttribute={"fill": "x", "padx": 4, "pady": (3, 0)},
                sync=no_sync,
            )
            calendar_meal_list_widgets[meal] = make_calendar_meal_scrollable_area(
                meal_card, meal
            )
        calendar_frame.addChildWidget(
            name="조회 식단 요약",
            widgetType="Label",
            style={
                "text": "날짜를 선택해 주세요.",
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 12, "bold"),
                "anchor": "w",
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (3, 0)},
            sync=sync_calendar_meal_summary,
        )
        calendar_frame.addChildWidget(
            name="조회 결정 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 46},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (12, 0)},
            sync=no_sync,
        )
        decision_menu = calendar_frame.childWidgets["조회 결정 메뉴"]
        decision_menu.addChildWidget(
            name="확인",
            widgetType="Button",
            style={
                "text": "확인",
                "bg": "#D1D6FF",
                "font": ("Malgun Gothic", 13, "bold"),
                "fg": "#626FCB",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda widget: confirm_selected_date(widget),
        )
        decision_menu.addChildWidget(
            name="메인으로 돌아가기",
            widgetType="Button",
            style={
                "text": "메인으로 돌아가기",
                "bg": "#D1D6FF",
                "font": ("Malgun Gothic", 13, "bold"),
                "fg": "#626FCB",
                "activebackground": "#8997FF",
                "activeforeground": "#3140B3",
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda widget: main_window.changePage("defaultPage"),
        )

        calendar_frame.childWidgets["조회 식단 제목"].syncWidget()
        for meal_list in calendar_meal_list_widgets.values():
            meal_list.syncWidget()
        calendar_frame.childWidgets["조회 식단 요약"].syncWidget()

        def confirm_selected_date(widget):
            if selected_date["value"] is not None:
                op.setSelectedDate(selected_date["value"])
            main_window.changePage("defaultPage")

        recordManagePage = main_window.pages["recordManagePage"]

        managed_date = {"value": op.getSelectedDate()}
        pending_write_date = {"value": managed_date["value"]}
        meal_names = ("아침", "점심", "저녁", "야식")
        meal_list_widgets = {}
        meal_scroll_targets = {}

        def sync_managed_date(widget):
            widget.style = {
                "text": op.getManagementData(managed_date["value"])["date_text"],
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 18, "bold"),
                "anchor": "w",
            }

        def sync_total_calories(widget):
            widget.style = {
                "text": op.getManagementData(managed_date["value"])["total_text"],
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 16, "bold"),
                "anchor": "w",
            }

        def sync_weight_entry(widget):
            value = op.getManagementData(managed_date["value"])["weight"]
            widget.obj.delete(0, "end")
            if value is not None and value != "":
                widget.obj.insert(0, str(value))

        def sync_weight_value(widget):
            data = op.getManagementData(managed_date["value"])
            value = data["weight"]
            value_text = "미입력" if value is None or value == "" else f"{value} kg"
            prefix = (
                "입력 반영값 (확인 전)" if data["weight_pending"] else "저장된 체중"
            )
            widget.style = {
                "text": f"{prefix}: {value_text}",
                "bg": "#B7BEFF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10, "bold"),
            }

        def refresh_record_manage():
            date_menu.childWidgets["관리 날짜"].syncWidget()
            date_menu.childWidgets["삭제"].syncWidget()
            for meal_widget in meal_list_widgets.values():
                meal_widget.syncWidget()
            record_frame.childWidgets["총 열량"].syncWidget()
            weight_menu.childWidgets["체중 입력"].syncWidget()
            weight_menu.childWidgets["체중 반영값"].syncWidget()

        def remove_meal_food(meal, item_index):
            op.removeFood(managed_date["value"], meal, item_index)
            refresh_record_manage()

        def sync_meal_list(widget, meal):
            meal_data = op.getManagementData(managed_date["value"])["meals"][meal]
            for child in list(widget.childWidgets.values()):
                child.destroy()
            widget.childWidgets.clear()

            def refresh_scroll_region():
                scroll_target = meal_scroll_targets.get(meal)
                if scroll_target is None:
                    return

                def apply_scroll_region():
                    canvas_obj = scroll_target["canvas"]
                    canvas_obj.update_idletasks()
                    content_height = max(scroll_target["content"].winfo_reqheight(), 1)
                    canvas_obj.itemconfigure(
                        scroll_target["window"], height=content_height
                    )
                    canvas_obj.configure(scrollregion=canvas_obj.bbox("all"))

                scroll_target["canvas"].after_idle(apply_scroll_region)

            if not meal_data:
                widget.addChildWidget(
                    name="등록된 음식 없음",
                    widgetType="Label",
                    style={
                        "text": "등록된 음식이 없습니다.",
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 10),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 2},
                    sync=no_sync,
                )
                refresh_scroll_region()
                return
            for item in meal_data:
                widget.addChildWidget(
                    name=f"등록 음식 {item['index']}",
                    widgetType="Frame",
                    style={"bg": "#D1D6FF"},
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 1},
                    sync=no_sync,
                )
                row = widget.childWidgets[f"등록 음식 {item['index']}"]
                row.addChildWidget(
                    name="음식 정보",
                    widgetType="Label",
                    style={
                        "text": item["text"],
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 10),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={"side": "left", "fill": "x", "expand": 1},
                    sync=no_sync,
                )
                row.addChildWidget(
                    name="음식 삭제",
                    widgetType="Button",
                    style={
                        "text": "X",
                        "width": 3,
                        "bg": "#C45B74",
                        "fg": "white",
                        "activebackground": "#A63D58",
                    },
                    placeType="pack",
                    placeAttribute={"side": "right", "padx": 2},
                    sync=no_sync,
                    event=lambda button, selected_meal=meal, selected_index=item["index"]: (
                        remove_meal_food(selected_meal, selected_index)
                    ),
                )
            refresh_scroll_region()

        def make_meal_scrollable_area(parent, meal):
            parent.addChildWidget(
                name="음식 목록 영역",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1, "padx": 5, "pady": 3},
                sync=no_sync,
            )
            outer = parent.childWidgets["음식 목록 영역"]
            outer.addChildWidget(
                name="스크롤 프레임",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType="pack",
                placeAttribute={"fill": "both", "expand": 1},
                sync=no_sync,
            )
            scroll_frame = outer.childWidgets["스크롤 프레임"]
            scroll_frame.obj.grid_rowconfigure(0, weight=1)
            scroll_frame.obj.grid_columnconfigure(0, weight=1)
            scroll_frame.addChildWidget(
                name="목록 캔버스",
                widgetType="Canvas",
                style={"bg": "#D1D6FF", "highlightthickness": 0},
                placeType="grid",
                placeAttribute={"row": 0, "column": 0, "sticky": "nsew"},
                sync=no_sync,
            )
            scroll_frame.addChildWidget(
                name="세로 스크롤",
                widgetType="Scrollbar",
                style={
                    "orient": "vertical",
                    "width": 16,
                    "bg": "#8C62FF",
                    "activebackground": "#653CD6",
                    "troughcolor": "#B7BEFF",
                    "borderwidth": 1,
                    "highlightthickness": 0,
                },
                placeType="grid",
                placeAttribute={"row": 0, "column": 1, "sticky": "ns"},
                sync=no_sync,
            )
            canvas = scroll_frame.childWidgets["목록 캔버스"]
            scrollbar = scroll_frame.childWidgets["세로 스크롤"]
            canvas.obj.configure(yscrollcommand=scrollbar.obj.set)
            scrollbar.obj.configure(command=canvas.obj.yview)
            canvas.addChildWidget(
                name="목록 내용",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType=None,
                placeAttribute={},
                sync=lambda widget, selected_meal=meal: sync_meal_list(
                    widget, selected_meal
                ),
            )
            content = canvas.childWidgets["목록 내용"]
            canvas_window = canvas.obj.create_window(
                (0, 0), window=content.obj, anchor="nw"
            )
            content.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj: target.configure(
                    scrollregion=target.bbox("all")
                ),
            )
            canvas.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj, item=canvas_window: (
                    target.itemconfigure(item, width=event.width)
                ),
            )
            meal_scroll_targets[meal] = {
                "canvas": canvas.obj,
                "content": content.obj,
                "window": canvas_window,
            }
            return content

        def open_food_manage(meal):
            result = op.setWeight(
                managed_date["value"], weight_menu.childWidgets["체중 입력"].obj.get()
            )
            if not result["ok"]:
                messagebox.showerror("체중 입력", result["message"])
                return
            op.beginFoodManage(managed_date["value"], meal)
            main_window.changePage("foodManagePage")

        recordManagePage.addWidget(
            name="관리 화면 프레임",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "padx": 12, "pady": 12},
            sync=no_sync,
        )
        record_frame = recordManagePage.widgets["관리 화면 프레임"]
        record_frame.addChildWidget(
            name="날짜 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 48},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (0, 8)},
            sync=no_sync,
        )
        date_menu = record_frame.childWidgets["날짜 메뉴"]
        date_menu.addChildWidget(
            name="관리 날짜",
            widgetType="Label",
            style={
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 18, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "x", "expand": 1},
            sync=sync_managed_date,
        )

        def open_write_calendar(widget):
            result = op.setWeight(
                managed_date["value"], weight_menu.childWidgets["체중 입력"].obj.get()
            )
            if not result["ok"]:
                messagebox.showerror("체중 입력", result["message"])
                return
            pending_write_date["value"] = managed_date["value"]
            draw_write_calendar(op.showCalendarMonth(pending_write_date["value"]))
            write_calendar_frame.childWidgets["선택 날짜"].syncWidget()
            main_window.changePage("calendarWritePage")

        def apply_record_delete_style(widget, text, enabled=True):
            widget.style = {
                "text": text,
                "state": "normal" if enabled else "disabled",
                "bg": "#C45B74" if enabled else "#858CAD",
                "fg": "white",
                "disabledforeground": "#515A86",
                "font": ("Malgun Gothic", 9, "bold"),
                "activebackground": "#A63D58",
                "wraplength": 145,
            }

        def sync_record_delete_button(widget):
            has_record = op.hasSavedRecord(managed_date["value"])
            state = op.getRecordDeleteConfirmation(managed_date["value"])
            apply_record_delete_style(widget, state["text"], enabled=has_record)

        def tick_record_delete_confirmation(selected_date, token):
            state = op.tickRecordDeleteConfirmation(selected_date, token)
            delete_button = date_menu.childWidgets["삭제"]
            if state["active"]:
                apply_record_delete_style(delete_button, state["text"])
                delete_button.obj.after(
                    1000,
                    lambda: tick_record_delete_confirmation(selected_date, token),
                )
            else:
                sync_record_delete_button(delete_button)

        def click_record_delete(widget):
            selected_date = managed_date["value"]
            if not op.hasSavedRecord(selected_date):
                return
            state = op.getRecordDeleteConfirmation(selected_date)
            if state["active"]:
                try:
                    deleted = op.confirmDeleteRecord(selected_date, state["token"])
                except (OSError, ValueError, TypeError) as error:
                    messagebox.showerror(
                        "기록 삭제", f"기록을 삭제하지 못했습니다.\n{error}"
                    )
                    return
                if deleted:
                    op.cancelRecordManage()
                    main_window.changePage("defaultPage")
                    return
            state = op.beginRecordDeleteConfirmation(selected_date)
            if state["active"]:
                apply_record_delete_style(widget, state["text"])
                widget.obj.after(
                    1000,
                    lambda: tick_record_delete_confirmation(
                        selected_date, state["token"]
                    ),
                )

        date_menu.addChildWidget(
            name="삭제",
            widgetType="Button",
            style={"text": "삭제"},
            placeType="pack",
            placeAttribute={"side": "right", "fill": "y", "padx": 2},
            sync=sync_record_delete_button,
            event=click_record_delete,
        )

        date_menu.addChildWidget(
            name="조회",
            widgetType="Button",
            style={
                "text": "조회",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 12, "bold"),
                "activebackground": "#653CD6",
            },
            placeType="pack",
            placeAttribute={"side": "right", "fill": "y", "padx": 2},
            sync=no_sync,
            event=open_write_calendar,
        )

        record_frame.addChildWidget(
            name="시간대 식단",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1},
            sync=no_sync,
        )
        meal_grid = record_frame.childWidgets["시간대 식단"]
        for meal_layout in op.getMealCardLayout():
            meal = meal_layout["name"]
            meal_grid.addChildWidget(
                name=meal,
                widgetType="Frame",
                style={
                    "bg": "#D1D6FF",
                    "highlightbackground": "#919CFD",
                    "highlightthickness": 2,
                },
                placeType="place",
                placeAttribute=meal_layout["place"],
                sync=no_sync,
            )
            meal_card = meal_grid.childWidgets[meal]
            meal_card.addChildWidget(
                name="제목 메뉴",
                widgetType="Frame",
                style={"bg": "#D1D6FF", "height": 34},
                placeType="pack",
                placeAttribute={"fill": "x", "padx": 5, "pady": (4, 2)},
                sync=no_sync,
            )
            title_menu = meal_card.childWidgets["제목 메뉴"]
            title_menu.addChildWidget(
                name="제목",
                widgetType="Label",
                style={
                    "text": meal,
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "font": ("Malgun Gothic", 14, "bold"),
                    "anchor": "w",
                },
                placeType="pack",
                placeAttribute={"side": "left", "fill": "x", "expand": 1},
                sync=no_sync,
            )
            title_menu.addChildWidget(
                name="음식 관리",
                widgetType="Button",
                style={
                    "text": "음식 관리",
                    "bg": "#8C62FF",
                    "fg": "white",
                    "font": ("Malgun Gothic", 10, "bold"),
                    "activebackground": "#653CD6",
                },
                placeType="pack",
                placeAttribute={"side": "right"},
                sync=no_sync,
                event=lambda button, selected_meal=meal: open_food_manage(
                    selected_meal
                ),
            )
            meal_list_widgets[meal] = make_meal_scrollable_area(meal_card, meal)

        record_frame.addChildWidget(
            name="총 열량",
            widgetType="Label",
            style={
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 16, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (8, 5)},
            sync=sync_total_calories,
        )
        record_frame.addChildWidget(
            name="체중 입력 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 38},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (0, 6)},
            sync=no_sync,
        )
        weight_menu = record_frame.childWidgets["체중 입력 메뉴"]
        weight_menu.addChildWidget(
            name="체중 제목",
            widgetType="Label",
            style={
                "text": "입력 체중 (kg)",
                "bg": "#B7BEFF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 4},
            sync=no_sync,
        )

        def save_management_weight(widget):
            result = op.setWeight(
                managed_date["value"], weight_menu.childWidgets["체중 입력"].obj.get()
            )
            if not result["ok"]:
                messagebox.showerror("체중 입력", result["message"])
                return
            refresh_record_manage()
            defaultpage.widgets["식단표 프레임"].syncWidget()

        weight_menu.addChildWidget(
            name="체중 입력",
            widgetType="Entry",
            style={
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12),
                "justify": "center",
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "x", "expand": 1, "padx": 5},
            sync=sync_weight_entry,
        )
        weight_menu.addChildWidget(
            name="체중 반영값",
            widgetType="Label",
            style={
                "text": "저장된 체중: 미입력",
                "bg": "#B7BEFF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 5},
            sync=sync_weight_value,
        )
        weight_menu.addChildWidget(
            name="체중 저장",
            widgetType="Button",
            style={
                "text": "체중 반영",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "right", "padx": 2},
            sync=no_sync,
            event=save_management_weight,
        )

        record_frame.addChildWidget(
            name="관리 결정 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 44},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (3, 0)},
            sync=no_sync,
        )
        management_decision = record_frame.childWidgets["관리 결정 메뉴"]

        def save_weight_and_return(widget):
            result = op.setWeight(
                managed_date["value"], weight_menu.childWidgets["체중 입력"].obj.get()
            )
            if not result["ok"]:
                messagebox.showerror("체중 입력", result["message"])
                return
            try:
                op.commitRecordManage()
                op.setSelectedDate(managed_date["value"])
            except (OSError, ValueError, TypeError) as error:
                messagebox.showerror(
                    "기록 저장", f"기록을 저장하지 못했습니다.\n{error}"
                )
                return
            main_window.changePage("defaultPage")

        def cancel_record_management(widget):
            op.cancelFoodManage()
            op.cancelRecordManage()
            main_window.changePage("defaultPage")

        management_decision.addChildWidget(
            name="확인",
            widgetType="Button",
            style={
                "text": "확인",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12, "bold"),
                "activebackground": "#8997FF",
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=save_weight_and_return,
        )
        management_decision.addChildWidget(
            name="메인으로 돌아가기",
            widgetType="Button",
            style={
                "text": "메인으로 돌아가기",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12, "bold"),
                "activebackground": "#8997FF",
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=cancel_record_management,
        )

        calendarWritePage = main_window.pages["calendarWritePage"]
        write_calendar_frame = None
        write_days_frame = None
        write_navigation = None

        def sync_write_date(widget):
            widget.style = {
                "text": op.getDate(pending_write_date["value"]),
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 18, "bold"),
            }

        calendarWritePage.addWidget(
            name="달력 프레임",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "padx": 10, "pady": (34, 14)},
            sync=no_sync,
        )
        write_calendar_frame = calendarWritePage.widgets["달력 프레임"]
        write_calendar_frame.addChildWidget(
            name="달력 월",
            widgetType="Label",
            style={
                "text": "",
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 24, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (0, 14)},
            sync=no_sync,
        )
        write_calendar_frame.addChildWidget(
            name="요일 및 날짜",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1},
            sync=no_sync,
        )
        write_days_frame = write_calendar_frame.childWidgets["요일 및 날짜"]
        write_initial_calendar = op.showCalendarMonth(managed_date["value"])
        for weekday in write_initial_calendar["weekdays"]:
            write_days_frame.addChildWidget(
                name=f"요일 {weekday['text']}",
                widgetType="Label",
                style={
                    "text": weekday["text"],
                    "bg": "#8C62FF",
                    "fg": "white",
                    "font": ("Malgun Gothic", 13, "bold"),
                },
                placeType="place",
                placeAttribute=weekday["place"],
                sync=no_sync,
            )
        for cell in write_initial_calendar["days"]:
            write_days_frame.addChildWidget(
                name=f"날짜 {cell['row']}-{cell['column']}",
                widgetType="Button",
                style={
                    "text": cell["text"],
                    "state": cell["state"],
                    "bg": "#D1D6FF",
                    "fg": "#626FCB",
                    "font": ("Malgun Gothic", 11, "bold"),
                    "anchor": "nw",
                    "justify": "left",
                },
                placeType="place",
                placeAttribute=cell["place"],
                sync=no_sync,
                event=lambda button: None,
            )
        write_calendar_frame.addChildWidget(
            name="달력 이동 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 44},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (14, 0)},
            sync=no_sync,
        )
        write_navigation = write_calendar_frame.childWidgets["달력 이동 메뉴"]
        write_navigation.addChildWidget(
            name="이전 달",
            widgetType="Button",
            style={
                "text": "◀",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 14, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda button: change_write_month(-1),
        )
        write_navigation.addChildWidget(
            name="다음 달",
            widgetType="Button",
            style={
                "text": "▶",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 14, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda button: change_write_month(1),
        )

        def draw_write_calendar(calendar_data):
            write_calendar_frame.childWidgets["달력 월"].style = {
                "text": calendar_data["title"],
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 24, "bold"),
            }
            weekday_colors = {
                "weekday": "#626FCB",
                "saturday": "#4E79C7",
                "sunday": "#C45B74",
            }
            for cell in calendar_data["days"]:
                day_widget = write_days_frame.childWidgets[
                    f"날짜 {cell['row']}-{cell['column']}"
                ]
                if not cell["in_range"]:
                    background = "#858CAD"
                elif cell["selected"]:
                    background = "#AAB3FF"
                elif cell["has_record"]:
                    background = "#D1D6FF"
                else:
                    background = "#E6E9FF"
                day_widget.style = {
                    "text": cell["text"],
                    "state": cell["state"],
                    "bg": background,
                    "fg": weekday_colors[cell["weekday_type"]],
                    "disabledforeground": weekday_colors[cell["weekday_type"]],
                    "activebackground": "#8997FF",
                    "font": ("Malgun Gothic", 11, "bold"),
                    "anchor": "nw",
                    "justify": "left",
                }
                if cell["in_range"] and cell["date"] is not None:
                    day_widget.event = lambda button, chosen=cell["date"]: (
                        select_write_date(chosen)
                    )
                else:
                    day_widget.event = lambda button: None

            previous_button = write_navigation.childWidgets["이전 달"]
            previous_button.style = {
                "text": "◀",
                "state": "normal" if calendar_data["can_previous"] else "disabled",
                "bg": "#D1D6FF" if calendar_data["can_previous"] else "#858CAD",
                "fg": "#626FCB" if calendar_data["can_previous"] else "#515A86",
                "disabledforeground": "#515A86",
                "font": ("Malgun Gothic", 14, "bold"),
            }

        def select_write_date(selected):
            pending_write_date["value"] = selected
            draw_write_calendar(op.getCalendar(selected))
            write_calendar_frame.childWidgets["선택 날짜"].syncWidget()

        def change_write_month(offset):
            draw_write_calendar(
                op.changeCalendarMonth(offset, pending_write_date["value"])
            )

        write_calendar_frame.addChildWidget(
            name="선택 날짜",
            widgetType="Label",
            style={
                "bg": "#B7BEFF",
                "fg": "white",
                "font": ("Malgun Gothic", 18, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (8, 0)},
            sync=sync_write_date,
        )
        write_calendar_frame.addChildWidget(
            name="기록 날짜 결정 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 46},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (12, 0)},
            sync=no_sync,
        )
        write_decision_menu = write_calendar_frame.childWidgets["기록 날짜 결정 메뉴"]

        def confirm_write_date(widget):
            op.setSelectedDate(pending_write_date["value"])
            managed_date["value"] = pending_write_date["value"]
            op.beginRecordManage(managed_date["value"])
            refresh_record_manage()
            main_window.changePage("recordManagePage")

        write_decision_menu.addChildWidget(
            name="확인",
            widgetType="Button",
            style={
                "text": "확인",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 13, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=confirm_write_date,
        )
        write_decision_menu.addChildWidget(
            name="취소",
            widgetType="Button",
            style={
                "text": "취소",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 13, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=lambda button: main_window.changePage("recordManagePage"),
        )

        draw_write_calendar(write_initial_calendar)

        foodManagePage = main_window.pages["foodManagePage"]

        def sync_food_manage_title(widget):
            widget.style = {
                "text": op.getFoodManageState()["title"],
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 15, "bold"),
                "anchor": "w",
            }

        def sync_food_search_entry(widget):
            query = op.getFoodManageState()["query"]
            widget.obj.delete(0, "end")
            if query:
                widget.obj.insert(0, query)

        def apply_food_delete_style(widget, confirmation):
            active = confirmation["active"]
            widget.style = {
                "text": confirmation["text"] if active else "X",
                "width": 8,
                "height": 3,
                "wraplength": 60,
                "justify": "center",
                "bg": "#E6A2B2" if active else "#C45B74",
                "fg": "white",
                "font": ("Malgun Gothic", 8, "bold"),
                "activebackground": "#A63D58",
            }

        def sync_food_results(widget):
            for child in list(widget.childWidgets.values()):
                child.destroy()
            widget.childWidgets.clear()
            foods = op.getFoodManageState()["results"]
            if not foods:
                widget.addChildWidget(
                    name="검색 결과 없음",
                    widgetType="Label",
                    style={
                        "text": "검색 결과가 없습니다.",
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 11),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 3},
                    sync=no_sync,
                )
                return

            for index, food in enumerate(foods):
                widget.addChildWidget(
                    name=f"검색 결과 {index}",
                    widgetType="Frame",
                    style={"bg": "#D1D6FF", "height": 42},
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 2},
                    sync=no_sync,
                )
                row = widget.childWidgets[f"검색 결과 {index}"]
                row.addChildWidget(
                    name="음식 정보",
                    widgetType="Label",
                    style={
                        "text": food["text"],
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 11),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={
                        "side": "left",
                        "fill": "x",
                        "expand": 1,
                        "padx": 5,
                    },
                    sync=no_sync,
                )
                row.addChildWidget(
                    name="대기열 추가",
                    widgetType="Button",
                    style={
                        "text": "+",
                        "width": 8,
                        "height": 3,
                        "bg": "#8C62FF",
                        "fg": "white",
                        "font": ("Malgun Gothic", 8, "bold"),
                    },
                    placeType="pack",
                    placeAttribute={"side": "right", "padx": 2},
                    sync=no_sync,
                    event=lambda button, food_id=food["id"]: add_food_to_queue(food_id),
                )
                row.addChildWidget(
                    name="음식 삭제",
                    widgetType="Button",
                    style={"text": "X"},
                    placeType="pack",
                    placeAttribute={"side": "right", "padx": 2},
                    sync=no_sync,
                    event=lambda button, food_id=food["id"]: click_food_delete(
                        button, food_id
                    ),
                )
                apply_food_delete_style(
                    row.childWidgets["음식 삭제"], food["delete_confirmation"]
                )

        def sync_food_queue(widget):
            for child in list(widget.childWidgets.values()):
                child.destroy()
            widget.childWidgets.clear()
            queued_foods = op.getFoodManageState()["queue"]
            if not queued_foods:
                widget.addChildWidget(
                    name="대기열 비어 있음",
                    widgetType="Label",
                    style={
                        "text": "대기 중인 음식이 없습니다.",
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 10),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 2},
                    sync=no_sync,
                )
                return

            for item in queued_foods:
                widget.addChildWidget(
                    name=f"대기 음식 {item['index']}",
                    widgetType="Frame",
                    style={"bg": "#D1D6FF", "height": 30},
                    placeType="pack",
                    placeAttribute={"fill": "x", "pady": 1},
                    sync=no_sync,
                )
                row = widget.childWidgets[f"대기 음식 {item['index']}"]
                row.addChildWidget(
                    name="음식 정보",
                    widgetType="Label",
                    style={
                        "text": item["text"],
                        "bg": "#D1D6FF",
                        "fg": "#626FCB",
                        "font": ("Malgun Gothic", 10),
                        "anchor": "w",
                    },
                    placeType="pack",
                    placeAttribute={
                        "side": "left",
                        "fill": "x",
                        "expand": 1,
                        "padx": 5,
                    },
                    sync=no_sync,
                )
                row.addChildWidget(
                    name="대기열에서 제거",
                    widgetType="Button",
                    style={
                        "text": "X",
                        "bg": "#C45B74",
                        "fg": "white",
                        "width": 3,
                    },
                    placeType="pack",
                    placeAttribute={"side": "right", "padx": 2},
                    sync=no_sync,
                    event=lambda button, item_index=item["index"]: remove_queued_food(
                        item_index
                    ),
                )

        def refresh_food_manage_lists():
            food_results_content.syncWidget()
            food_queue_content.syncWidget()

        def add_food_to_queue(food_id):
            if op.addFoodToQueue(food_id):
                food_queue_content.syncWidget()

        def remove_queued_food(item_index):
            op.removeFoodFromQueue(item_index)
            food_queue_content.syncWidget()

        def tick_food_delete_confirmation(food_id, token):
            state = op.tickFoodDeleteConfirmation(food_id, token)
            food_results_content.syncWidget()
            if state["active"]:
                food_page_root.obj.after(
                    1000,
                    lambda: tick_food_delete_confirmation(food_id, token),
                )

        def click_food_delete(widget, food_id):
            state = op.getFoodDeleteConfirmation(food_id)
            if state["active"]:
                try:
                    deleted = op.confirmDeleteFood(food_id, state["token"])
                except (OSError, ValueError, TypeError) as error:
                    messagebox.showerror(
                        "음식 삭제", f"음식을 삭제하지 못했습니다.\n{error}"
                    )
                    return
                if deleted:
                    refresh_food_manage_lists()
                    return
            state = op.beginFoodDeleteConfirmation(food_id)
            if state["active"]:
                apply_food_delete_style(widget, state)
                food_page_root.obj.after(
                    1000,
                    lambda: tick_food_delete_confirmation(food_id, state["token"]),
                )

        def submit_food_search(widget):
            query = food_search_widget.obj.get().strip()
            if not query:
                messagebox.showinfo(
                    "음식 검색", "값이 없어 전체 항목이 정렬됩니다"
                )
            op.searchFoods(query)
            food_results_content.syncWidget()

        def sync_clear_entry(widget):
            widget.obj.delete(0, "end")

        def sync_food_search_results(widget):
            widget.style = {
                "text": "검색",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 11, "bold"),
            }

        def create_new_food(widget):
            try:
                result = op.createFood(
                    food_name_entry.obj.get(), food_calories_entry.obj.get()
                )
            except (OSError, ValueError, TypeError) as error:
                messagebox.showerror(
                    "음식 추가", f"음식을 저장하지 못했습니다.\n{error}"
                )
                return
            if not result["ok"]:
                messagebox.showerror("음식 추가", result["message"])
                return
            refresh_food_manage_lists()
            food_name_entry.obj.delete(0, "end")
            food_calories_entry.obj.delete(0, "end")
            for child in food_create_frame.childWidgets.values():
                if child is not food_create_success:
                    child.hideWidget()
            food_create_success.placeWidget()
            food_add_button.obj.after(2000, restore_food_create_form)

        def restore_food_create_form():
            food_create_success.hideWidget()
            for name in (
                "음식 이름 제목",
                "음식 이름 입력",
                "열량 제목",
                "열량 입력",
                "추가",
            ):
                food_create_frame.childWidgets[name].placeWidget()

        def sync_food_add_button(widget):
            widget.style = {
                "text": "추가",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 10, "bold"),
            }

        foodManagePage.addWidget(
            name="음식 관리 프레임",
            widgetType="Frame",
            style={"bg": "#B7BEFF"},
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1, "padx": 10, "pady": 8},
            sync=no_sync,
        )
        food_page_root = foodManagePage.widgets["음식 관리 프레임"]

        food_page_root.addChildWidget(
            name="검색 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 42},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (0, 5)},
            sync=no_sync,
        )
        food_search_row = food_page_root.childWidgets["검색 메뉴"]
        food_search_row.addChildWidget(
            name="검색 입력",
            widgetType="Entry",
            style={
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12),
            },
            placeType="pack",
            placeAttribute={
                "side": "left",
                "fill": "both",
                "expand": 1,
                "padx": (0, 5),
            },
            sync=sync_food_search_entry,
        )
        food_search_widget = food_search_row.childWidgets["검색 입력"]
        food_search_row.addChildWidget(
            name="검색 버튼",
            widgetType="Button",
            style={
                "text": "검색",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 11, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "right", "fill": "y"},
            sync=sync_food_search_results,
            event=submit_food_search,
        )

        def make_scrollable_area(parent, name, fixed_height=None, content_sync=no_sync):
            style = {"bg": "#B7BEFF"}
            place = {"fill": "both", "expand": 1}
            if fixed_height is not None:
                style["height"] = fixed_height
                place = {"fill": "x", "pady": (0, 3)}
            parent.addChildWidget(
                name=name,
                widgetType="Frame",
                style=style,
                placeType="pack",
                placeAttribute=place,
                sync=no_sync,
            )
            outer = parent.childWidgets[name]
            if fixed_height is not None:
                outer.obj.pack_propagate(False)
            outer.addChildWidget(
                name="내용 캔버스",
                widgetType="Canvas",
                style={"bg": "#D1D6FF", "highlightthickness": 0},
                placeType="pack",
                placeAttribute={"side": "left", "fill": "both", "expand": 1},
                sync=no_sync,
            )
            outer.addChildWidget(
                name="세로 스크롤",
                widgetType="Scrollbar",
                style={"orient": "vertical"},
                placeType="pack",
                placeAttribute={"side": "right", "fill": "y"},
                sync=no_sync,
            )
            canvas = outer.childWidgets["내용 캔버스"]
            scrollbar = outer.childWidgets["세로 스크롤"]
            canvas.obj.configure(yscrollcommand=scrollbar.obj.set)
            scrollbar.obj.configure(command=canvas.obj.yview)
            canvas.addChildWidget(
                name="목록 내용",
                widgetType="Frame",
                style={"bg": "#D1D6FF"},
                placeType=None,
                placeAttribute={},
                sync=content_sync,
            )
            content = canvas.childWidgets["목록 내용"]
            window_id = canvas.obj.create_window(
                (0, 0), window=content.obj, anchor="nw"
            )
            content.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj: target.configure(
                    scrollregion=target.bbox("all")
                ),
            )
            canvas.obj.bind(
                "<Configure>",
                lambda event, target=canvas.obj, item=window_id: target.itemconfigure(
                    item, width=event.width
                ),
            )
            return outer, content

        food_results_area, food_results_content = make_scrollable_area(
            food_page_root,
            "검색 결과 목록",
            content_sync=sync_food_results,
        )

        food_page_root.addChildWidget(
            name="음식 추가 프레임",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 42},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (4, 4)},
            sync=no_sync,
        )
        food_create_frame = food_page_root.childWidgets["음식 추가 프레임"]
        food_create_frame.addChildWidget(
            name="음식 이름 제목",
            widgetType="Label",
            style={
                "text": "이름",
                "bg": "#B7BEFF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 2},
            sync=no_sync,
        )
        food_create_frame.addChildWidget(
            name="음식 이름 입력",
            widgetType="Entry",
            style={
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10),
                "width": 16,
            },
            placeType="pack",
            placeAttribute={"side": "left", "fill": "x", "expand": 1, "padx": 3},
            sync=sync_clear_entry,
        )
        food_name_entry = food_create_frame.childWidgets["음식 이름 입력"]
        food_create_frame.addChildWidget(
            name="열량 제목",
            widgetType="Label",
            style={
                "text": "열량(kcal)",
                "bg": "#B7BEFF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 2},
            sync=no_sync,
        )
        food_create_frame.addChildWidget(
            name="열량 입력",
            widgetType="Entry",
            style={
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 10),
                "width": 8,
            },
            placeType="pack",
            placeAttribute={"side": "left", "padx": 3},
            sync=sync_clear_entry,
        )
        food_calories_entry = food_create_frame.childWidgets["열량 입력"]
        food_create_frame.addChildWidget(
            name="추가",
            widgetType="Button",
            style={
                "text": "추가",
                "bg": "#8C62FF",
                "fg": "white",
                "font": ("Malgun Gothic", 10, "bold"),
            },
            placeType="pack",
            placeAttribute={"side": "right", "padx": 2},
            sync=sync_food_add_button,
            event=create_new_food,
        )
        food_add_button = food_create_frame.childWidgets["추가"]
        food_create_frame.addChildWidget(
            name="추가 성공 메시지",
            widgetType="Label",
            style={
                "text": "추가 되었습니다!",
                "bg": "#B7BEFF",
                "fg": "#41A169",
                "font": ("Malgun Gothic", 13, "bold"),
            },
            placeType="pack",
            placeAttribute={"fill": "both", "expand": 1},
            sync=no_sync,
        )
        food_create_success = food_create_frame.childWidgets["추가 성공 메시지"]
        food_create_success.hideWidget()

        food_page_root.addChildWidget(
            name="대기열 제목",
            widgetType="Label",
            style={
                "text": "식단 대기열",
                "bg": "#8C62FF",
                "fg": "#D9DDFF",
                "font": ("Malgun Gothic", 14, "bold"),
                "anchor": "w",
            },
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (2, 3)},
            sync=sync_food_manage_title,
        )
        food_queue_area, food_queue_content = make_scrollable_area(
            food_page_root,
            "식단 대기열 목록",
            fixed_height=130,
            content_sync=sync_food_queue,
        )

        food_page_root.addChildWidget(
            name="확인 취소 메뉴",
            widgetType="Frame",
            style={"bg": "#B7BEFF", "height": 44},
            placeType="pack",
            placeAttribute={"fill": "x", "pady": (5, 0)},
            sync=no_sync,
        )
        food_decision_menu = food_page_root.childWidgets["확인 취소 메뉴"]

        def confirm_food_manage(widget):
            if op.commitFoodManage():
                refresh_record_manage()
                main_window.changePage("recordManagePage")

        def cancel_food_manage(widget):
            op.cancelFoodManage()
            main_window.changePage("recordManagePage")

        food_decision_menu.addChildWidget(
            name="확인",
            widgetType="Button",
            style={
                "text": "확인",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=confirm_food_manage,
        )
        food_decision_menu.addChildWidget(
            name="취소",
            widgetType="Button",
            style={
                "text": "취소",
                "bg": "#D1D6FF",
                "fg": "#626FCB",
                "font": ("Malgun Gothic", 12, "bold"),
            },
            placeType="place",
            placeAttribute={
                "relx": 0.5,
                "relwidth": 0.5,
                "relheight": 1,
                "x": 1,
                "width": -2,
            },
            sync=no_sync,
            event=cancel_food_manage,
        )

        main_window.changePage("defaultPage")

        main_window.obj.mainloop()
