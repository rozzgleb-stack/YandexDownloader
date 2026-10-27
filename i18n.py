# -*- coding: utf-8 -*-
"""UI translations. Every user-facing UI key must have all four languages."""
from __future__ import annotations
from typing import Any

LANG_NAMES = {'ru': 'Русский', 'en': 'English', 'be': 'Беларуская', 'zh': '简体中文'}
RAW: dict[str,tuple[str,str,str,str]] = {
    'app_title': ('YANDEX DOWNLOADER', 'YANDEX DOWNLOADER', 'YANDEX DOWNLOADER', 'YANDEX DOWNLOADER'),
    'app_subtitle': ('Фото и видео из публичных папок Яндекс Диска — быстро, аккуратно и удобно', 'Photos & videos from public Yandex Disk folders — fast, clean and convenient', 'Фота і відэа з публічных папак Яндэкс Дыска — хутка, акуратна і зручна', '从 Yandex Disk 公开文件夹快速、整洁、便捷地下载照片和视频'),
    'app_badge': ('ВЕРСИЯ 6.4', 'VERSION 6.4', 'ВЕРСІЯ 6.4', '版本 6.4'),
    'sound_title': ('ЗВУК ЗАВЕРШЕНИЯ', 'COMPLETION SOUND', 'ГУК ЗАВЯРШЭННЯ', '完成提示音'),
    'sound_toggle': ('Включить звук', 'Enable sound', 'Уключыць гук', '启用提示音'),
    'sound_default': ('Стандартный сигнал', 'Default chime', 'Стандартны сігнал', '默认提示音'),
    'sound_choose': ('Выбрать WAV', 'Choose WAV', 'Выбраць WAV', '选择 WAV'),
    'sound_preview': ('▶ Прослушать', '▶ Preview', '▶ Праслухаць', '▶ 试听'),
    'sound_wav_files': ('Звуковые файлы WAV', 'WAV audio files', 'Гукавыя файлы WAV', 'WAV 音频文件'),
    'sound_all_files': ('Все файлы', 'All files', 'Усе файлы', '所有文件'),
    'sound_wav_only': ('Пожалуйста, выберите WAV-файл.', 'Please select a WAV file.', 'Калі ласка, выберыце WAV-файл.', '请选择 WAV 文件。'),
    'sound_invalid': ('Не удалось прочитать WAV-файл.', 'The WAV file could not be read.', 'Не ўдалося прачытаць WAV-файл.', '无法读取 WAV 文件。'),
    'language': ('Язык', 'Language', 'Мова', '语言'),
    'donate': ('♡ Поддержать автора', '♡ Support the creator', '♡ Падтрымаць аўтара', '♡ 支持作者'),
    'links_title': ('01 / ССЫЛКИ НА ПАПКИ', '01 / FOLDER LINKS', '01 / СПАСЫЛКІ НА ПАПКІ', '01 / 文件夹链接'),
    'links_tip': ('Вставьте публичные ссылки на папки, каждую с новой строки', 'Paste public folder links, one per line', 'Устаўце публічныя спасылкі на папкі, кожную з новага радка', '粘贴公开文件夹链接，每行一个'),
    'links_placeholder': ('https://disk.yandex.ru/d/…', 'https://disk.yandex.ru/d/…', 'https://disk.yandex.ru/d/…', 'https://disk.yandex.ru/d/…'),
    'paste': ('Вставить', 'Paste', 'Уставіць', '粘贴'),
    'clear': ('Очистить', 'Clear', 'Ачысціць', '清空'),
    'count_links': ('Ссылок: {count}', 'Links: {count}', 'Спасылак: {count}', '链接数：{count}'),
    'save_title': ('02 / СОХРАНЕНИЕ', '02 / DESTINATION', '02 / ЗАХАВАННЕ', '02 / 保存位置'),
    'choose': ('Выбрать…', 'Browse…', 'Выбраць…', '浏览…'),
    'filetype_title': ('Что скачивать', 'Download', 'Што спампоўваць', '下载内容'),
    'media_all': ('Фото + видео', 'Photos + videos', 'Фота + відэа', '照片 + 视频'),
    'media_photo': ('Только фото', 'Photos only', 'Толькі фота', '仅照片'),
    'media_video': ('Только видео', 'Videos only', 'Толькі відэа', '仅视频'),
    'recursive': ('Вложенные папки', 'Subfolders', 'Укладзеныя папкі', '包含子文件夹'),
    'archive': ('Создать ZIP', 'Create ZIP', 'Стварыць ZIP', '创建 ZIP'),
    'verify': ('Проверять MD5', 'Verify MD5', 'Правяраць MD5', '校验 MD5'),
    'verify_hint': ('Если контрольная сумма доступна', 'When checksums are available', 'Калі даступна кантрольная сума', '仅在校验值可用时'),
    'threads_title': ('03 / ПАРАЛЛЕЛЬНАЯ ЗАГРУЗКА', '03 / PARALLEL DOWNLOADS', '03 / ПАРАЛЕЛЬНЫЯ СПАМПОЎКІ', '03 / 并行下载'),
    'threads_hint': ('Одновременно: {count}', 'Concurrent: {count}', 'Адначасова: {count}', '同时下载：{count}'),
    'mode_safe': ('Бережно', 'Gentle', 'Ашчадна', '轻量'),
    'mode_balanced': ('Баланс', 'Balanced', 'Баланс', '均衡'),
    'mode_fast': ('Быстро', 'Fast', 'Хутка', '快速'),
    'mode_max': ('Максимум', 'Maximum', 'Максімум', '最大'),
    'preview': ('Проверить папки', 'Check folders', 'Праверыць папкі', '检查文件夹'),
    'download': ('↓ Скачать файлы', '↓ Download files', '↓ Спампаваць файлы', '↓ 下载文件'),
    'stop': ('Остановить', 'Stop', 'Спыніць', '停止'),
    'retry': ('Повтор ошибок ({count})', 'Retry failures ({count})', 'Паўтарыць памылкі ({count})', '重试失败项（{count}）'),
    'open_folder': ('Открыть папку', 'Open folder', 'Адкрыць папку', '打开文件夹'),
    'file_table': ('ФАЙЛЫ И СТАТУСЫ', 'FILES & STATUS', 'ФАЙЛЫ І СТАТУСЫ', '文件和状态'),
    'column_name': ('Имя файла', 'File name', 'Імя файла', '文件名'),
    'column_type': ('Тип', 'Type', 'Тып', '类型'),
    'column_state': ('Статус', 'Status', 'Статус', '状态'),
    'photo': ('Фото', 'Photo', 'Фота', '照片'),
    'video': ('Видео', 'Video', 'Відэа', '视频'),
    'waiting': ('В очереди', 'Queued', 'У чарзе', '排队中'),
    'working': ('Загрузка…', 'Downloading…', 'Спампоўка…', '下载中…'),
    'downloaded': ('Готово', 'Done', 'Гатова', '完成'),
    'skipped': ('Уже есть', 'Already exists', 'Ужо ёсць', '已存在'),
    'failed': ('Ошибка', 'Failed', 'Памылка', '失败'),
    'cancelled': ('Отменено', 'Cancelled', 'Скасавана', '已取消'),
    'stats_title': ('В ПРЯМОМ ЭФИРЕ', 'LIVE METRICS', 'ЖЫВАЯ СТАТЫСТЫКА', '实时统计'),
    'speed': ('СКОРОСТЬ', 'SPEED', 'ХУТКАСЦЬ', '速度'),
    'remaining': ('ОСТАЛОСЬ ПРИМЕРНО', 'TIME REMAINING (EST.)', 'ЗАСТАЛОСЯ ПРЫБЛІЗНА', '预计剩余时间'),
    'files': ('ФАЙЛЫ', 'FILES', 'ФАЙЛЫ', '文件'),
    'volume': ('ПЕРЕДАНО ДАННЫХ', 'DATA TRANSFERRED', 'ПЕРАДАДЗЕНА ДАНЫХ', '已传输数据'),
    'progress': ('ОБЩИЙ ПРОГРЕСС', 'OVERALL PROGRESS', 'АГУЛЬНЫ ПРАГРЭС', '总体进度'),
    'events': ('ЖУРНАЛ СОБЫТИЙ', 'EVENT LOG', 'ЖУРНАЛ ПАДЗЕЙ', '事件日志'),
    'copy_log': ('Скопировать журнал', 'Copy log', 'Скапіраваць журнал', '复制日志'),
    'shortcuts': ('Ctrl+V · Ctrl+A · Ctrl+Enter', 'Ctrl+V · Ctrl+A · Ctrl+Enter', 'Ctrl+V · Ctrl+A · Ctrl+Enter', 'Ctrl+V · Ctrl+A · Ctrl+Enter'),
    'footer_note': ('Только публичные папки · Без обхода ограничений', 'Public folders only · No bypassing restrictions', 'Толькі публічныя папкі · Без абыходу абмежаванняў', '仅限公开文件夹 · 不绕过访问限制'),
    'idle': ('Вставьте ссылку на публичную папку Яндекс Диска.', 'Paste a public Yandex Disk folder link to begin.', 'Устаўце спасылку на публічную папку Яндэкс Дыска.', '请粘贴 Yandex Disk 公开文件夹链接。'),
    'scanning': ('Проверяю ссылки и нахожу файлы…', 'Checking links and locating files…', 'Правяраю спасылкі і шукаю файлы…', '正在检查链接并查找文件…'),
    'scanning_one': ('Сканирование папки {current}/{total}…', 'Scanning folder {current}/{total}…', 'Сканаванне папкі {current}/{total}…', '正在扫描文件夹 {current}/{total}…'),
    'retrying': ('Повторяю неудачные загрузки…', 'Retrying failed downloads…', 'Паўтараю няўдалыя спампоўкі…', '正在重试失败的下载…'),
    'stopping': ('Останавливаю загрузку…', 'Stopping downloads…', 'Спыняю спампоўку…', '正在停止下载…'),
    'checked': ('Найдено: {photos} фото, {videos} видео · {size}. Можно скачивать.', 'Found: {photos} photos, {videos} videos · {size}. Ready to download.', 'Знойдзена: {photos} фота, {videos} відэа · {size}. Можна спампоўваць.', '发现：{photos} 张照片、{videos} 个视频 · {size}。可以开始下载。'),
    'none_found': ('Подходящих файлов не найдено.', 'No matching files found.', 'Прыдатных файлаў не знойдзена.', '未找到符合条件的文件。'),
    'finished': ('Готово: скачано {done}, пропущено {skipped}, ошибок {failed}', 'Finished: {done} downloaded, {skipped} skipped, {failed} failed', 'Гатова: спампавана {done}, прапушчана {skipped}, памылак {failed}', '完成：下载 {done}，跳过 {skipped}，失败 {failed}'),
    'stopped_summary': ('Остановлено: скачано {done}, пропущено {skipped}, ошибок {failed}', 'Stopped: {done} downloaded, {skipped} skipped, {failed} failed', 'Спынена: спампавана {done}, прапушчана {skipped}, памылак {failed}', '已停止：下载 {done}，跳过 {skipped}，失败 {failed}'),
    'stopped': ('Остановлено пользователем.', 'Stopped by user.', 'Спынена карыстальнікам.', '用户已停止。'),
    'error_prefix': ('Ошибка: {error}', 'Error: {error}', 'Памылка: {error}', '错误：{error}'),
    'api_error': ('Ошибка Яндекс Диска: {error}', 'Yandex Disk error: {error}', 'Памылка Яндэкс Дыска: {error}', 'Yandex Disk 错误：{error}'),
    'read_error': ('Не удалось прочитать ссылку {number}: {error}', 'Could not read link {number}: {error}', 'Не ўдалося прачытаць спасылку {number}: {error}', '无法读取链接 {number}：{error}'),
    'folder_found': ('{name}: {count} файлов', '{name}: {count} files', '{name}: {count} файлаў', '{name}：{count} 个文件'),
    'found_summary': ('Найдено: {photos} фото · {videos} видео · {size}', 'Found: {photos} photos · {videos} videos · {size}', 'Знойдзена: {photos} фота · {videos} відэа · {size}', '发现：{photos} 张照片 · {videos} 个视频 · {size}'),
    'cached': ('Использую ранее проверенный список.', 'Using previously checked file list.', 'Выкарыстоўваю раней правераны спіс.', '使用之前检查过的文件列表。'),
    'error_report': ('Отчёт об ошибках: {path}', 'Error report: {path}', 'Справаздача пра памылкі: {path}', '错误报告：{path}'),
    'copied': ('Журнал скопирован.', 'Log copied.', 'Журнал скапіраваны.', '日志已复制。'),
    'zip_pack': ('Создаю ZIP: {name}…', 'Creating ZIP: {name}…', 'Ствараю ZIP: {name}…', '正在创建 ZIP：{name}…'),
    'destination_error': ('Папка недоступна', 'Destination unavailable', 'Папка недаступная', '目标文件夹不可用'),
    'folder_missing': ('Папка ещё не создана.', 'Folder does not exist yet.', 'Папка яшчэ не створана.', '文件夹尚不存在。'),
    'dialog_error': ('Ошибка', 'Error', 'Памылка', '错误'),
    'dialog_input': ('Проверьте данные', 'Check input', 'Праверце даныя', '检查输入'),
    'clipboard_empty': ('В буфере обмена нет текста.', 'No text in clipboard.', 'У буферы абмену няма тэксту.', '剪贴板中没有文本。'),
    'clipboard_title': ('Буфер обмена', 'Clipboard', 'Буфер абмену', '剪贴板'),
    'no_urls': ('Вставьте хотя бы одну ссылку на папку.', 'Paste at least one folder link.', 'Устаўце хаця б адну спасылку на папку.', '请至少粘贴一个文件夹链接。'),
    'bad_url_line': ('Строка {line}: {error}', 'Line {line}: {error}', 'Радок {line}: {error}', '第 {line} 行：{error}'),
    'bad_url': ('Нужна публичная ссылка на папку Яндекс Диска вида https://disk.yandex.ru/d/…', 'Enter a public Yandex Disk folder link such as https://disk.yandex.ru/d/…', 'Патрэбная публічная спасылка на папку Яндэкс Дыска, як https://disk.yandex.ru/d/…', '请输入公开 Yandex Disk 文件夹链接，例如 https://disk.yandex.ru/d/…'),
    'bad_folder': ('Ссылка ведёт на файл, а не на папку.', 'This link is a file, not a folder.', 'Спасылка вядзе на файл, а не на папку.', '该链接指向文件，而非文件夹。'),
    'bad_permissions': ('Нет доступа к папке или неверная ссылка.', 'Folder is inaccessible or link is invalid.', 'Няма доступу да папкі або спасылка няправільная.', '文件夹不可访问或链接无效。'),
    'no_valid_folders': ('Не удалось открыть ни одной папки. Проверьте ссылки.', 'No folders could be opened. Check the links.', 'Не ўдалося адкрыць ніводнай папкі. Праверце спасылкі.', '无法打开任何文件夹，请检查链接。'),
    'no_destination': ('Выберите папку сохранения.', 'Choose a destination folder.', 'Выберыце папку захавання.', '请选择保存文件夹。'),
    'log_truncated': ('Показаны первые {count} файлов из {total}', 'Showing first {count} of {total} files', 'Паказаны першыя {count} файлаў з {total}', '显示前 {count} / {total} 个文件'),
    'close_title': ('Закрыть приложение', 'Close application', 'Закрыць праграму', '关闭应用'),
    'close_busy': ('Загрузка ещё идёт. Остановить и закрыть?', 'Downloads are in progress. Stop and exit?', 'Спампоўка яшчэ ідзе. Спыніць і выйсці?', '下载仍在进行。停止并退出吗？'),
    'open_link_error': ('Не удалось открыть ссылку: {error}', 'Could not open link: {error}', 'Не ўдалося адкрыць спасылку: {error}', '无法打开链接：{error}'),
    'donate_dialog': ('Не удалось автоматически открыть браузер. Ссылка скопирована: {url}', 'Could not open browser. Link copied: {url}', 'Не ўдалося адкрыць браўзер. Спасылка скапіравана: {url}', '无法打开浏览器。链接已复制：{url}'),
    'no_folders': ('Ничего не удалось открыть.', 'Could not open any folders.', 'Не ўдалося адкрыць ніводнай папкі.', '无法打开任何文件夹。'),
    'events_downloaded': ('✓ {file}', '✓ {file}', '✓ {file}', '✓ {file}'),
    'events_skipped': ('Уже есть: {file}', 'Already exists: {file}', 'Ужо ёсць: {file}', '已存在：{file}'),
    'events_failed': ('Ошибка файла {file}: {error}', 'Failed {file}: {error}', 'Памылка файла {file}: {error}', '文件失败 {file}：{error}'),
    'events_zip': ('ZIP: {path}', 'ZIP: {path}', 'ZIP: {path}', 'ZIP：{path}'),
    'events_zip_failed': ('Не удалось создать ZIP {name}: {error}', 'Could not create ZIP {name}: {error}', 'Не ўдалося стварыць ZIP {name}: {error}', '无法创建 ZIP {name}：{error}'),
    'events_start': ('Загружаю {file}', 'Downloading {file}', 'Спампоўваю {file}', '正在下载 {file}'),
    'saved_hint': ('Настройки сохраняются автоматически', 'Settings are saved automatically', 'Налады захоўваюцца аўтаматычна', '设置自动保存'),
    'graph_title': ('Динамика скорости', 'Speed trend', 'Змена хуткасці', '速度趋势'),
    'no_speed': ('— МБ/с', '— MB/s', '— МБ/с', '— MB/s'),
    'speed_value': ('{speed:.2f} МБ/с', '{speed:.2f} MB/s', '{speed:.2f} МБ/с', '{speed:.2f} MB/s'),
    'size_bytes': ('{size}', '{size}', '{size}', '{size}'),
    'elapsed': ('Загрузка файлов…', 'Downloading files…', 'Спампоўка файлаў…', '正在下载文件…'),
    'help_tip': ('Ctrl+L — ссылки · Ctrl+Enter — начать', 'Ctrl+L — links · Ctrl+Enter — start', 'Ctrl+L — спасылкі · Ctrl+Enter — пачаць', 'Ctrl+L — 链接 · Ctrl+Enter — 开始'),
    'api_cancelled': ('Операция остановлена.', 'Operation cancelled.', 'Аперацыя спынена.', '操作已取消。'),
}
LANG_CODES = ('ru','en','be','zh')
TRANSLATIONS = {locale:{key:values[index] for key,values in RAW.items()} for index,locale in enumerate(LANG_CODES)}

