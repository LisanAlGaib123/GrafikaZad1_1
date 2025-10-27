
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import math

class Drawable:
    HANDLE_SIZE = 6

    def __init__(self, obj_id=None, color='black', width=2):
        self.obj_id = obj_id
        self.color = color
        self.width = width
        self.selected = False

    def draw(self, canvas):
        raise NotImplementedError

    def bbox(self):
        raise NotImplementedError

    def contains_point(self, x, y):
        raise NotImplementedError

    def move(self, dx, dy):
        raise NotImplementedError

    def handles(self):
        x1,y1,x2,y2 = self.bbox()
        return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        typ = data.get('type')
        if typ == 'line':
            return Line.from_dict(data)
        elif typ == 'rect':
            return Rect.from_dict(data)
        elif typ == 'circle':
            return Circle.from_dict(data)
        else:
            raise ValueError('Unknown type')

class Line(Drawable):
    def __init__(self, x1, y1, x2, y2, color='black', width=2, obj_id=None):
        super().__init__(obj_id, color, width)
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2

    def draw(self, canvas):
        kw = {'fill':self.color, 'width':self.width}
        canvas.create_line(self.x1,self.y1,self.x2,self.y2, **kw)
        if self.selected:
            self._draw_handles(canvas)

    def _draw_handles(self, canvas):
        for (x,y) in [(self.x1,self.y1),(self.x2,self.y2)]:
            canvas.create_rectangle(x-self.HANDLE_SIZE, y-self.HANDLE_SIZE,
                                    x+self.HANDLE_SIZE, y+self.HANDLE_SIZE,
                                    outline='blue')

    def bbox(self):
        return (min(self.x1,self.x2), min(self.y1,self.y2), max(self.x1,self.x2), max(self.y1,self.y2))

    def contains_point(self, x, y):
        px,py = x,y
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
        dx,dy = x2-x1, y2-y1
        if dx==0 and dy==0:
            return (abs(px-x1) <= 5 and abs(py-y1) <=5)
        t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx+dy*dy)
        t = max(0, min(1,t))
        projx = x1 + t*dx
        projy = y1 + t*dy
        dist = math.hypot(px-projx, py-projy)
        return dist <= max(6, self.width+3)

    def move(self, dx, dy):
        self.x1 += dx; self.y1 += dy; self.x2 += dx; self.y2 += dy

    def resize(self, handle_index, x, y):
        if handle_index == 0:
            self.x1, self.y1 = x, y
        else:
            self.x2, self.y2 = x, y

    def to_dict(self):
        return {'type':'line','x1':self.x1,'y1':self.y1,'x2':self.x2,'y2':self.y2,'color':self.color,'width':self.width}

    @classmethod
    def from_dict(cls, d):
        return Line(d['x1'],d['y1'],d['x2'],d['y2'], d.get('color','black'), d.get('width',2))

class Rect(Drawable):
    def __init__(self, x1, y1, x2, y2, color='black', width=2, fill=''):
        super().__init__(None, color, width)
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
        self.fill = fill

    def draw(self, canvas):
        kw = {'outline':self.color, 'width':self.width}
        if self.fill:
            kw['fill'] = self.fill
        canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2, **kw)
        if self.selected:
            self._draw_handles(canvas)

    def _draw_handles(self, canvas):
        for (x,y) in self.handles():
            canvas.create_rectangle(x-self.HANDLE_SIZE, y-self.HANDLE_SIZE,
                                    x+self.HANDLE_SIZE, y+self.HANDLE_SIZE,
                                    outline='blue')

    def bbox(self):
        return (min(self.x1,self.x2), min(self.y1,self.y2), max(self.x1,self.x2), max(self.y1,self.y2))

    def contains_point(self, x, y):
        x1,y1,x2,y2 = self.bbox()
        return x1 <= x <= x2 and y1 <= y <= y2

    def move(self, dx, dy):
        self.x1 += dx; self.y1 += dy; self.x2 += dx; self.y2 += dy

    def resize(self, handle_index, x, y):
        if handle_index == 0:
            self.x1, self.y1 = x, y
        elif handle_index == 1:
            self.x2, self.y1 = x, y
        elif handle_index == 2:
            self.x2, self.y2 = x, y
        elif handle_index == 3:
            self.x1, self.y2 = x, y

    def to_dict(self):
        return {'type':'rect','x1':self.x1,'y1':self.y1,'x2':self.x2,'y2':self.y2,'color':self.color,'width':self.width,'fill':self.fill}

    @classmethod
    def from_dict(cls, d):
        return Rect(d['x1'],d['y1'],d['x2'],d['y2'], d.get('color','black'), d.get('width',2), d.get('fill',''))

