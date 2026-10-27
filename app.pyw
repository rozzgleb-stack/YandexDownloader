# -*- coding: utf-8 -*-
"""Yandex Downloader 6.4 — made by glebasya32.

A four-language Windows desktop downloader with a clean interface and tactile 3D buttons.
Networking uses engine.py (stdlib, with public folder validation).
"""
from __future__ import annotations
from collections import deque
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

from engine import APP_VERSION, Task, Meter, parse_folder_link, folder_details, enumerate_folder, clean_name, human, eta_text, execute_tasks
from i18n import LANG_NAMES, tr, translate_exception, size_text, eta_locale
from PIL import Image, ImageDraw, ImageFilter, ImageTk

DONATE_URL='https://www.donationalerts.com/r/glebasya322'
BG='#F4F6FA'; SURFACE='#FFFFFF'; WHITE='#FFFFFF'; INK='#171A22'; MUTED='#647084'; LINE='#E1E7F0'; PALE='#EFF3F9'; BLUE='#1674EF'; GLOW='#D5E7FF'
STATE_CODES = {'Загрузка':'working','downloaded':'downloaded','skipped':'skipped','failed':'failed','cancelled':'cancelled'}
MEDIA_KEYS=('media_all','media_photo','media_video')


def asset(name):
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/name


def prefs_path():
    base=Path(os.environ.get('APPDATA',str(Path.home()/'.config')))/'YandexDownloader32'
    return base/'settings.json'


def load_prefs():
    try:
        data=json.loads(prefs_path().read_text(encoding='utf-8'))
        if isinstance(data,dict):return data
    except (OSError,ValueError):pass
    return {}


class RaisedButton(tk.Canvas):
    """Tactile button with real rasterized soft shadows and a pressed-in state.

    The surface is solid, NOT transparent or glass-like. Mouse-down pushes the
    button face into its shadow; releasing restores the elevation.
    """
    def __init__(self,parent,label,command,variant='light',width=135,height=38,**kwargs):
        super().__init__(parent,width=width,height=height,bg=parent.cget('bg'),bd=0,
                         highlightthickness=0,relief='flat',cursor='hand2',takefocus=1,**kwargs)
        self.label=label;self.command=command;self.variant=variant
        self.enabled=True;self.hovered=False;self.pressed=False
        self._bw=width;self._bh=height;self._photo=None;self._frames={}
        self._img_id=self.create_image(0,0,anchor='nw')
        self._label_id=self.create_text(width/2,height/2-2,text=label,fill=INK,
                                        font=('Segoe UI',9,'bold'),anchor='center',width=width-24)
        self.bind('<Configure>',self._resize)
        self.bind('<Enter>',self._enter)
        self.bind('<Leave>',self._leave)
        self.bind('<ButtonPress-1>',self._press)
        self.bind('<ButtonRelease-1>',self._release)
        self.bind('<Return>',self._keyboard)
        self.bind('<space>',self._keyboard)
        self.bind('<FocusIn>',lambda e:self._paint())
        self.bind('<FocusOut>',lambda e:self._paint())
        self._paint()

    def _resize(self,event):
        if event.width!=self._bw or event.height!=self._bh:
            self._bw=event.width;self._bh=event.height
            self._frames.clear()
            self._paint()

    def _enter(self,event):
        self.hovered=True;self._paint()

    def _leave(self,event):
        self.hovered=False;self.pressed=False;self._paint()

    def _press(self,event):
        if not self.enabled:return
        self.focus_set()
        self.pressed=True
        self._paint()

    def _release(self,event):
        if not self.enabled or not self.pressed:return
        inside=0 <= event.x < self._bw and 0 <= event.y < self._bh
        self.pressed=False
        self._paint()
        if inside:self.command()

    def _keyboard(self,event):
        if not self.enabled:return 'break'
        self.focus_set()
        self.pressed=True;self._paint()
        def fire():
            if not self.winfo_exists():return
            self.pressed=False;self._paint()
            self.command()
        self.after(85,fire)
        return 'break'

    def set_enabled(self,flag):
        self.enabled=bool(flag)
        self.pressed=False
        self.configure(cursor='hand2' if flag else 'arrow')
        self._paint()

    def set_label(self,label):
        self.label=label
        self._paint()

    def _paint(self):
        w=max(24,self._bw);h=max(24,self._bh)
        key=(w,h,self.variant,self.enabled,self.hovered,self.pressed)
        if key not in self._frames:
            self._frames[key]=ImageTk.PhotoImage(self._surface(w,h))
        self._photo=self._frames[key]
        self.itemconfigure(self._img_id,image=self._photo)
        self.coords(self._label_id,w/2,h/2+(2 if self.pressed else (-3 if self.hovered and self.enabled else -2)))
        self.itemconfigure(self._label_id,text=self.label,width=w-22,
                           fill=('#A0A8B5' if not self.enabled else '#FFFFFF' if self.variant in ('blue','dark') else INK))
        self.tag_raise(self._label_id)

    def _surface(self,width,height):
        """Antialiased opaque image: shadow, bevel, and recessed pressed styling."""
        scale=2
        W,H=width*scale,height*scale
        canvas_bg=self.cget('bg')
        bg=Image.new('RGBA',(W,H),canvas_bg)
        if not self.enabled:
            face='#EAEDF2';border='#DBE0E7'
        elif self.variant=='dark':
            face='#292D36' if not self.hovered else '#404652';border='#191D26'
        elif self.variant=='blue':
            face='#226AE7' if not self.hovered else '#357EFA';border='#1753B9'
        else:
            face='#FFFFFF' if not self.hovered else '#F8FAFF';border='#C8D0DE'
        down=self.pressed and self.enabled
        lifted=self.hovered and self.enabled and not down
        y=6 if down else 1 if lifted else 3
        face_box=(5*scale,y*scale,(width-5)*scale,(height-(8 if lifted else 6 if not down else 3))*scale)
        radius=11*scale

        if self.enabled and not down:
            shade=Image.new('RGBA',(W,H),(0,0,0,0))
            ds=ImageDraw.Draw(shade)
            shadow_alpha=90 if lifted else 73
            ds.rounded_rectangle((face_box[0],face_box[1]+5*scale,face_box[2],face_box[3]+4*scale),
                                 radius=radius,fill=(35,49,72,shadow_alpha))
            shade=shade.filter(ImageFilter.GaussianBlur(3.2*scale))
            bg=Image.alpha_composite(bg,shade)
        d=ImageDraw.Draw(bg)
        if down:
            # Recessed well: the former shadow collapses and a dark top inner
            # line appears around the sunken face.
            well=(face_box[0]-1*scale,2*scale,face_box[2]+1*scale,face_box[3]+2*scale)
            d.rounded_rectangle(well,radius=radius,fill='#B5BFCE' if self.variant=='light' else '#1B263B')
            d.rounded_rectangle(face_box,radius=radius,fill=face,outline=border,width=scale)
            d.rounded_rectangle((face_box[0]+2*scale,face_box[1]+2*scale,
                                 face_box[2]-2*scale,face_box[3]-2*scale),
                                 radius=max(1,radius-2*scale),outline='#D8DDE8' if self.variant=='light' else '#385379',width=scale)
        else:
            d.rounded_rectangle(face_box,radius=radius,fill=face,outline=border,width=scale)
            # Soft top-edge highlight makes the buttons look convex.
            highlight='#FFFFFF' if self.variant=='light' else '#A6C8FF' if self.variant=='blue' else '#687281'
            d.arc((face_box[0]+3*scale,face_box[1]+1*scale,
                   face_box[2]-3*scale,face_box[3]-1*scale),185,350,
                   fill=highlight,width=scale)
            if lifted:
                d.rounded_rectangle((face_box[0]+scale,face_box[1]+scale,
                                     face_box[2]-scale,face_box[3]-scale),
                                     radius=radius-scale,outline='#EDF3FF' if self.variant=='light' else '#6EACFA',width=scale)
        return bg.convert('RGB').resize((width,height),Image.Resampling.LANCZOS)