def tr(key: str, lang: str = 'ru', **kwargs: Any) -> str:
    template = TRANSLATIONS.get(lang,TRANSLATIONS['ru']).get(key, TRANSLATIONS['ru'].get(key,key))
    try: return template.format(**kwargs)
    except (KeyError,ValueError): return template


def translate_exception(exc: BaseException, lang: str) -> str:
    """Translate known engine errors while retaining diagnostics for unknown exceptions."""
    message=str(exc)
    if 'публичная ссылка на папку' in message: return tr('bad_url',lang)
    if 'отдельный файл' in message: return tr('bad_folder',lang)
    if 'HTTP 400' in message or 'HTTP 401' in message or 'HTTP 403' in message or 'HTTP 404' in message:
        return tr('bad_permissions',lang)
    if 'ни одной папки' in message: return tr('no_valid_folders',lang)
    if 'Остановлено' in message: return tr('api_cancelled',lang)
    if 'Ошибка API Яндекс Диска:' in message: return tr('api_error',lang,error=message.split(':',1)[-1].strip())
    return message

_SIZE_UNITS = {
    'ru': ('Б','КБ','МБ','ГБ','ТБ'),
    'en': ('B','KB','MB','GB','TB'),
    'be': ('Б','КБ','МБ','ГБ','ТБ'),
    'zh': ('字节','KB','MB','GB','TB'),
}
_TIME_UNITS = {
    'ru': ('ч','мин','с'),
    'en': ('h','min','s'),
    'be': ('г','хв','с'),
    'zh': ('小时','分钟','秒'),
}

def size_text(value: int | float | None, lang: str='ru') -> str:
    if value is None: return '—'
    n=max(0.0,float(value))
    for unit in _SIZE_UNITS.get(lang,_SIZE_UNITS['ru']):
        if n<1024 or unit==_SIZE_UNITS.get(lang,_SIZE_UNITS['ru'])[-1]:
            return f'{n:.0f} {unit}' if unit == _SIZE_UNITS.get(lang,_SIZE_UNITS['ru'])[0] else f'{n:.1f} {unit}'
        n/=1024
    return '—'

def eta_locale(seconds: float | None, lang: str='ru') -> str:
    if seconds is None or seconds<0:return '—'
    n=round(seconds)
    h,m,s=_TIME_UNITS.get(lang,_TIME_UNITS['ru'])
    if n>=3600:return f'{n//3600} {h} {(n%3600)//60} {m}'
    if n>=60:return f'{n//60} {m} {n%60} {s}'
    return f'{n} {s}'
