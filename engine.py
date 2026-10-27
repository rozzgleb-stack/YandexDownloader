# -*- coding: utf-8 -*-
"""Yandex public folder media downloader engine. Standard library only.

Downloads only from public folders verified by Yandex Disk public API.
"""
from __future__ import annotations

import concurrent.futures
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from typing import Callable
import zipfile

APP_VERSION = '6.4'
API = 'https://cloud-api.yandex.net/v1/disk/public/resources'
UA = {'User-Agent': 'Mozilla/5.0 (YandexDownloader32/6.0)'}
ALLOWED_HOSTS = {'disk.yandex.ru','disk.yandex.by','disk.yandex.com','disk.yandex.kz','yadi.sk'}
PHOTO_EXT = {'.jpg','.jpeg','.png','.webp','.gif','.bmp','.tif','.tiff','.heic','.heif','.avif','.dng','.raw','.cr2','.nef','.arw','.rw2','.orf','.raf','.srw','.pef','.jxl'}
VIDEO_EXT = {'.mp4','.mov','.m4v','.mkv','.avi','.webm','.wmv','.mpeg','.mpg','.3gp','.ts','.mts','.m2ts','.flv','.vob','.ogv'}


def parse_folder_link(value: str) -> str:
    """Strict syntax check; API get_resource() validates directory, not just URL."""
    value = value.strip()
    try:
        url = urllib.parse.urlsplit(value)
        if (url.scheme.lower() != 'https' or (url.hostname or '').lower() not in ALLOWED_HOSTS
                or url.username or url.password or url.port is not None):
            raise ValueError
        segments = [urllib.parse.unquote(v) for v in url.path.split('/') if v]
        if len(segments) != 2 or segments[0] not in ('d', 'public') or not segments[1]:
            raise ValueError
        return urllib.parse.urlunsplit(('https',(url.hostname or '').lower(),url.path,'',''))
    except (ValueError, TypeError) as exc:
        raise ValueError('Нужна публичная ссылка на папку Яндекс Диска вида https://disk.yandex.ru/d/…') from exc


def clean_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]','_', str(name)).strip(' .')[:170]
    if not name: name = 'Без_имени'
    if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)',name,re.I): name = '_' + name
    return name


def type_of(item: dict) -> str | None:
    ext=Path(item.get('name') or '').suffix.lower()
    if ext in PHOTO_EXT: return 'photo'
    if ext in VIDEO_EXT: return 'video'
    media=str(item.get('media_type') or '').lower()
    mime=str(item.get('mime_type') or '').lower()
    if media in ('image','photo') or mime.startswith('image/'): return 'photo'
    if media in ('video','movie') or mime.startswith('video/'): return 'video'
    return None


def human(n: int | float | None) -> str:
    if n is None:return '—'
    val=float(n)
    for unit in ('Б','КБ','МБ','ГБ','ТБ'):
        if val<1024 or unit=='ТБ':return f'{val:.0f} {unit}' if unit=='Б' else f'{val:.1f} {unit}'
        val/=1024


def eta_text(seconds: float | None) -> str:
    if seconds is None or seconds < 0: return '—'
    seconds = int(round(seconds))
    if seconds >= 3600:return f'{seconds//3600} ч {(seconds%3600)//60} мин'
    if seconds >= 60:return f'{seconds//60} мин {seconds%60} с'
    return f'{seconds} с'


def _backoff(delay: float, cancel: threading.Event):
    if cancel.wait(delay):raise InterruptedError('Остановлено')


def api_json(endpoint: str, key: str, cancel: threading.Event, *, path: str | None = None, **kwargs) -> dict:
    params = {'public_key':key,**kwargs}
    if path is not None:params['path']=path
    url=API+endpoint+'?'+urllib.parse.urlencode(params)
    err=None
    for attempt in range(4):
        if cancel.is_set():raise InterruptedError('Остановлено')
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=35) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            if e.code in (400,401,403,404):
                raise RuntimeError(f'Яндекс Диск: HTTP {e.code}. Проверьте права доступа и ссылку.') from e
            err=e
        except (OSError,ValueError) as e:err=e
        if attempt<3:_backoff(min(1.0*2**attempt,6.0),cancel)
    raise RuntimeError(f'Ошибка API Яндекс Диска: {err}')


def folder_details(key: str,cancel: threading.Event) -> dict:
    info=api_json('',key,cancel)
    if info.get('type')!='dir':
        raise ValueError('Эта ссылка ведёт на отдельный файл. Разрешены только папки.')
    return info


@dataclasses.dataclass(frozen=True)
class Task:
    key: str
    remote: str
    relative: tuple[str,...]
    destination: Path
    size: int | None
    kind: str
    md5: str | None = None

    @property
    def label(self) -> str: return '/'.join(self.relative)


