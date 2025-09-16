import base64
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from atlassian import Confluence
from datetime import datetime
from getpass import getpass

from requests.auth import HTTPBasicAuth



def copy_confluence_page(url, username, password ,page_id, page_parent_id):
    confluence = Confluence(
        url=url,
        username=username,
        password=password,
        verify_ssl=False
    )
    # Загружаем страницу
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,space,version', status=None, version=None)
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M")


    # Создаем новую страницу
    new_page = {
        "type": "page",
        "title": page["title"] + " - отчет " + str(date),
        "space": {
            "key": page["space"]["key"]
        },
        "body": {
            "storage": {
                "value": page["body"]["storage"]["value"],
                "representation": "storage"
            }
        },
        "version": {
            "number": 1
        }
    }

    # Пытаемся создать новую страницу
    try:
        new_page = confluence.create_page(space=new_page["space"]["key"], title=new_page["title"],
                                          body=new_page["body"]["storage"]["value"], parent_id=page_parent_id)
    except Exception as e:
        print(f"Ошибка при создании новой страницы: {e}")
        return

    print("Новая страница успешно создана.")
    return new_page["id"]





def update_confluence_page_old(url, username, password, page_id, data_to_find, replace_text):
    confluence = Confluence(
        url=url,
        username=username,
        password=password,
        verify_ssl=False
    )
    # Загружаем страницу
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,space,version', status=None, version=None)
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return

    # Если replace_text не строка, преобразуем в строку (например, для DataFrame)
    replace_content = str(replace_text) if not isinstance(replace_text, str) else replace_text
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Заменяем данные на странице
    page["body"]["storage"]["value"] = page["body"]["storage"]["value"].replace(str(data_to_find), replace_content)
    
    page["version"]["number"] += 1

    # Пытаемся загрузить обновленную страницу
    try:
        confluence.update_page(
            page_id=page["id"],
            title=page["title"],
            body=page["body"]["storage"]["value"],
            minor_edit=True
        )
    except Exception as e:
        print(f"Ошибка при обновлении страницы: {e}")
        return

    print("Страница успешно обновлена.")
  
def update_confluence_page(url, username, password, page_id, data_to_find, replace_text):
    confluence = Confluence(
        url=url,
        username=username,
        password=password,
        verify_ssl=False
    )
    
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,space,version')
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return
    
    # Преобразуем replace_text в строку, если это не строка
    replace_content = str(replace_text) if not isinstance(replace_text, str) else replace_text
    
    # Получаем исходное содержимое страницы
    original_html = page["body"]["storage"]["value"]
    
    # Проверка наличия плейсхолдера перед заменой
    if data_to_find not in original_html:
        print(f"ВНИМАНИЕ: Плейсхолдер '{data_to_find}' не найден на странице!")
        return "Плейсхолдер не найден"
    
    # Простая замена без использования BeautifulSoup
    modified_html = original_html.replace(str(data_to_find), replace_content)
    
    # Обновление страницы с измененным содержимым
    try:
        confluence.update_page(
            page_id=page["id"],
            title=page["title"],
            body=modified_html,
            type='page',
            representation='storage',
            minor_edit=True
        )
        print("Страница успешно обновлена.")
        return "Успешно"
    except Exception as e:
        print(f"Ошибка при обновлении страницы: {e}")
        return f"Ошибка: {e}"


def render_llm_report_placeholders(report: dict) -> dict:
    """Формирует словарь {placeholder: html} с фолбэками из структурированного отчёта LLM.
    Ожидается структура {verdict, confidence, findings[], recommended_actions[]}.
    При отсутствии полей подставляются безопасные значения.
    """
    safe = lambda x: str(x).strip() if x is not None else ""

    verdict = safe((report or {}).get("verdict") or "нет данных")
    conf_val = (report or {}).get("confidence")
    confidence_str = f"{int(conf_val * 100)}%" if isinstance(conf_val, (int, float)) else "—"

    findings = (report or {}).get("findings") or []
    items = []
    for f in findings:
        if isinstance(f, dict):
            summary = safe(f.get("summary"))
            sev = safe(f.get("severity"))
            comp = safe(f.get("component"))
            ev = safe(f.get("evidence"))
            meta = []
            if sev:
                meta.append(f"<span style='color:#b00'><strong>{sev}</strong></span>")
            if comp:
                meta.append(f"<code>{comp}</code>")
            if ev:
                meta.append(f"<em>{ev}</em>")
            meta_str = (" &middot; ".join(meta)) if meta else ""
            if summary or meta_str:
                items.append(f"<li>{summary} {('— ' + meta_str) if meta_str else ''}</li>")
        else:
            s = safe(f)
            if s:
                items.append(f"<li>{s}</li>")
    findings_html = "<ul>" + "".join(items) + "</ul>" if items else "<em>Нет существенных находок</em>"

    actions = (report or {}).get("recommended_actions") or (report or {}).get("actions") or []
    aitems = []
    for a in actions:
        s = safe(a)
        if s:
            aitems.append(f"<li>{s}</li>")
    actions_html = "<ul>" + "".join(aitems) + "</ul>" if aitems else "<em>Нет рекомендаций</em>"

    affected = (report or {}).get("affected_components") or []
    affected_html = ""
    if affected:
        affected_html = "<p><strong>Затронутые компоненты:</strong> " + ", ".join([f"<code>{safe(a)}</code>" for a in affected]) + "</p>"

    return {
        "${LLM_VERDICT}": f"<strong>{verdict}</strong>",
        "${LLM_CONFIDENCE}": confidence_str,
        "${LLM_FINDINGS}": affected_html + findings_html,
        "${LLM_ACTIONS}": actions_html,
    }