class Circle(Drawable):
    def __init__(self, cx, cy, r, color='black', width=2, fill=''):
        super().__init__(None, color, width)
        self.cx,self.cy,self.r = cx,cy,r
        self.fill = fill

    def draw(self, canvas):
        x1,y1,x2,y2 = self.bbox()
        kw = {'outline':self.color, 'width':self.width}
        if self.fill:
            kw['fill'] = self.fill
        canvas.create_oval(x1,y1,x2,y2, **kw)
        if self.selected:
            self._draw_handles(canvas)

    def _draw_handles(self, canvas):
        for (x,y) in self.handles():
            canvas.create_rectangle(x-self.HANDLE_SIZE, y-self.HANDLE_SIZE,
                                    x+self.HANDLE_SIZE, y+self.HANDLE_SIZE,
                                    outline='blue')

    def bbox(self):
        return (self.cx-self.r, self.cy-self.r, self.cx+self.r, self.cy+self.r)

    def contains_point(self, x, y):
        return math.hypot(x-self.cx, y-self.cy) <= self.r + max(6, self.width)

    def handles(self):
        # tylko jeden uchwyt na obwodzie (np. po prawej stronie)
        return [(self.cx + self.r, self.cy)]

    def move(self, dx, dy):
        self.cx += dx; self.cy += dy

    def resize(self, handle, x, y):
        # zmiana promienia na podstawie odległości od środka do punktu uchwytu
        dx = x - self.cx
        dy = y - self.cy
        self.r = max(2, (dx ** 2 + dy ** 2) ** 0.5)

    def to_dict(self):
        return {'type':'circle','cx':self.cx,'cy':self.cy,'r':self.r,'color':self.color,'width':self.width,'fill':self.fill}

    @classmethod
    def from_dict(cls, d):
        return Circle(d['cx'], d['cy'], d['r'], d.get('color','black'), d.get('width',2), d.get('fill',''))