def enumerate_folder(key: str,cancel: threading.Event,*,recursive=True):
    """Yield media metadata with server paging; preserve safe relative names."""
    stack=[(None,(),0)]
    visited=set()
    while stack:
        path,parent,depth=stack.pop()
        if depth>40:raise RuntimeError('Слишком глубокая вложенность папок')
        if path in visited:continue
        visited.add(path)
        offset=0
        while True:
            if cancel.is_set():raise InterruptedError('Остановлено')
            data=api_json('',key,cancel,path=path,limit=100,offset=offset,
                          fields='_embedded.items.name,_embedded.items.path,_embedded.items.type,_embedded.items.size,_embedded.items.mime_type,_embedded.items.media_type,_embedded.items.md5,_embedded.total')
            embedded=data.get('_embedded') or {}
            items=embedded.get('items') or []
            if not items:break
            for item in items:
                if cancel.is_set():raise InterruptedError('Остановлено')
                name=clean_name(item.get('name') or 'file')
                if item.get('type')=='dir':
                    if recursive and item.get('path'):
                        stack.append((item['path'],parent+(name,),depth+1))
                elif item.get('type')=='file' and item.get('path'):
                    kind=type_of(item)
                    if kind:
                        size=item.get('size')
                        yield {'remote':item['path'],'relative':parent+(name,),
                               'size':max(0,int(size)) if size is not None else None,
                               'kind':kind,'md5':item.get('md5')}
            offset+=len(items)
            total=embedded.get('total')
            if (total is not None and offset>=total) or (total is None and len(items)<100):break


class Meter:
    """Thread-safe byte accounting. Speed measures bytes received THIS session."""
    def __init__(self,tasks: list[Task]):
        self.lock=threading.RLock()
        self.total=len(tasks)
        self.total_bytes=sum(t.size or 0 for t in tasks)
        self.unknown=sum(t.size is None for t in tasks)
        self.sizes=[t.size for t in tasks]
        self.current={}
        self.done=set()
        self.success=0;self.skipped=0;self.failed=0;self.cancelled=0
        self.transferred=0
        self.t0=time.monotonic()
        self.samples=deque([(self.t0,0)])

    def received(self,index:int,delta:int):
        with self.lock:
            self.transferred+=delta

    def position(self,index:int,count:int):
        with self.lock:
            self.current[index]=count

    def finish(self,index:int,result:str):
        with self.lock:
            self.current.pop(index,None)
            self.done.add(index)
            if result=='downloaded':self.success+=1
            elif result=='skipped':self.skipped+=1
            elif result=='cancelled':self.cancelled+=1
            else:self.failed+=1

    def snapshot(self) -> dict:
        with self.lock:
            now=time.monotonic()
            self.samples.append((now,self.transferred))
            while len(self.samples)>2 and self.samples[1][0]<now-6.0:self.samples.popleft()
            tstart,bstart=self.samples[0]
            interval=max(0.001,now-tstart)
            speed=(self.transferred-bstart)/interval if interval>0.15 else 0.0
            # Completion progress includes skipped; failed tasks are considered processed for count.
            total_known = self.total_bytes
            current_known=sum((size or 0) for i,size in enumerate(self.sizes) if i in self.done)
            current_known+=sum(min(self.sizes[i] or 0,v) for i,v in self.current.items())
            file_ratio=(len(self.done)+sum(min(1,v/max(self.sizes[i] or 1,1)) for i,v in self.current.items()))/max(self.total,1)
            fraction=(current_known/total_known) if total_known and not self.unknown else file_ratio
            # Pending unknown file sizes prohibit reliable ETA.
            eta=(max(0,total_known-current_known)/speed) if speed>1000 and not self.unknown else None
            return dict(total=self.total,completed=len(self.done),done=self.success,skipped=self.skipped,failed=self.failed,cancelled=self.cancelled,
                        total_bytes=total_known,current_bytes=current_known,transferred=self.transferred,
                        speed=speed,eta=eta,pct=max(0,min(100,100*fraction)),unknown=self.unknown)


def _md5_file(path: Path,cancel:threading.Event) -> str:
    dig=hashlib.md5()
    with path.open('rb') as f:
        while True:
            if cancel.is_set():raise InterruptedError('Остановлено')
            chunk=f.read(1024*1024)
            if not chunk:break
            dig.update(chunk)
    return dig.hexdigest()