def render_llm_markdown(report: dict) -> str:
    """Генерирует markdown для единого плейсхолдера `$$answer_llm$$`.
    Форматирует: вердикт/доверие, список находок с метаданными, список действий.
    """
    def safe(x):
        return str(x).strip() if x is not None else ""

    verdict = safe((report or {}).get("verdict") or "нет данных")
    conf_val = (report or {}).get("confidence")
    confidence_str = f"{int(conf_val*100)}%" if isinstance(conf_val, (int, float)) else "—"

    md_lines = []
    md_lines.append("### Итог LLM")
    md_lines.append(f"- Вердикт: {verdict}")
    md_lines.append(f"- Доверие: {confidence_str}")
    md_lines.append("")

    findings = (report or {}).get("findings") or []
    md_lines.append("#### Ключевые находки")
    if not findings:
        md_lines.append("- Нет существенных находок")
    else:
        for f in findings:
            if isinstance(f, dict):
                summary = safe(f.get("summary"))
                sev = safe(f.get("severity"))
                comp = safe(f.get("component"))
                ev = safe(f.get("evidence"))
                meta = []
                if sev:
                    meta.append(f"severity: {sev}")
                if comp:
                    meta.append(f"component: {comp}")
                if ev:
                    meta.append(f"evidence: {ev}")
                meta_str = "; ".join(meta)
                if meta_str:
                    md_lines.append(f"- {summary} ({meta_str})")
                else:
                    md_lines.append(f"- {summary}")
            else:
                md_lines.append(f"- {safe(f)}")

    actions = (report or {}).get("recommended_actions") or (report or {}).get("actions") or []
    md_lines.append("")
    md_lines.append("#### Рекомендации")
    if not actions:
        md_lines.append("- Нет рекомендаций")
    else:
        for a in actions:
            s = safe(a)
            if s:
                md_lines.append(f"- [ ] {s}")

    affected = (report or {}).get("affected_components") or []
    if affected:
        md_lines.append("")
        md_lines.append("#### Затронутые компоненты")
        md_lines.append(", ".join([f"`{safe(x)}`" for x in affected]))

    return "\n".join(md_lines)


def update_confluence_page_multi(url, username, password, page_id, replacements: dict) -> str:
    """Один проход по странице: заменить несколько плейсхолдеров. Отсутствующие не считаем ошибкой."""
    confluence = Confluence(
        url=url,
        username=username,
        password=password,
        verify_ssl=False
    )

    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,space,version')
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return "Ошибка загрузки"

    html = page["body"]["storage"]["value"]
    replaced_any = False
    for placeholder, value in (replacements or {}).items():
        if not isinstance(value, str) or not value.strip():
            print(f"[warn] Пропускаю пустую замену для: {placeholder}")
            continue
        if placeholder in html:
            html = html.replace(str(placeholder), str(value))
            replaced_any = True
        else:
            print(f"[warn] Плейсхолдер '{placeholder}' не найден. Пропускаю.")

    if not replaced_any:
        print("Нет совпавших плейсхолдеров. Обновление не требуется.")
        return "Нет замен"

    try:
        confluence.update_page(
            page_id=page["id"],
            title=page["title"],
            body=html,
            type='page',
            representation='storage',
            minor_edit=True
        )
        print("Страница успешно обновлена (мульти-замена).")
        return "Успешно"
    except Exception as e:
        print(f"Ошибка при обновлении страницы: {e}")
        return f"Ошибка: {e}"