# --- Aplikacja GUI ---
class App:
    def __init__(self, root):
        self.root = root
        root.title('Prymitywy graficzne')
        self.objects = []
        self.mode = 'select'
        self.current_preview = None
        self.selected = None
        self.dragging = False
        self.drag_start = (0,0)
        self.resize_handle = None

        self._build_ui()
        self._bind_events()
        self.redraw()

    def _build_ui(self):
        frm = tk.Frame(self.root)
        frm.pack(side='top', fill='x')

        tk.Button(frm, text='Wybierz', command=lambda: self.set_mode('select')).pack(side='left')
        tk.Button(frm, text='Rysuj linię', command=lambda: self.set_mode('draw_line')).pack(side='left')
        tk.Button(frm, text='Rysuj prostokąt', command=lambda: self.set_mode('draw_rect')).pack(side='left')
        tk.Button(frm, text='Rysuj okrąg', command=lambda: self.set_mode('draw_circle')).pack(side='left')
        tk.Button(frm, text='Usuń', command=self.delete_selected).pack(side='left')
        tk.Button(frm, text='Wyczyść', command=self.clear_canvas).pack(side='left')
        tk.Button(frm, text='Zapisz', command=self.save).pack(side='left')
        tk.Button(frm, text='Otwórz', command=self.load).pack(side='left')

        param_frame = tk.LabelFrame(self.root, text='Parametry / Nowy / Edytuj')
        param_frame.pack(side='left', fill='y', padx=4, pady=4)

        tk.Label(param_frame, text='Typ:').grid(row=0, column=0, sticky='w')
        self.type_var = tk.StringVar(value='line')
        tk.OptionMenu(param_frame, self.type_var, 'line','rect','circle').grid(row=0,column=1,sticky='w')

        tk.Label(param_frame, text='Parametry (CSV):').grid(row=1, column=0, columnspan=2, sticky='w')
        self.params_entry = tk.Entry(param_frame, width=25)
        self.params_entry.grid(row=2, column=0, columnspan=2)
        tk.Button(param_frame, text='Rysuj z parametrów', command=self.create_from_params).grid(row=3, column=0, columnspan=2, pady=4)

        tk.Label(param_frame, text='Kolor:').grid(row=4,column=0,sticky='w')
        self.color_entry = tk.Entry(param_frame)
        self.color_entry.grid(row=4,column=1)
        tk.Label(param_frame, text='Szerokość:').grid(row=5,column=0,sticky='w')
        self.width_entry = tk.Entry(param_frame)
        self.width_entry.grid(row=5,column=1)

        tk.Button(param_frame, text='Zastosuj do zaznaczonego', command=self.apply_params).grid(row=6,column=0,columnspan=2,pady=4)

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack(side='right', expand=True, fill='both')

        self.status = tk.StringVar()
        self.status.set('Tryb: select')
        tk.Label(self.root, textvariable=self.status).pack(side='bottom', fill='x')

    def _bind_events(self):
        c = self.canvas
        c.bind('<Button-1>', self.on_click)
        c.bind('<B1-Motion>', self.on_drag)
        c.bind('<ButtonRelease-1>', self.on_release)
        c.bind('<Double-Button-1>', self.on_double)

    def set_mode(self, mode):
        self.mode = mode
        self.status.set('Tryb: ' + mode)
        self.deselect_all()
        self.redraw()

    def clear_canvas(self):
        self.objects.clear()
        self.deselect_all()
        self.redraw()

    def delete_selected(self):
        if self.selected:
            self.objects.remove(self.selected)
            self.selected = None
            self.redraw()

    def on_click(self, event):
        x,y = event.x,event.y
        if self.mode.startswith('draw'):
            self.dragging = True
            self.drag_start = (x,y)
            if self.mode == 'draw_line':
                self.current_preview = Line(x,y,x,y)
            elif self.mode == 'draw_rect':
                self.current_preview = Rect(x,y,x,y)
            elif self.mode == 'draw_circle':
                self.current_preview = Circle(x,y,0)
            self.redraw()
        else:
            obj = self.find_object_at(x,y)
            if obj:
                self.selected = obj
                obj.selected = True
                self.resize_handle = self._which_handle(obj, x, y)
                self.dragging = True
                self.drag_start = (x,y)
            else:
                self.deselect_all()
            self.redraw()

    def on_drag(self, event):
        x,y = event.x,event.y
        if self.mode.startswith('draw') and self.dragging and self.current_preview:
            x0,y0 = self.drag_start
            if isinstance(self.current_preview, Line):
                self.current_preview.x2,self.current_preview.y2 = x,y
            elif isinstance(self.current_preview, Rect):
                self.current_preview.x2,self.current_preview.y2 = x,y
            elif isinstance(self.current_preview, Circle):
                r = math.hypot(x-x0,y-y0)
                self.current_preview.r = r
            self.redraw()
        elif self.mode == 'select' and self.dragging and self.selected:
            x0,y0 = self.drag_start
            dx,dy = x-x0,y-y0
            if self.resize_handle is not None:
                self.selected.resize(self.resize_handle, x, y)
            else:
                self.selected.move(dx,dy)
                self.drag_start = (x,y)
            self.redraw()

    def on_release(self, event):
        if self.mode.startswith('draw') and self.current_preview:
            self.objects.append(self.current_preview)
            self.current_preview = None
        self.dragging = False
        self.resize_handle = None
        self.redraw()

    def on_double(self, event):
        obj = self.find_object_at(event.x,event.y)
        if obj:
            self.selected = obj
            obj.selected = True
            self.redraw()

    def find_object_at(self, x, y):
        for obj in reversed(self.objects):
            if obj.contains_point(x,y):
                return obj
        return None

    def _which_handle(self, obj, x, y):
        for i,(hx,hy) in enumerate(obj.handles()):
            if abs(hx-x)<=Drawable.HANDLE_SIZE and abs(hy-y)<=Drawable.HANDLE_SIZE:
                return i
        return None

    def create_from_params(self):
        typ = self.type_var.get()
        params = self.params_entry.get().strip()
        try:
            nums = [float(v.strip()) for v in params.split(',') if v.strip()!='']
        except:
            messagebox.showerror('Błąd', 'Niepoprawne dane parametru')
            return
        color = self.color_entry.get().strip() or 'black'
        width = float(self.width_entry.get().strip() or 2)
        try:
            if typ == 'line' and len(nums)>=4:
                obj = Line(*nums[:4], color=color, width=width)
            elif typ == 'rect' and len(nums)>=4:
                obj = Rect(*nums[:4], color=color, width=width)
            elif typ == 'circle' and len(nums)>=3:
                obj = Circle(*nums[:3], color=color, width=width)
            else:
                messagebox.showerror('Błąd', 'Niepoprawne parametry')
                return
            self.objects.append(obj)
            self.redraw()
        except Exception as e:
            messagebox.showerror('Błąd', str(e))

    def apply_params(self):
        if not self.selected:
            messagebox.showinfo('Brak obiektu', 'Najpierw wybierz obiekt')
            return
        params = self.params_entry.get().strip()
        try:
            nums = [float(s.strip()) for s in params.split(',') if s.strip()!='']
        except Exception:
            messagebox.showerror('Błąd', 'Niepoprawne parametry (użyj CSV)')
            return
        try:
            if isinstance(self.selected, Line) and len(nums) >=4:
                self.selected.x1,self.selected.y1,self.selected.x2,self.selected.y2 = nums[:4]
            elif isinstance(self.selected, Rect) and len(nums)>=4:
                self.selected.x1,self.selected.y1,self.selected.x2,self.selected.y2 = nums[:4]
            elif isinstance(self.selected, Circle) and len(nums)>=3:
                self.selected.cx,self.selected.cy,self.selected.r = nums[:3]
            c = self.color_entry.get().strip()
            if c:
                self.selected.color = c
            w = self.width_entry.get().strip()
            if w:
                self.selected.width = float(w)
            self.update_param_panel()
            self.redraw()
        except Exception as e:
            messagebox.showerror('Błąd', f'Nie udało się zastosować parametrów:{e}')

    def deselect_all(self):
        for o in self.objects:
            o.selected = False
        self.selected = None
        self.update_param_panel()

    def update_param_panel(self):
        if self.selected:
            if isinstance(self.selected, Line):
                self.type_var.set('line')
                self.params_entry.delete(0, 'end')
                self.params_entry.insert(0, f'{self.selected.x1},{self.selected.y1},{self.selected.x2},{self.selected.y2}')
            elif isinstance(self.selected, Rect):
                self.type_var.set('rect')
                self.params_entry.delete(0,'end')
                self.params_entry.insert(0, f'{self.selected.x1},{self.selected.y1},{self.selected.x2},{self.selected.y2}')
            elif isinstance(self.selected, Circle):
                self.type_var.set('circle')
                self.params_entry.delete(0,'end')
                self.params_entry.insert(0, f'{self.selected.cx},{self.selected.cy},{self.selected.r}')
            self.color_entry.delete(0,'end'); self.color_entry.insert(0,self.selected.color)
            self.width_entry.delete(0,'end'); self.width_entry.insert(0,str(self.selected.width))
        else:
            # clear inputs but keep selected type from optionmenu
            self.params_entry.delete(0,'end')
            self.color_entry.delete(0,'end')
            self.width_entry.delete(0,'end')

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')])
        if not path:
            return
        try:
            data = [o.to_dict() for o in self.objects]
            with open(path,'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo('Zapisano', 'Zapisano plik')
        except Exception as e:
            messagebox.showerror('Błąd', f'Błąd podczas zapisu:{e}')

    def load(self):
        path = filedialog.askopenfilename(filetypes=[('JSON files','*.json')])
        if not path:
            return
        try:
            with open(path,'r', encoding='utf-8') as f:
                data = json.load(f)
            self.objects = [Drawable.from_dict(d) for d in data]
            self.deselect_all()
            self.redraw()
            messagebox.showinfo('Wczytano', 'Plik wczytany')
        except Exception as e:
            messagebox.showerror('Błąd', f'Błąd podczas wczytywania:{e}')

    def redraw(self):
        self.canvas.delete('all')
        for obj in self.objects:
            obj.draw(self.canvas)
        if self.current_preview:
            if isinstance(self.current_preview, Line):
                self.canvas.create_line(self.current_preview.x1,self.current_preview.y1,self.current_preview.x2,self.current_preview.y2, fill='gray', dash=(4,2))
            elif isinstance(self.current_preview, Rect):
                self.canvas.create_rectangle(self.current_preview.x1,self.current_preview.y1,self.current_preview.x2,self.current_preview.y2, outline='gray', dash=(4,2))
            elif isinstance(self.current_preview, Circle):
                x1,y1,x2,y2 = self.current_preview.bbox()
                self.canvas.create_oval(x1,y1,x2,y2, outline='gray', dash=(4,2))
        if self.selected:
            x1,y1,x2,y2 = self.selected.bbox()
            self.canvas.create_rectangle(x1,y1,x2,y2, outline='blue', dash=(2,2))
            for hx,hy in self.selected.handles():
                self.canvas.create_rectangle(hx-Drawable.HANDLE_SIZE, hy-Drawable.HANDLE_SIZE, hx+Drawable.HANDLE_SIZE, hy+Drawable.HANDLE_SIZE, outline='blue')

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
