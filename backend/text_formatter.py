import re
from typing import Dict, Any, List

def format_analysis_text(raw_text: str) -> Dict[str, Any]:
    """
    Форматирует сырой текст анализа в красивый структурированный формат
    Убирает символы "*" и создает читаемый текст
    """
    
    # Убираем лишние символы форматирования
    cleaned_text = raw_text.replace('*', '').replace('#', '').strip()
    
    # Разбиваем текст на секции
    sections = {}
    current_section = "intro"
    current_content = []
    
    lines = cleaned_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Определяем секции по ключевым словам
        lower_line = line.lower()
        
        if any(keyword in lower_line for keyword in ['резюме', 'summary', 'краткое', 'suummary']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "summary"
            current_content = []
        elif any(keyword in lower_line for keyword in ['отправитель', 'sender', 'от кого']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "sender"
            current_content = []
        elif any(keyword in lower_line for keyword in ['тип письма', 'type', 'категория']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "type"
            current_content = []
        elif any(keyword in lower_line for keyword in ['содержание', 'content', 'основное']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "content"
            current_content = []
        elif any(keyword in lower_line for keyword in ['действия', 'actions', 'требуемые']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "actions"
            current_content = []
        elif any(keyword in lower_line for keyword in ['сроки', 'deadline', 'дата']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "deadlines"
            current_content = []
        elif any(keyword in lower_line for keyword in ['последствия', 'consequences', 'если не']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "consequences"
            current_content = []
        elif any(keyword in lower_line for keyword in ['срочность', 'urgency', 'приоритет', 'важность']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "urgency"
            current_content = []
        elif any(keyword in lower_line for keyword in ['шаблон', 'template', 'ответ']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "template"
            current_content = []
        else:
            # Если это не заголовок секции, добавляем к содержимому
            if not any(char.isdigit() for char in line[:3]) or len(line) > 5:
                current_content.append(line)
    
    # Добавляем последнюю секцию
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    # Создаем структурированный результат
    formatted_result = {
        "main_content": sections.get("summary", sections.get("intro", "")).strip(),
        "sender_info": sections.get("sender", "").strip(),
        "document_type": sections.get("type", "").strip(),
        "key_content": sections.get("content", "").strip(),
        "required_actions": sections.get("actions", "").strip(),
        "deadlines": sections.get("deadlines", "").strip(),
        "consequences": sections.get("consequences", "").strip(),
        "urgency_level": extract_urgency_level(sections.get("urgency", "")),
        "response_template": sections.get("template", "").strip(),
        "full_analysis": create_beautiful_full_text(sections),
        "formatted_sections": format_sections_for_display(sections)
    }
    
    return formatted_result

def extract_urgency_level(urgency_text: str) -> str:
    """Извлекает уровень срочности из текста"""
    if not urgency_text:
        return "СРЕДНИЙ"
    
    urgency_lower = urgency_text.lower()
    
    if any(keyword in urgency_lower for keyword in ['высокий', 'срочно', 'критичн', 'немедленно', 'high', 'urgent', 'critical']):
        return "ВЫСОКИЙ"
    elif any(keyword in urgency_lower for keyword in ['низкий', 'несрочно', 'может подождать', 'low', 'not urgent']):
        return "НИЗКИЙ"
    else:
        return "СРЕДНИЙ"

def create_beautiful_full_text(sections: Dict[str, str]) -> str:
    """Создает красиво отформатированный полный текст анализа"""
    beautiful_text = ""
    
    section_titles = {
        "intro": "📋 Общая информация",
        "summary": "📝 Краткое резюме",
        "sender": "👤 Информация об отправителе", 
        "type": "📋 Тип документа",
        "content": "📄 Основное содержание",
        "actions": "⚡ Требуемые действия",
        "deadlines": "📅 Важные сроки",
        "consequences": "⚠️ Возможные последствия",
        "urgency": "🚨 Уровень срочности",
        "template": "📨 Шаблон ответа"
    }
    
    for section_key, content in sections.items():
        if content.strip():
            title = section_titles.get(section_key, f"📌 {section_key.title()}")
            beautiful_text += f"\n{title}\n"
            beautiful_text += "─" * 40 + "\n"
            beautiful_text += f"{content.strip()}\n\n"
    
    return beautiful_text.strip()

def format_sections_for_display(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Форматирует секции для красивого отображения в UI"""
    display_sections = []
    
    section_config = {
        "summary": {
            "title": "Краткое резюме",
            "icon": "📝",
            "color": "blue",
            "priority": 1
        },
        "sender": {
            "title": "Отправитель",
            "icon": "👤", 
            "color": "gray",
            "priority": 2
        },
        "type": {
            "title": "Тип документа",
            "icon": "📋",
            "color": "purple",
            "priority": 3
        },
        "content": {
            "title": "Основное содержание",
            "icon": "📄",
            "color": "green",
            "priority": 4
        },
        "actions": {
            "title": "Требуемые действия",
            "icon": "⚡",
            "color": "orange",
            "priority": 5
        },
        "deadlines": {
            "title": "Важные сроки",
            "icon": "📅",
            "color": "red",
            "priority": 6
        },
        "consequences": {
            "title": "Возможные последствия",
            "icon": "⚠️",
            "color": "yellow",
            "priority": 7
        },
        "urgency": {
            "title": "Уровень срочности",
            "icon": "🚨",
            "color": "red",
            "priority": 8
        }
    }
    
    for section_key, content in sections.items():
        if content.strip() and section_key in section_config:
            config = section_config[section_key]
            display_sections.append({
                "key": section_key,
                "title": config["title"],
                "icon": config["icon"],
                "color": config["color"],
                "priority": config["priority"],
                "content": content.strip()
            })
    
    # Сортируем по приоритету
    display_sections.sort(key=lambda x: x["priority"])
    
    return display_sections

def create_improved_analysis_prompt(language: str, filename: str) -> str:
    """Создает улучшенный промпт для анализа с лучшим форматированием"""
    
    language_prompts = {
        "en": "Analyze this German official letter and provide a structured response in English.",
        "ru": "Проанализируйте это официальное немецкое письмо и дайте структурированный ответ на русском языке.",
        "de": "Analysieren Sie diesen deutschen offiziellen Brief und geben Sie eine strukturierte Antwort auf Deutsch."
    }

    base_prompt = language_prompts.get(language, language_prompts["ru"])

    return f"""{base_prompt}

Пожалуйста, проанализируйте документ и предоставьте информацию в следующем формате БЕЗ использования символов форматирования (* # и других):

КРАТКОЕ РЕЗЮМЕ
Дайте краткое описание содержания письма в 2-3 предложениях.

ИНФОРМАЦИЯ ОБ ОТПРАВИТЕЛЕ  
Укажите кто отправил письмо (организация, департамент, должностное лицо).

ТИП ПИСЬМА
Определите тип документа (уведомление, требование, приглашение, справка и т.д.).

ОСНОВНОЕ СОДЕРЖАНИЕ
Подробно опишите о чем говорится в письме, какая информация передается.

ТРЕБУЕМЫЕ ДЕЙСТВИЯ
Перечислите какие конкретные действия требуются от получателя письма.

ВАЖНЫЕ СРОКИ
Укажите все упомянутые даты, сроки и временные рамки.

ВОЗМОЖНЫЕ ПОСЛЕДСТВИЯ
Опишите что может произойти если не предпринять требуемые действия.

УРОВЕНЬ СРОЧНОСТИ
Оцените срочность как НИЗКИЙ, СРЕДНИЙ или ВЫСОКИЙ.

ШАБЛОН ОТВЕТА
При необходимости предложите вежливый шаблон ответа на немецком языке.

Файл: {filename}

Важно: НЕ используйте символы *, #, _, ** или другие символы форматирования. Пишите простым читаемым текстом."""