class App:
    def __init__(self,root):
        self.root=root
        prefs=load_prefs()
        self.locale=prefs.get('locale','ru') if prefs.get('locale') in LANG_NAMES else 'ru'
        self.target=tk.StringVar(value=prefs.get('target',str(Path.home()/'Downloads')))
        self.media_key=prefs.get('media','media_all') if prefs.get('media') in MEDIA_KEYS else 'media_all'
        self.recursive=tk.BooleanVar(value=bool(prefs.get('recursive',True)))
        self.zip_files=tk.BooleanVar(value=bool(prefs.get('zip',False)))
        self.verify=tk.BooleanVar(value=bool(prefs.get('verify',False)))
        self.sound_enabled=tk.BooleanVar(value=bool(prefs.get('sound_enabled',True)))
        self.sound_path=tk.StringVar(value=str(prefs.get('sound_path','')))
        self.parallel=tk.IntVar(value=max(1,min(12,int(prefs.get('threads',4)))))
        self.status=tk.StringVar()
        self.speed=tk.StringVar(value=self.t('no_speed'))
        self.remaining=tk.StringVar(value='—')
        self.file_count=tk.StringVar(value='0 / 0')
        self.transfer=tk.StringVar(value='—')
        self.progress=tk.DoubleVar(value=0)
        self.events=queue.Queue();self.cancel=threading.Event();self.busy=False
        self.current_meter=None;self.cache=None;self.retry_list=[];self.planned=[]
        self.file_states={};self.log_items=deque(maxlen=260)
        self.speed_history=deque([0.0]*40,maxlen=40)
        self.status_record=('idle',{})
        self.link_value=prefs.get('last_links','')
        self._after_persist=None
        self._ui_images=[]
        screen_height=root.winfo_screenheight()
        initial_height=max(785,min(940,screen_height-90))
        root.geometry(f'1180x{initial_height}')
        root.minsize(1030,785)
        root.configure(bg=BG)
        self._style()
        self._render()
        try:
            root.iconbitmap(str(asset('app.ico')))
        except Exception:
            try:
                self.icon=tk.PhotoImage(file=str(asset('app.png')))
                root.iconphoto(True,self.icon)
            except tk.TclError:pass
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.after(280,self.pump)
        root.after(1200,self._periodic_save)

    def t(self,key,**kw):return tr(key,self.locale,**kw)

    def _style(self):
        st=ttk.Style(self.root)
        st.theme_use('clam')
        st.configure('XD.TCombobox',font=('Segoe UI',10),fieldbackground=WHITE,background=WHITE,
                     foreground=INK,arrowcolor=INK,padding=(9,8))
        st.map('XD.TCombobox',fieldbackground=[('readonly',WHITE)],background=[('readonly',WHITE)],
               foreground=[('readonly',INK)])
        st.configure('XD.Treeview',background=WHITE,fieldbackground=WHITE,foreground=INK,
                     rowheight=27,font=('Segoe UI',9),borderwidth=0)
        st.configure('XD.Treeview.Heading',background=PALE,foreground=MUTED,
                     font=('Segoe UI',9,'bold'),padding=(9,9),relief='flat')
        st.map('XD.Treeview',background=[('selected',GLOW)],foreground=[('selected',INK)])
        st.configure('XD.Horizontal.TProgressbar',troughcolor='#E7EBF2',background=BLUE,
                     bordercolor='#E7EBF2',lightcolor=BLUE,darkcolor=BLUE,thickness=12)

    def _label(self,parent,text='',size=10,bold=False,muted=False,bg=None,**kw):
        family='Microsoft YaHei UI' if self.locale=='zh' and sys.platform=='win32' else 'Segoe UI'
        return tk.Label(parent,text=text,font=(family,size,'bold' if bold else 'normal'),
                        fg=MUTED if muted else INK,bg=bg or parent.cget('bg'),**kw)

    def _section(self,parent,title,expand=False):
        rim=tk.Frame(parent,bg=LINE,padx=1,pady=1)
        inner=tk.Frame(rim,bg=WHITE,padx=17,pady=10)
        inner.pack(fill='both',expand=True)
        self._label(inner,title,10,True).pack(anchor='w',pady=(0,6))
        return rim,inner

    def _button(self,parent,key,callback,variant='light',width=140,height=37):
        return RaisedButton(parent,self.t(key),callback,variant,width,height)

    def _render(self):
        # Preserve content when switching language; these are also used by progress events.
        if hasattr(self,'urls'):
            self.link_value=self.urls.get('1.0','end-1c')
        for child in self.root.winfo_children():child.destroy()
        self._ui_images.clear()
        self.root.title(f'Yandex Downloader {APP_VERSION} · made by glebasya32')
        self._style()
        self.outer=tk.Frame(self.root,bg=BG,padx=22,pady=10)
        self.outer.pack(fill='both',expand=True)
        self.hero=tk.Canvas(self.outer,height=139,bg=BG,bd=0,highlightthickness=0)
        self.hero.pack(fill='x',pady=(0,9))
        self._paint_header()
        self.hero.bind('<Configure>',self._paint_header,add=True)
        self._hero_widgets()
        footer=tk.Frame(self.outer,bg=BG)
        footer.pack(side='bottom',fill='x',pady=(7,0))
        self._label(footer,self.t('footer_note'),9,muted=True,bg=BG).pack(side='left')
        self._label(footer,'made by glebasya32',9,True,muted=True,bg=BG).pack(side='right')
        self._label(footer,self.t('saved_hint')+' · ',8,muted=True,bg=BG).pack(side='right')
        main=tk.Frame(self.outer,bg=BG)
        main.pack(fill='both',expand=True)
        left=tk.Frame(main,bg=BG)
        left.pack(side='left',fill='both',expand=True,padx=(0,13))
        right=tk.Frame(main,bg=BG,width=292)
        right.pack(side='right',fill='y');right.pack_propagate(False)

        card,box=self._section(left,self.t('links_title'));card.pack(fill='x',pady=(0,10))
        self._label(box,self.t('links_tip'),9,muted=True).pack(anchor='w',pady=(0,6))
        text_outer=tk.Frame(box,bg=LINE,padx=1,pady=1)
        text_outer.pack(fill='x')
        self.urls=tk.Text(text_outer,height=2,relief='flat',bd=0,wrap='none',undo=True,
                          bg=WHITE,fg=INK,insertbackground=INK,selectbackground='#C8E0FF',
                          font=('Consolas',10),padx=10,pady=8)
        self.urls.pack(fill='x')
        self.urls.insert('1.0',self.link_value)
        self._bind_clipboard(self.urls)
        self.urls.bind('<KeyRelease>',self._link_count,add=True)
        row=tk.Frame(box,bg=WHITE)
        row.pack(fill='x',pady=(8,0))
        self._button(row,'paste',self.paste_url,width=103,height=32).pack(side='left',padx=(0,6))
        self._button(row,'clear',self.clear_urls,width=98,height=32).pack(side='left')
        self.linkcount=self._label(row,self.t('count_links',count=0),9,muted=True)
        self.linkcount.pack(side='right',pady=8)
        self._link_count()

        card,box=self._section(left,self.t('save_title'));card.pack(fill='x',pady=(0,10))
        row=tk.Frame(box,bg=WHITE);row.pack(fill='x')
        entry_border=tk.Frame(row,bg=LINE,padx=1,pady=1)
        entry_border.pack(side='left',fill='x',expand=True,padx=(0,8))
        self.dest=tk.Entry(entry_border,textvariable=self.target,bg=WHITE,fg=INK,
                           insertbackground=INK,relief='flat',font=('Segoe UI',10),bd=0)
        self.dest.pack(fill='x',ipady=10,padx=9)
        self._bind_clipboard(self.dest)
        self._button(row,'choose',self.choose_folder,width=106,height=37).pack(side='left')
        opt=tk.Frame(box,bg=WHITE);opt.pack(fill='x',pady=(11,0))
        self._label(opt,self.t('filetype_title'),9,True).pack(side='left',padx=(0,11))
        self.kind_combo=ttk.Combobox(opt,style='XD.TCombobox',width=20,state='readonly',
                                     values=[self.t(k) for k in MEDIA_KEYS])
        self.kind_combo.current(MEDIA_KEYS.index(self.media_key))
        self.kind_combo.bind('<<ComboboxSelected>>',self._media_selected)
        self.kind_combo.pack(side='left')
        checks=tk.Frame(box,bg=WHITE);checks.pack(fill='x',pady=(10,0))
        for key,var in [('recursive',self.recursive),('archive',self.zip_files),('verify',self.verify)]:
            tk.Checkbutton(checks,text=self.t(key),variable=var,bg=WHITE,fg=INK,
                           activebackground=WHITE,highlightthickness=0,selectcolor=WHITE,
                           font=('Segoe UI',9)).pack(side='left',padx=(0,13))

        card,box=self._section(left,self.t('threads_title'));card.pack(fill='x',pady=(0,10))
        trd=tk.Frame(box,bg=WHITE);trd.pack(fill='x')
        self.thread_label=self._label(trd,self.t('threads_hint',count=self.parallel.get()),9,muted=True)
        self.thread_label.pack(side='right')
        self.scale=tk.Scale(box,from_=1,to=12,orient='horizontal',showvalue=False,
                            variable=self.parallel,resolution=1,bd=0,highlightthickness=0,
                            bg=WHITE,fg=INK,troughcolor='#D6E0EE',activebackground=BLUE,
                            command=self._threads_changed)
        self.scale.pack(fill='x',pady=(0,4))
        modes=tk.Frame(box,bg=WHITE);modes.pack(fill='x')
        for key,value in [('mode_safe',1),('mode_balanced',4),('mode_fast',8),('mode_max',12)]:
            self._button(modes,key,lambda n=value:self.parallel.set(n) or self._threads_changed(None),
                         width=118,height=31).pack(side='left',padx=(0,7))

        actions=tk.Frame(left,bg=BG);actions.pack(fill='x',pady=(0,10))
        self.preview_btn=self._button(actions,'preview',self.preview,width=160)
        self.preview_btn.pack(side='left',padx=(0,7))
        self.start_btn=self._button(actions,'download',self.start,'blue',width=165)
        self.start_btn.pack(side='left',padx=(0,7))
        self.stop_btn=self._button(actions,'stop',self.stop,width=115)
        self.stop_btn.pack(side='left',padx=(0,7))
        self.retry_btn=RaisedButton(actions,self.t('retry',count=len(self.retry_list)),self.retry,width=153,height=37)
        self.retry_btn.pack(side='left')

        card,box=self._section(left,self.t('file_table'),expand=True)
        card.pack(fill='both',expand=True)
        self._button(box,'open_folder',self.open_folder,width=142,height=30).pack(anchor='e',pady=(0,7))
        table_frame=tk.Frame(box,bg=WHITE);table_frame.pack(fill='both',expand=True)
        self.tree=ttk.Treeview(table_frame,columns=('name','type','state'),show='headings',
                               style='XD.Treeview',height=8)
        for col,key in [('name','column_name'),('type','column_type'),('state','column_state')]:
            self.tree.heading(col,text=self.t(key))
        self.tree.column('name',width=370,stretch=True)
        self.tree.column('type',width=75,anchor='center',stretch=False)
        self.tree.column('state',width=115,anchor='center',stretch=False)
        self.tree.pack(side='left',fill='both',expand=True)
        scroll=ttk.Scrollbar(table_frame,orient='vertical',command=self.tree.yview)
        scroll.pack(side='right',fill='y');self.tree.configure(yscrollcommand=scroll.set)
        self._populate_tree()

        card,box=self._section(right,self.t('stats_title'));card.pack(fill='x',pady=(0,10))
        self._stat(box,'speed',self.speed,19)
        self._label(box,self.t('graph_title'),8,muted=True).pack(anchor='w',pady=(0,3))
        self.spark=tk.Canvas(box,height=39,highlightthickness=0,bd=0,bg=WHITE)
        self.spark.pack(fill='x',pady=(0,5))
        self._stat(box,'remaining',self.remaining,18)
        self._stat(box,'files',self.file_count,16)
        self._stat(box,'volume',self.transfer,10)
        card,box=self._section(right,self.t('progress'));card.pack(fill='x',pady=(0,10))
        ttk.Progressbar(box,variable=self.progress,maximum=100,style='XD.Horizontal.TProgressbar').pack(fill='x',pady=(0,9))
        self._label(box,textvariable=self.status,muted=True,size=9,wraplength=242,justify='left').pack(anchor='w')
        card,box=self._section(right,self.t('sound_title'));card.pack(fill='x',pady=(0,10))
        sound_row=tk.Frame(box,bg=WHITE);sound_row.pack(fill='x')
        tk.Checkbutton(sound_row,text=self.t('sound_toggle'),variable=self.sound_enabled,
                       command=self._save_prefs,bg=WHITE,fg=INK,activebackground=WHITE,
                       highlightthickness=0,selectcolor=WHITE,font=('Segoe UI',9)).pack(side='left')
        path_row=tk.Frame(box,bg=WHITE);path_row.pack(fill='x',pady=(5,0))
        self.sound_desc=self._label(path_row,self._sound_desc(),8,muted=True,wraplength=238,anchor='w')
        self.sound_desc.pack(anchor='w',fill='x')
        sound_buttons=tk.Frame(box,bg=WHITE);sound_buttons.pack(fill='x',pady=(6,0))
        self._button(sound_buttons,'sound_choose',self.choose_sound,width=124,height=31).pack(side='left',padx=(0,6))
        self._button(sound_buttons,'sound_preview',self.preview_sound,width=122,height=31).pack(side='left')

        card,box=self._section(right,self.t('events'),expand=True);card.pack(fill='both',expand=True)
        self.logs=tk.Text(box,relief='flat',bg=WHITE,fg=MUTED,font=('Consolas',9),
                          bd=0,padx=4,pady=4,wrap='word',state='disabled',height=7)
        self.logs.pack(fill='both',expand=True)
        self._button(box,'copy_log',self.copy_log,width=160,height=32).pack(anchor='w',pady=(6,0))
        self._repopulate_logs()

        self._set_status(*self.status_record)
        self._set_busy(self.busy)
        self.root.bind('<Control-Return>',lambda e:self.start())
        self.root.bind('<Control-l>',lambda e:self.urls.focus_set())
        self.root.bind('<Control-L>',lambda e:self.urls.focus_set())
        self.root.after(50,self.draw_spark)

    def _paint_header(self,event=None):
        cv=self.hero
        w=max(400,cv.winfo_width())
        h=139
        if hasattr(self,'_header_ids'):
            for item in self._header_ids:cv.delete(item)
        ids=[]
        # Solid white header with a gentle drop shadow. No translucency,
        # animated caustics, Mica, or refraction anywhere in the app.
        ids.append(cv.create_rectangle(14,9,w-14,h-3,fill='#E6E8EE',outline=''))
        ids.append(cv.create_rectangle(11,6,w-11,h-9,fill=WHITE,outline='#DDE3ED',width=1))
        ids.append(cv.create_line(28,h-12,w-28,h-12,fill='#F2F4F8',width=1))
        self._header_ids=ids
        for item in reversed(ids):cv.tag_lower(item)

    def _hero_widgets(self):
        cv=self.hero
        try:
            logo=tk.PhotoImage(file=str(asset('logo_header.png')))
            self._ui_images.append(logo)
            cv.create_image(45,72,image=logo,anchor='w')
        except tk.TclError:pass
        cv.create_text(126,49,text=self.t('app_title'),anchor='w',font=('Segoe UI',22,'bold'),fill=INK)
        cv.create_text(127,87,text=self.t('app_subtitle'),anchor='w',font=('Segoe UI',10),fill=MUTED)
        cv.create_text(127,112,text=self.t('app_badge'),anchor='w',font=('Segoe UI',8,'bold'),fill=BLUE)
        self.locale_name=tk.StringVar(value=LANG_NAMES[self.locale])
        self.lang_combo=ttk.Combobox(cv,textvariable=self.locale_name,state='readonly',width=14,
                                    style='XD.TCombobox',values=list(LANG_NAMES.values()))
        self.lang_combo.bind('<<ComboboxSelected>>',self._language_selected)
        self.lang_window=cv.create_window(820,52,window=self.lang_combo,anchor='e')
        self.donate_button=RaisedButton(cv,self.t('donate'),self.open_donations,'dark',width=215,height=38)
        self.donate_window=cv.create_window(1052,52,window=self.donate_button,anchor='e')
        cv.bind('<Configure>',self._place_header_buttons,add=True)

    def _place_header_buttons(self,event):
        w=event.width
        self.hero.coords(self.donate_window,w-27,52)
        self.hero.coords(self.lang_window,w-264,52)

    def _stat(self,parent,key,variable,size):
        self._label(parent,self.t(key),8,True,True).pack(anchor='w',pady=(0,3))
        self._label(parent,textvariable=variable,size=size,bold=True,wraplength=250,
                    justify='left').pack(anchor='w',pady=(0,5))

    def _language_selected(self,event):
        chosen=self.locale_name.get()
        target=next((code for code,name in LANG_NAMES.items() if chosen==name),self.locale)
        if target==self.locale:return
        self.locale=target
        # Message language updates immediately, including the donate button.
        self.link_value=self.urls.get('1.0','end-1c')
        self._save_prefs()
        self.root.after_idle(self._render)

    def _media_selected(self,event):
        self.media_key=MEDIA_KEYS[max(0,self.kind_combo.current())]
        self.cache=None

    def _threads_changed(self,event):
        self.thread_label.configure(text=self.t('threads_hint',count=self.parallel.get()))

    def _link_count(self,event=None):
        if hasattr(self,'linkcount'):
            count=len([line for line in self.urls.get('1.0','end-1c').splitlines() if line.strip()])
            self.linkcount.configure(text=self.t('count_links',count=count))

    def _bind_clipboard(self,widget):
        """Robust clipboard support across Latin/Cyrillic layouts and standard Tk events."""
        layout={'м':'v','с':'c','ч':'x','ф':'a','я':'z','н':'y'}
        codes={86:'v',67:'c',88:'x',65:'a',90:'z',89:'y'}
        codes_tk={'cyrillic_em':'v','cyrillic_es':'c','cyrillic_che':'x','cyrillic_ef':'a',
                  'cyrillic_ya':'z','cyrillic_en':'y'}
        def action(name):
            widget.focus_set()
            try:
                if name=='paste':
                    text=self.root.clipboard_get()
                    if isinstance(widget,tk.Text):
                        if widget.tag_ranges('sel'):widget.delete('sel.first','sel.last')
                        widget.insert('insert',text)
                        try: widget.edit_separator()
                        except tk.TclError: pass
                    else:
                        try:
                            if widget.selection_present():widget.delete('sel.first','sel.last')
                        except tk.TclError:
                            pass
                        widget.insert('insert',text)
                elif name in ('cut','copy'):
                    if isinstance(widget,tk.Text):text=widget.get('sel.first','sel.last')
                    else:text=widget.selection_get()
                    self.root.clipboard_clear();self.root.clipboard_append(text)
                    if name=='cut':widget.delete('sel.first','sel.last')
                elif name=='all':
                    if isinstance(widget,tk.Text):
                        widget.tag_add('sel','1.0','end-1c')
                        widget.mark_set('insert','1.0')
                        widget.see('insert')
                    else:
                        widget.selection_range(0,'end')
                        widget.icursor('end')
                elif name=='undo':
                    if isinstance(widget,tk.Text):widget.edit_undo()
                elif name=='redo':
                    if isinstance(widget,tk.Text):widget.edit_redo()
            except (tk.TclError,AttributeError):
                return 'break'
            if widget==self.urls:self._link_count()
            return 'break'
        def shortcut(e):
            if e.state & 0x4:
                key=(e.keysym or '').lower()
                if sys.platform=='win32':key=codes.get(e.keycode,key)
                key=codes_tk.get(key,layout.get(key,key))
                name={'v':'paste','c':'copy','x':'cut','a':'all','z':'undo','y':'redo'}.get(key)
                if name:return action(name)
            return None
        # Route physical Ctrl shortcuts through one KeyPress handler.
        # Binding Ctrl+V and <<Paste>> simultaneously makes Tk insert text
        # multiple times on some systems.
        widget.bind('<KeyPress>',shortcut,add=False)
        widget.bind('<Shift-Insert>',lambda e:action('paste'))
        widget.bind('<Control-Insert>',lambda e:action('copy'))
        menu=tk.Menu(widget,tearoff=False,bg=WHITE,fg=INK,activebackground=GLOW)
        for key,name in [('paste','paste'),('copy_log','copy'),('clear','cut'),('links_title','all')]:
            label={'paste':{'ru':'Вставить','en':'Paste','be':'Уставіць','zh':'粘贴'},
                   'copy':{'ru':'Копировать','en':'Copy','be':'Капіяваць','zh':'复制'},
                   'cut':{'ru':'Вырезать','en':'Cut','be':'Выразаць','zh':'剪切'},
                   'all':{'ru':'Выделить всё','en':'Select all','be':'Вылучыць усё','zh':'全选'}}[name][self.locale]
            menu.add_command(label=label,command=lambda n=name:action(n))
        def pop(e):
            widget.focus_set()
            try:menu.tk_popup(e.x_root,e.y_root)
            finally:menu.grab_release()
            return 'break'
        widget.bind('<Button-3>',pop)
        widget.bind('<Button-2>',pop)

    def paste_url(self):
        self.urls.focus_set()
        try:
            text=self.root.clipboard_get()
            if self.urls.tag_ranges('sel'):self.urls.delete('sel.first','sel.last')
            self.urls.insert('insert',text)
            self._link_count()
        except tk.TclError:messagebox.showinfo(self.t('clipboard_title'),self.t('clipboard_empty'))

    def clear_urls(self):
        self.urls.delete('1.0','end');self._link_count()

    def choose_folder(self):
        folder=filedialog.askdirectory(initialdir=self.target.get())
        if folder:self.target.set(folder)

    def links(self):
        rows=[line.strip() for line in self.urls.get('1.0','end-1c').splitlines() if line.strip()]
        if not rows:raise ValueError(self.t('no_urls'))
        links=[]
        for n,url in enumerate(rows,1):
            try:key=parse_folder_link(url)
            except ValueError as err:
                raise ValueError(self.t('bad_url_line',line=n,error=translate_exception(err,self.locale))) from err
            if key not in links:links.append(key)
        return links

    def _settings(self):
        links=self.links();path=self.target.get().strip()
        if not path:raise ValueError(self.t('no_destination'))
        return (links,Path(path).expanduser(),self.media_key,self.recursive.get(),
                self.zip_files.get(),self.verify.get(),int(self.parallel.get()))

    def _save_prefs(self):
        try:
            settings={'locale':self.locale,'target':self.target.get(),
                      'media':self.media_key,'recursive':self.recursive.get(),'zip':self.zip_files.get(),
                      'verify':self.verify.get(),'threads':int(self.parallel.get()),
                      'sound_enabled':self.sound_enabled.get(),'sound_path':self.sound_path.get(),
                      'last_links':self.urls.get('1.0','end-1c') if hasattr(self,'urls') else self.link_value}
            path=prefs_path();path.parent.mkdir(parents=True,exist_ok=True)
            tmp=path.with_suffix('.tmp')
            tmp.write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf-8')
            os.replace(tmp,path)
        except OSError:pass

    def _periodic_save(self):
        if self.root.winfo_exists():
            self._save_prefs();self.root.after(4000,self._periodic_save)

    def _set_status(self,key,params=None):
        self.status_record=(key,params or {})
        self.status.set(self.t(key,**(params or {})))

    def _log(self,key_or_text,params=None):
        self.log_items.append((time.strftime('%H:%M:%S'),key_or_text,params))
        if hasattr(self,'logs'):
            self.logs.configure(state='normal')
            self.logs.insert('end',self._log_text(self.log_items[-1])+'\n')
            self.logs.see('end');self.logs.configure(state='disabled')

    def _log_text(self,item):
        stamp,key,params=item
        return stamp+'  '+(self.t(key,**params) if params is not None else str(key))

    def _repopulate_logs(self):
        self.logs.configure(state='normal');self.logs.delete('1.0','end')
        for item in self.log_items:self.logs.insert('end',self._log_text(item)+'\n')
        self.logs.see('end');self.logs.configure(state='disabled')

    def _populate_tree(self):
        for row in self.tree.get_children():self.tree.delete(row)
        for i,item in enumerate(self.planned[:1100]):
            state=self.file_states.get(i,'waiting')
            self.tree.insert('','end',iid=f'f{i}',values=(item.label[:96],
                       self.t('video' if item.kind=='video' else 'photo'),self.t(state)))

    def _set_busy(self,flag):
        self.busy=flag
        for btn in (self.preview_btn,self.start_btn):btn.set_enabled(not flag)
        self.stop_btn.set_enabled(flag)
        self.retry_btn.set_enabled(not flag and bool(self.retry_list))
        self.retry_btn.set_label(self.t('retry',count=len(self.retry_list)))
        if hasattr(self,'scale'):self.scale.configure(state='disabled' if flag else 'normal')
        if hasattr(self,'kind_combo'):self.kind_combo.configure(state='disabled' if flag else 'readonly')

    def preview(self):self._launch('preview')
    def start(self):self._launch('download')
    def retry(self):
        if self.busy or not self.retry_list:return
        self._launch('retry',tasks=list(self.retry_list))

    def _launch(self,mode,tasks=None):
        if self.busy:return
        try:options=self._settings()
        except Exception as err:
            messagebox.showerror(self.t('dialog_input'),str(err));return
        links,folder,media,recurse,zip_files,verify,threads=options
        if mode!='preview':
            try:folder.mkdir(parents=True,exist_ok=True)
            except OSError as ex:messagebox.showerror(self.t('destination_error'),str(ex));return
        self.cancel.clear();self.current_meter=None
        self.progress.set(0);self.speed.set(self.t('no_speed'));self.remaining.set('—')
        self.file_count.set('0 / 0');self.transfer.set('—')
        self.file_states.clear();self.planned=[];self._populate_tree()
        self._set_status('retrying' if mode=='retry' else 'scanning')
        self._set_busy(True)
        self._save_prefs()
        threading.Thread(target=self._worker,args=(mode,options,tasks),daemon=True).start()

    def stop(self):
        self.cancel.set();self._set_status('stopping')

    def post(self,key,value):self.events.put((key,value))

    def _scan(self,links,folder,media,recurse):
        planned=[];occupied=set();archives=[];failed=0
        for n,link in enumerate(links,1):
            if self.cancel.is_set():break
            self.post('status',('scanning_one',{'current':n,'total':len(links)}))
            try:
                info=folder_details(link,self.cancel)
                name=clean_name(info.get('name') or 'Folder')
                label=(f'{n:02d}_' if len(links)>1 else '')+name
                dest=folder/label
                archives.append((label,dest,folder/(label+'.zip')))
                count=0
                for item in enumerate_folder(link,self.cancel,recursive=recurse):
                    if (media=='media_photo' and item['kind']!='photo') or (media=='media_video' and item['kind']!='video'):continue
                    out=dest.joinpath(*item['relative']);key=str(out).casefold();suffix=2
                    while key in occupied:
                        out=out.with_name(f'{out.stem} ({suffix}){out.suffix}')
                        key=str(out).casefold();suffix+=1
                    occupied.add(key)
                    planned.append(Task(link,item['remote'],item['relative'],out,item['size'],item['kind'],item['md5']))
                    count+=1
                self.post('log',('folder_found',{'name':name,'count':count}))
            except InterruptedError:break
            except Exception as err:
                failed+=1;self.post('log',('read_error',{'number':n,'error':translate_exception(err,self.locale)}))
        if failed and not archives and not self.cancel.is_set():raise RuntimeError('Не удалось открыть ни одной папки. Проверьте ссылки и доступ.')
        return planned,archives

    def _worker(self,mode,settings,tasks):
        links,folder,media,recurse,zip_files,verify,threads=settings
        failed=[]
        try:
            key=(tuple(links),str(folder),media,recurse)
            if mode=='retry':planned=tasks or [];archives=[]
            elif self.cache and self.cache[0]==key:
                planned,archives=self.cache[1:]
                self.post('log',('cached',{}))
            else:
                planned,archives=self._scan(links,folder,media,recurse)
                if self.cancel.is_set():return
                self.cache=(key,planned,archives)
            if self.cancel.is_set():return
            p=sum(t.kind=='photo' for t in planned)
            v=len(planned)-p;size=sum(t.size or 0 for t in planned)
            self.post('log',('found_summary',{'photos':p,'videos':v,'size':size_text(size,self.locale)}))
            self.post('plan',planned)
            if mode=='preview':
                self.post('status',('checked',{'photos':p,'videos':v,'size':size_text(size,self.locale)}));return
            if not planned:
                self.post('status',('none_found',{}));return
            meter=Meter(planned)
            self.post('meter',meter)
            _,failed=execute_tasks(planned,self.cancel,threads,self._engine_event,verify_md5=verify,
                                  zip_folders=archives if zip_files else None,meter=meter)
            result=meter.snapshot()
            self.post('status',('stopped_summary' if self.cancel.is_set() else 'finished',
                                {'done':result['done'],'skipped':result['skipped'],'failed':result['failed']}))
            if not self.cancel.is_set() and result['done']>0:
                self.post('completion_sound',None)
            if failed:
                report=folder/'YandexDownloader_errors.txt'
                report.write_text('\n'.join(f'{task.label}\t{task.remote}' for task in failed),encoding='utf-8')
                self.post('log',('error_report',{'path':str(report)}))
        except InterruptedError:self.post('status',('stopped',{}))
        except Exception as ex:
            self.post('status',('error_prefix',{'error':translate_exception(ex,self.locale)}))
            self.post('log',('error_prefix',{'error':translate_exception(ex,self.locale)}))
        finally:
            self.post('retry_count',(failed,mode))
            self.post('finished',None)

    def _engine_event(self,event,data):
        # Engine emits localizable event tuples; no Tk calls from background threads.
        if isinstance(data,tuple) and len(data)==2 and isinstance(data[1],dict):
            self.post(event,data)
        elif event=='status':self.post('status',('elapsed',{}))
        elif event=='log':self.post('log',str(data))
        else:self.post(event,data)

    def pump(self):
        try:
            for _ in range(220):
                try:kind,value=self.events.get_nowait()
                except queue.Empty:break
                if kind=='status':
                    if isinstance(value,tuple):self._set_status(value[0],value[1])
                    else:self._set_status('error_prefix',{'error':str(value)})
                elif kind=='log':
                    if isinstance(value,tuple):self._log(value[0],value[1])
                    else:self._log(str(value))
                elif kind=='plan':
                    self.planned=list(value);self._populate_tree()
                    self.file_count.set(f'0 / {len(value)}')
                    if len(value)>1100:self._log('log_truncated',{'count':1100,'total':len(value)})
                elif kind=='meter':self.current_meter=value
                elif kind=='file':
                    idx,state,label=value
                    self.file_states[idx]=STATE_CODES.get(state,state)
                    iid=f'f{idx}'
                    if self.tree.exists(iid):self.tree.set(iid,'state',self.t(self.file_states[idx]))
                elif kind=='retry_count':
                    failed,mode=value
                    if mode in ('download','retry'):self.retry_list=failed
                elif kind=='completion_sound':
                    if self.sound_enabled.get():self._play_sound()
                elif kind=='finished':self._set_busy(False)
        except tk.TclError:return
        if self.current_meter:
            snap=self.current_meter.snapshot()
            self.progress.set(snap['pct'])
            mbps=snap['speed']/1048576
            self.speed.set(self.t('speed_value',speed=mbps) if snap['speed']>0 else self.t('no_speed'))
            if self.busy:self.speed_history.append(mbps)
            self.remaining.set(eta_locale(snap['eta'],self.locale))
            self.file_count.set(f'{snap["completed"]} / {snap["total"]}')
            self.transfer.set(f'{size_text(snap["current_bytes"],self.locale)} / {size_text(snap["total_bytes"],self.locale)}')
            self.draw_spark()
        if self.root.winfo_exists():self.root.after(360,self.pump)

    def draw_spark(self):
        if not hasattr(self,'spark') or not self.spark.winfo_exists():return
        cv=self.spark;cv.delete('all')
        w=max(175,cv.winfo_width());h=45
        data=list(self.speed_history);peak=max(.08,max(data))
        coords=[]
        for i,value in enumerate(data):coords.extend((i*w/max(1,len(data)-1), h-4-(value/peak)*(h-14)))
        if len(coords)>3:
            cv.create_polygon(*([0,h]+coords+[w,h]),fill='#EBF3FF',outline='')
            cv.create_line(*coords,fill=BLUE,width=2,smooth=True)
            x,y=coords[-2:];cv.create_oval(x-3,y-3,x+3,y+3,fill=BLUE,outline=WHITE)

    def _sound_desc(self):
        selected=self.sound_path.get().strip()
        return Path(selected).name if selected else self.t('sound_default')

    def choose_sound(self):
        filename=filedialog.askopenfilename(
            parent=self.root,title=self.t('sound_choose'),
            filetypes=[(self.t('sound_wav_files'),'*.wav'),(self.t('sound_all_files'),'*.*')]
        )
        if not filename:return
        if Path(filename).suffix.lower()!='.wav':
            messagebox.showerror(self.t('dialog_error'),self.t('sound_wav_only'))
            return
        try:
            import wave
            with wave.open(filename,'rb') as audio:
                if audio.getnframes()<=0:raise ValueError('Empty audio')
        except Exception:
            messagebox.showerror(self.t('dialog_error'),self.t('sound_invalid'))
            return
        self.sound_path.set(filename)
        self.sound_desc.configure(text=self._sound_desc())
        self._save_prefs()

    def preview_sound(self):
        self._play_sound()

    def _play_sound(self):
        path=self.sound_path.get().strip()
        source=Path(path) if path else asset('completion.wav')
        if not source.is_file():
            # If a custom file has been moved, fall back to the bundled chime.
            source=asset('completion.wav')
        if sys.platform=='win32':
            try:
                import winsound
                winsound.PlaySound(str(source),winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                return
            except Exception:pass
        # Cross-platform source runs can still notify without an extra audio dependency.
        try:self.root.bell()
        except tk.TclError:pass

    def open_folder(self):
        dest=Path(self.target.get()).expanduser()
        if not dest.exists():messagebox.showinfo(self.t('destination_error'),self.t('folder_missing'));return
        try:
            if os.name=='nt':os.startfile(str(dest))
            elif sys.platform=='darwin':subprocess.Popen(['open',str(dest)])
            else:subprocess.Popen(['xdg-open',str(dest)])
        except Exception as ex:messagebox.showerror(self.t('dialog_error'),str(ex))

    def open_donations(self):
        try:
            success=webbrowser.open(DONATE_URL,new=2)
            if not success:raise RuntimeError('browser returned false')
        except Exception:
            self.root.clipboard_clear();self.root.clipboard_append(DONATE_URL)
            messagebox.showinfo(self.t('donate'),self.t('donate_dialog',url=DONATE_URL))

    def copy_log(self):
        text='\n'.join(self._log_text(item) for item in self.log_items)
        self.root.clipboard_clear();self.root.clipboard_append(text)
        self._set_status('copied')

    def close(self):
        if self.busy and not messagebox.askyesno(self.t('close_title'),self.t('close_busy')):return
        self._save_prefs();self.cancel.set()
        self.root.destroy()


def main():
    if sys.platform=='win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:pass
    root=tk.Tk()
    App(root)
    root.mainloop()

if __name__=='__main__':main()