def download_one(task:Task,index:int,cancel:threading.Event,meter:Meter,*,verify_md5=False) -> str:
    """Atomic rename after download; resume only on confirmed HTTP 206 content range."""
    if cancel.is_set():return 'cancelled'
    dest=task.destination
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file() and task.size is not None and dest.stat().st_size == task.size:
        if not (verify_md5 and task.md5) or _md5_file(dest,cancel).lower()==task.md5.lower():
            return 'skipped'
    partial=dest.with_name(dest.name+'.part')
    last=None
    for attempt in range(4):
        if cancel.is_set():return 'cancelled'
        try:
            # An interrupted download can be complete but not renamed yet.
            if partial.exists() and task.size is not None and partial.stat().st_size==task.size:
                if not (verify_md5 and task.md5) or _md5_file(partial,cancel).lower()==task.md5.lower():
                    os.replace(partial,dest)
                    return 'downloaded'
            dl=api_json('/download',task.key,cancel,path=task.remote)
            href=dl['href']
            existing=partial.stat().st_size if partial.exists() else 0
            if task.size is not None and existing>task.size:
                partial.unlink();existing=0
            hdr=dict(UA)
            if existing:hdr['Range']=f'bytes={existing}-'
            req=urllib.request.Request(href,headers=hdr)
            with urllib.request.urlopen(req,timeout=100) as res:
                status=getattr(res,'status',200)
                if status==206 and existing:
                    content_range=res.headers.get('Content-Range','')
                    if not content_range.startswith(f'bytes {existing}-'):
                        raise OSError('Неверный диапазон возобновления')
                    mode='ab';current=existing
                else:mode='wb';current=0
                meter.position(index,current)
                with partial.open(mode) as out:
                    while not cancel.is_set():
                        block=res.read(256*1024)
                        if not block:break
                        out.write(block)
                        current+=len(block)
                        meter.received(index,len(block))
                        meter.position(index,current)
            if cancel.is_set():return 'cancelled'
            if task.size is not None and partial.stat().st_size!=task.size:
                raise OSError(f'Несовпадение размера: {human(partial.stat().st_size)} вместо {human(task.size)}')
            if verify_md5 and task.md5:
                if _md5_file(partial,cancel).lower()!=task.md5.lower():
                    # Restart corrupted partial completely.
                    partial.unlink(missing_ok=True)
                    raise OSError('Контрольная сумма файла не совпала')
            os.replace(partial,dest)
            return 'downloaded'
        except InterruptedError:return 'cancelled'
        except (OSError,KeyError,RuntimeError,ValueError) as ex:
            last=ex
            if attempt<3:_backoff(min(1.0*(attempt+1),4.0),cancel)
    raise RuntimeError(str(last))


def zip_output(folder:Path,archive:Path,cancel:threading.Event,log:Callable[[str],None]):
    if not folder.exists():return
    tmp=archive.with_name(archive.name+'.tmp')
    try:
        with zipfile.ZipFile(tmp,'w',allowZip64=True) as archive_file:
            for src in sorted(folder.rglob('*')):
                if cancel.is_set():raise InterruptedError('Остановлено')
                if src.is_file() and not src.name.endswith('.part'):
                    archive_file.write(src,src.relative_to(folder),compress_type=zipfile.ZIP_STORED)
        os.replace(tmp,archive)
        log(('events_zip',{'path':str(archive)}))
    finally:tmp.unlink(missing_ok=True)


def execute_tasks(tasks:list[Task],cancel:threading.Event,concurrency:int,
                  on_event:Callable[[str,object],None],*,verify_md5=False,zip_folders=None,meter:Meter | None = None) -> tuple[Meter,list[Task]]:
    """Schedule all media from all folders in one bounded pool. Return failed items for retry."""
    meter=meter or Meter(tasks)
    failures=[]
    if not tasks:return meter,failures
    def job(i,t):
        if cancel.is_set():return 'cancelled',None
        on_event('file',(i,'Загрузка',t.label))
        try:
            result=download_one(t,i,cancel,meter,verify_md5=verify_md5)
            return result,None
        except Exception as exc:
            return 'failed',str(exc)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(16,concurrency)),thread_name_prefix='YandexDL') as pool:
        future_map={pool.submit(job,i,t):(i,t) for i,t in enumerate(tasks)}
        for future in concurrent.futures.as_completed(future_map):
            idx,task=future_map[future]
            try:result,error=future.result()
            except concurrent.futures.CancelledError:result,error='cancelled',None
            except Exception as e:result,error='failed',str(e)
            meter.finish(idx,result)
            if result=='failed':
                failures.append(task)
                on_event('log',('events_failed',{'file':task.label,'error':error}))
            elif result=='downloaded':on_event('log',('events_downloaded',{'file':task.label}))
            elif result=='skipped':on_event('log',('events_skipped',{'file':task.label}))
            on_event('file',(idx,result,task.label))
            if cancel.is_set():
                for f in future_map:f.cancel()
    if zip_folders and not cancel.is_set():
        for name,output,archive in zip_folders:
            if cancel.is_set():break
            on_event('status',('zip_pack',{'name':name}))
            try:zip_output(output,archive,cancel,lambda txt:on_event('log',txt))
            except Exception as exc:on_event('log',('events_zip_failed',{'name':name,'error':str(exc)}))
    return meter,failures
