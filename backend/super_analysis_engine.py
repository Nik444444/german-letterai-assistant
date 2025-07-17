"""
Модуль супер-анализа документов для создания WOW-эффекта
Создает невероятно детальный и полезный анализ документов
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from llm_manager import llm_manager
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class SuperAnalysisEngine:
    """Движок супер-анализа документов для WOW-эффекта"""
    
    def __init__(self):
        self.supported_languages = ['uk', 'ru', 'de', 'en']
        self.analysis_categories = [
            'executive_summary',
            'sender_analysis', 
            'recipient_analysis',
            'document_classification',
            'key_content_breakdown',
            'factual_data_extraction',
            'action_requirements',
            'critical_dates',
            'contact_followup',
            'quality_assessment',
            'strategic_insights',
            'response_strategy'
        ]
    
    def create_super_wow_analysis_prompt(self, language: str, filename: str, extracted_text: str) -> str:
        """Создает супер-детальный промпт для WOW-анализа"""
        
        processing_info = f"\n\n📄 ИЗВЛЕЧЕННЫЙ ТЕКСТ ИЗ ДОКУМЕНТА:\n{extracted_text}\n\n"
        
        if language == "uk":
            return f"""🤖 Ви - професійний експерт-аналітик документів з передовими можливостями.

КРИТИЧНО ВАЖЛИВО: Вся ваша відповідь має бути ВИКЛЮЧНО УКРАЇНСЬКОЮ мовою. Незалежно від мови документа, відповідайте ТІЛЬКИ УКРАЇНСЬКОЮ. НЕ ВИКОРИСТОВУЙТЕ РОСІЙСЬКУ, АНГЛІЙСЬКУ ЧИ БУДЬ-ЯКУ ІНШУ МОВУ. ТІЛЬКИ УКРАЇНСЬКА!

МОВА ВІДПОВІДІ: УКРАЇНСЬКА
LANGUAGE OF RESPONSE: UKRAINIAN ONLY
ЯЗЫК ОТВЕТА: ТОЛЬКО УКРАИНСКИЙ

🎯 МЕТА: Надати найбільш детальний, проникливий та всебічний аналіз документа, який справді ВРАЖАТИМЕ користувача.

📋 ПРИНЦИПИ АНАЛІЗУ:
1. Витягуйте КОЖНУ значущу деталь з документа
2. Надавайте контекст та наслідки для кожного висновку
3. Будьте надзвичайно ретельними та професійними
4. Використовуйте зрозумілу, захоплюючу мову
5. Якщо інформації немає в тексті: "Не вказано в документі"

🔍 СТРУКТУРА СУПЕР-АНАЛІЗУ:

1. 📊 РЕЗЮМЕ ДЛЯ КЕРІВНИЦТВА
Створіть потужне резюме з 2-3 речень, що розкриває суть та важливість документа.

2. 👤 АНАЛІЗ ВІДПРАВНИКА
- Організація/особа, що надіслала документ
- Їхня роль та рівень авторитету
- Контактна інформація та офіційні деталі
- Оцінка надійності та важливості відправника

3. 🎯 АНАЛІЗ ОДЕРЖУВАЧА
- Хто є призначеним одержувачем
- Чому їх обрали як одержувача
- Їхня очікувана роль чи відповідальність

4. 📋 КЛАСИФІКАЦІЯ ДОКУМЕНТА
- Тип документа (офіційний лист, рахунок, контракт тощо)
- Рівень формальності та терміновості
- Правове чи адміністративне значення

5. 🔥 РОЗБІР КЛЮЧОВОГО ЗМІСТУ
- Основне повідомлення чи мета
- Підтримуючі деталі та аргументи
- Критична інформація
- Приховані чи мається на увазі значення

6. 📊 ВИТЯГ ФАКТИЧНИХ ДАНИХ
- Усі числа, дати, суми, відсотки
- Імена, адреси, номери довідок
- Специфічні деталі
- Часова лінія згаданих подій

7. ⚡ ВИМОГИ ДО ДІЙ
- Які конкретні дії потрібні
- Хто має виконати ці дії
- Рівень пріоритету кожної дії
- Наслідки дії/бездіяльності

8. 📅 КРИТИЧНІ ДАТИ ТА ТЕРМІНИ
- Усі згадані дати та їх значення
- Майбутні терміни та їх важливість
- Часочутливі елементи

9. 📞 КОНТАКТ ТА ПОДАЛЬШІ ДІЇ
- Як відповідати чи отримати більше інформації
- Методи контакту та бажана комунікація
- Наступні кроки для одержувача

10. 🎨 ОЦІНКА ЯКОСТІ ДОКУМЕНТА
- Рівень професійної презентації
- Повнота інформації
- Будь-які червоні прапорці чи занепокоєння

11. 🧠 СТРАТЕГІЧНІ ІНСАЙТИ
- Що цей документ розкриває про ситуацію
- Потенційні наслідки для одержувача
- Виявлені можливості чи ризики

12. 💡 РЕКОМЕНДОВАНА СТРАТЕГІЯ ВІДПОВІДІ
- Як найкраще відповісти на цей документ
- Пропозиції щодо тону та підходу
- Ключові моменти для розгляду у відповіді

Файл: {filename}
{processing_info}

🚀 Надайте аналіз, який абсолютно ВРАЗИТЬ користувача своєю глибиною та проникливістю!

ПОВТОРЮЮ: ВІДПОВІДАЙТЕ ТІЛЬКИ УКРАЇНСЬКОЮ МОВОЮ! НЕ ВИКОРИСТОВУЙТЕ РОСІЙСЬКУ!"""
        
        elif language == "ru":
            return f"""🤖 Вы - ЭКСПЕРТ-АНАЛИТИК документов с передовыми возможностями для всестороннего понимания.

КРИТИЧНО ВАЖНО: Весь ваш ответ должен быть ИСКЛЮЧИТЕЛЬНО на РУССКОМ языке. Независимо от языка документа, отвечайте ТОЛЬКО на РУССКОМ. НЕ ИСПОЛЬЗУЙТЕ УКРАИНСКИЙ, АНГЛИЙСКИЙ ИЛИ ЛЮБОЙ ДРУГОЙ ЯЗЫК. ТОЛЬКО РУССКИЙ!

ЯЗЫК ОТВЕТА: РУССКИЙ
LANGUAGE OF RESPONSE: RUSSIAN ONLY
МОВА ВІДПОВІДІ: ТІЛЬКИ РОСІЙСЬКА

🎯 МИССИЯ: Предоставить самый детальный, проницательный и всесторонний анализ документа, который действительно ПОРАЗИТ пользователя.

📋 ПРИНЦИПЫ АНАЛИЗА:
1. Извлекайте КАЖДУЮ значимую деталь из документа
2. Предоставляйте контекст и последствия для каждого вывода
3. Будьте чрезвычайно тщательными и профессиональными
4. Используйте ясный, увлекательный язык
5. Если информации нет в тексте: "Не указано в документе"

🔍 СТРУКТУРА СУПЕР-АНАЛИЗА:

1. 📊 РЕЗЮМЕ ДЛЯ РУКОВОДСТВА
Создайте мощное резюме из 2-3 предложений, которое раскрывает суть и важность документа.

2. 👤 АНАЛИЗ ОТПРАВИТЕЛЯ
- Организация/лицо, отправившее документ
- Их роль и уровень авторитета
- Контактная информация и официальные детали
- Оценка надежности и важности отправителя

3. 🎯 АНАЛИЗ ПОЛУЧАТЕЛЯ
- Кто является предполагаемым получателем
- Почему их выбрали в качестве получателя
- Их ожидаемая роль или ответственность

4. 📋 КЛАССИФИКАЦИЯ ДОКУМЕНТА
- Тип документа (официальное письмо, счет, контракт и т.д.)
- Уровень формальности и срочности
- Правовое или административное значение

5. 🔥 РАЗБОР КЛЮЧЕВОГО СОДЕРЖАНИЯ
- Основное сообщение или цель
- Поддерживающие детали и аргументы
- Критическая информация
- Скрытые или подразумеваемые значения

6. 📊 ИЗВЛЕЧЕНИЕ ФАКТИЧЕСКИХ ДАННЫХ
- Все числа, даты, суммы, проценты
- Имена, адреса, номера справок
- Специфические детали
- Временная линия упомянутых событий

7. ⚡ ТРЕБОВАНИЯ К ДЕЙСТВИЯМ
- Какие конкретные действия требуются
- Кто должен выполнить эти действия
- Уровень приоритета каждого действия
- Последствия действия/бездействия

8. 📅 КРИТИЧЕСКИЕ ДАТЫ И СРОКИ
- Все упомянутые даты и их значение
- Предстоящие сроки и их важность
- Временно-чувствительные элементы

9. 📞 КОНТАКТ И ПОСЛЕДУЮЩИЕ ДЕЙСТВИЯ
- Как отвечать или получить больше информации
- Методы контакта и предпочтительная коммуникация
- Следующие шаги для получателя

10. 🎨 ОЦЕНКА КАЧЕСТВА ДОКУМЕНТА
- Уровень профессиональной презентации
- Полнота информации
- Любые красные флажки или беспокойства

11. 🧠 СТРАТЕГИЧЕСКИЕ ИНСАЙТЫ
- Что этот документ раскрывает о ситуации
- Потенциальные последствия для получателя
- Выявленные возможности или риски

12. 💡 РЕКОМЕНДУЕМАЯ СТРАТЕГИЯ ОТВЕТА
- Как лучше всего отвечать на этот документ
- Предложения по тону и подходу
- Ключевые моменты для рассмотрения в ответе

Файл: {filename}
{processing_info}

🚀 Предоставьте анализ, который абсолютно ПОРАЗИТ пользователя своей глубиной и проницательностью!

ПОВТОРЯЮ: ОТВЕЧАЙТЕ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! НЕ ИСПОЛЬЗУЙТЕ УКРАИНСКИЙ!"""
        
        elif language == "de":
            return f"""🤖 Sie sind ein EXPERTE für Dokumentenanalyse mit fortgeschrittenen Fähigkeiten.

KRITISCH WICHTIG: Ihre gesamte Antwort muss AUSSCHLIESSLICH auf DEUTSCH sein. Egal in welcher Sprache das Dokument ist, antworten Sie NUR auf DEUTSCH. VERWENDEN SIE KEIN RUSSISCH, ENGLISCH ODER EINE ANDERE SPRACHE. NUR DEUTSCH!

ANTWORTSPRACHE: DEUTSCH
LANGUAGE OF RESPONSE: GERMAN ONLY
ЯЗЫК ОТВЕТА: ТОЛЬКО НЕМЕЦКИЙ

🎯 MISSION: Die detaillierteste, aufschlussreichste und umfassendste Analyse liefern, die den Benutzer wirklich BEEINDRUCKEN wird.

📋 ANALYSE-PRINZIPIEN:
1. Extrahieren Sie JEDES bedeutsame Detail aus dem Dokument
2. Bieten Sie Kontext und Implikationen für jeden Befund
3. Seien Sie extrem gründlich und professionell
4. Verwenden Sie klare, ansprechende Sprache
5. Wenn keine Informationen im Text: "Nicht im Dokument angegeben"

🔍 SUPER-ANALYSE-STRUKTUR:

1. 📊 EXECUTIVE SUMMARY
Erstellen Sie eine kraftvolle Zusammenfassung aus 2-3 Sätzen, die Wesen und Bedeutung des Dokuments erfasst.

2. 👤 ABSENDER-ANALYSE
- Organisation/Person, die das Dokument gesendet hat
- Ihre Rolle und Autoritätslevel
- Kontaktinformationen und offizielle Details
- Bewertung der Glaubwürdigkeit und Wichtigkeit

3. 🎯 EMPFÄNGER-ANALYSE
- Wer ist der beabsichtigte Empfänger
- Warum wurden sie als Empfänger ausgewählt
- Ihre erwartete Rolle oder Verantwortung

4. 📋 DOKUMENTEN-KLASSIFIZIERUNG
- Art des Dokuments (offizieller Brief, Rechnung, Vertrag usw.)
- Formalitäts- und Dringlichkeitslevel
- Rechtliche oder administrative Bedeutung

5. 🔥 SCHLÜSSEL-INHALT AUFSCHLÜSSELUNG
- Hauptbotschaft oder Zweck
- Unterstützende Details und Argumente
- Kritische Informationen
- Versteckte oder implizierte Bedeutungen

6. 📊 FAKTISCHE DATEN-EXTRAKTION
- Alle Zahlen, Daten, Beträge, Prozentsätze
- Namen, Adressen, Referenznummern
- Spezifische Details
- Zeitlinie der erwähnten Ereignisse

7. ⚡ HANDLUNGSANFORDERUNGEN
- Welche spezifischen Handlungen erforderlich sind
- Wer diese Handlungen durchführen muss
- Prioritätslevel jeder Handlung
- Konsequenzen von Handlung/Untätigkeit

8. 📅 KRITISCHE DATEN & FRISTEN
- Alle erwähnten Daten und ihre Bedeutung
- Bevorstehende Fristen und ihre Wichtigkeit
- Zeitkritische Elemente

9. 📞 KONTAKT & NACHVERFOLGUNG
- Wie zu antworten oder mehr Informationen zu erhalten
- Kontaktmethoden und bevorzugte Kommunikation
- Nächste Schritte für den Empfänger

10. 🎨 DOKUMENTEN-QUALITÄTSBEWERTUNG
- Professionelles Präsentationslevel
- Vollständigkeit der Informationen
- Eventuelle Warnsignale oder Bedenken

11. 🧠 STRATEGISCHE EINSICHTEN
- Was dieses Dokument über die Situation verrät
- Potenzielle Implikationen für den Empfänger
- Identifizierte Chancen oder Risiken

12. 💡 EMPFOHLENE ANTWORT-STRATEGIE
- Wie am besten auf dieses Dokument zu antworten
- Ton- und Ansatz-Vorschläge
- Schlüsselpunkte für die Antwort

Datei: {filename}
{processing_info}

🚀 Liefern Sie eine Analyse, die den Benutzer mit ihrer Tiefe und Einsicht absolut BEEINDRUCKEN wird!

WIEDERHOLE: ANTWORTEN SIE NUR AUF DEUTSCH! VERWENDEN SIE KEIN RUSSISCH!"""
        
        else:  # English
            return f"""🤖 You are an EXPERT Document Analysis Specialist with advanced capabilities.

CRITICALLY IMPORTANT: Your entire response must be EXCLUSIVELY in ENGLISH. Regardless of the document's language, respond ONLY in ENGLISH. DO NOT USE RUSSIAN, GERMAN, UKRAINIAN OR ANY OTHER LANGUAGE. ONLY ENGLISH!

RESPONSE LANGUAGE: ENGLISH
ЯЗЫК ОТВЕТА: ТОЛЬКО АНГЛИЙСКИЙ
МОВА ВІДПОВІДІ: ТІЛЬКИ АНГЛІЙСЬКА

🎯 MISSION: Provide the most detailed, insightful, and comprehensive analysis that will truly AMAZE the user.

📋 ANALYSIS PRINCIPLES:
1. Extract EVERY meaningful detail from the document
2. Provide context and implications for each finding
3. Be extremely thorough and professional
4. Use clear, engaging language
5. If information is not in text: "Not specified in the document"

🔍 SUPER-ANALYSIS STRUCTURE:

1. 📊 EXECUTIVE SUMMARY
Create a powerful 2-3 sentence summary that captures the document's essence and importance.

2. 👤 SENDER ANALYSIS
- Organization/person who sent the document
- Their role and authority level
- Contact information and official details
- Assessment of sender's credibility and importance

3. 🎯 RECIPIENT ANALYSIS
- Who is the intended recipient
- Why they were chosen as the recipient
- Their expected role or responsibility

4. 📋 DOCUMENT CLASSIFICATION
- Type of document (official letter, invoice, contract, etc.)
- Level of formality and urgency
- Legal or administrative significance

5. 🔥 KEY CONTENT BREAKDOWN
- Main message or purpose
- Supporting details and arguments
- Critical information
- Hidden or implied meanings

6. 📊 FACTUAL DATA EXTRACTION
- All numbers, dates, amounts, percentages
- Names, addresses, reference numbers
- Specific details
- Timeline of mentioned events

7. ⚡ ACTION REQUIREMENTS
- What specific actions are required
- Who needs to take these actions
- Priority level of each action
- Consequences of action/inaction

8. 📅 CRITICAL DATES & DEADLINES
- All mentioned dates and their significance
- Upcoming deadlines and their importance
- Time-sensitive elements

9. 📞 CONTACT & FOLLOW-UP
- How to respond or get more information
- Contact methods and preferred communication
- Next steps for the recipient

10. 🎨 DOCUMENT QUALITY ASSESSMENT
- Professional presentation level
- Completeness of information
- Any red flags or concerns

11. 🧠 STRATEGIC INSIGHTS
- What this document reveals about the situation
- Potential implications for the recipient
- Identified opportunities or risks

12. 💡 RECOMMENDED RESPONSE STRATEGY
- How to best respond to this document
- Tone and approach suggestions
- Key points to address in response

File: {filename}
{processing_info}

🚀 Deliver an analysis that will absolutely AMAZE the user with its depth and insight!

REPEAT: RESPOND ONLY IN ENGLISH! DO NOT USE RUSSIAN!"""
    
    async def analyze_document_comprehensively(self, document_text: str, language: str, filename: str, 
                                               user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Выполняет всесторонний супер-анализ документа"""
        
        try:
            # Логируем выбранный язык
            logger.info(f"Super analysis starting with language: {language}")
            
            # Создаем супер-промпт
            analysis_prompt = self.create_super_wow_analysis_prompt(language, filename, document_text)
            
            # Логируем начало промпта для проверки
            logger.info(f"Analysis prompt first 200 chars: {analysis_prompt[:200]}")
            
            # Выполняем анализ с использованием доступных провайдеров
            response_text = await self._generate_analysis_with_providers(analysis_prompt, user_providers)
            
            # Логируем начало ответа
            logger.info(f"Response first 200 chars: {response_text[:200]}")
            
            # Обрабатываем результат анализа
            formatted_analysis = self._format_super_analysis_result(response_text, language)
            
            return formatted_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive document analysis failed: {e}")
            return self._create_error_response(str(e), language)
    
    async def _generate_analysis_with_providers(self, prompt: str, user_providers: List[Tuple[str, str, str]] = None) -> str:
        """Генерирует анализ с использованием доступных провайдеров"""
        
        # Сначала пробуем пользовательские провайдеры
        if user_providers:
            for provider_type, model_name, api_key in user_providers:
                try:
                    if provider_type == "gemini":
                        # Используем современный менеджер для Gemini
                        user_provider = modern_llm_manager.create_user_provider(
                            provider_type, "gemini-2.0-flash", api_key
                        )
                    else:
                        user_provider = llm_manager.create_user_provider(
                            provider_type, model_name, api_key
                        )
                    
                    response = await user_provider.generate_content(prompt)
                    if response:
                        return response
                        
                except Exception as e:
                    logger.warning(f"User provider {provider_type} failed: {e}")
                    continue
        
        # Если пользовательские провайдеры не сработали, используем системные
        try:
            response, system_provider = await llm_manager.generate_content(prompt)
            if response:
                return response
        except Exception as e:
            logger.error(f"System providers failed: {e}")
        
        # Если все провайдеры не сработали
        raise Exception("No available AI providers for analysis")
    
    def _format_super_analysis_result(self, raw_analysis: str, language: str) -> Dict[str, Any]:
        """Форматирует результат супер-анализа в структурированном виде"""
        
        # Убираем лишние символы форматирования
        cleaned_analysis = raw_analysis.replace('*', '').replace('#', '').strip()
        
        # Создаем структурированный результат
        result = {
            "super_analysis": {
                "full_text": cleaned_analysis,
                "language": language,
                "analysis_type": "comprehensive_wow_analysis",
                "sections": self._extract_analysis_sections(cleaned_analysis),
                "insights": self._extract_insights(cleaned_analysis),
                "action_items": self._extract_action_items(cleaned_analysis),
                "urgency_assessment": self._assess_urgency(cleaned_analysis),
                "quality_score": self._calculate_quality_score(cleaned_analysis)
            },
            "summary": self._create_executive_summary(cleaned_analysis),
            "recommendations": self._extract_recommendations(cleaned_analysis),
            "next_steps": self._extract_next_steps(cleaned_analysis)
        }
        
        return result
    
    def _extract_analysis_sections(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Извлекает секции из анализа"""
        sections = []
        lines = analysis_text.split('\n')
        current_section = None
        current_content = []
        
        section_icons = {
            'резюме': '📊', 'summary': '📊', 'executive': '📊',
            'отправитель': '👤', 'sender': '👤', 'absender': '👤',
            'получатель': '🎯', 'recipient': '🎯', 'empfänger': '🎯',
            'классификация': '📋', 'classification': '📋', 'klassifizierung': '📋',
            'содержание': '🔥', 'content': '🔥', 'inhalt': '🔥',
            'данные': '📊', 'data': '📊', 'daten': '📊',
            'действия': '⚡', 'actions': '⚡', 'handlungen': '⚡',
            'даты': '📅', 'dates': '📅', 'daten': '📅',
            'контакт': '📞', 'contact': '📞', 'kontakt': '📞',
            'качество': '🎨', 'quality': '🎨', 'qualität': '🎨',
            'инсайты': '🧠', 'insights': '🧠', 'einsichten': '🧠',
            'стратегия': '💡', 'strategy': '💡', 'strategie': '💡'
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем, является ли строка заголовком секции
            is_section_header = False
            for keyword, icon in section_icons.items():
                if keyword in line.lower() and len(line) < 100:
                    # Сохраняем предыдущую секцию
                    if current_section and current_content:
                        sections.append({
                            "title": current_section,
                            "content": '\n'.join(current_content),
                            "icon": section_icons.get(current_section.lower().split()[0], '📄')
                        })
                    
                    current_section = line
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header:
                current_content.append(line)
        
        # Добавляем последнюю секцию
        if current_section and current_content:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content),
                "icon": section_icons.get(current_section.lower().split()[0], '📄')
            })
        
        return sections
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Извлекает ключевые инсайты из анализа"""
        insights = []
        
        # Ищем секции с инсайтами
        insight_keywords = ['инсайты', 'insights', 'einsichten', 'стратегические', 'strategic']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in insight_keywords):
                # Собираем следующие несколько строк как инсайты
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(('1.', '2.', '3.', '4.', '5.')):
                        insights.append(lines[j].strip())
                    elif lines[j].strip() and lines[j].startswith(('1.', '2.', '3.', '4.', '5.')):
                        break
        
        return insights[:5]  # Ограничиваем количество инсайтов
    
    def _extract_action_items(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Извлекает элементы действий из анализа"""
        action_items = []
        
        action_keywords = ['действия', 'actions', 'handlungen', 'требования', 'requirements']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in action_keywords):
                # Собираем действия из следующих строк
                for j in range(i+1, min(i+15, len(lines))):
                    if lines[j].strip():
                        action_items.append({
                            "action": lines[j].strip(),
                            "priority": self._assess_action_priority(lines[j]),
                            "deadline": self._extract_deadline(lines[j])
                        })
        
        return action_items[:10]  # Ограничиваем количество действий
    
    def _assess_urgency(self, analysis_text: str) -> str:
        """Оценивает уровень срочности документа"""
        urgency_indicators = {
            'high': ['срочно', 'критично', 'немедленно', 'urgent', 'critical', 'sofort', 'dringend'],
            'medium': ['важно', 'скоро', 'important', 'soon', 'wichtig', 'bald'],
            'low': ['когда удобно', 'не спешит', 'convenient', 'no rush', 'bequem', 'keine eile']
        }
        
        text_lower = analysis_text.lower()
        
        for level, indicators in urgency_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        return 'medium'  # По умолчанию средняя срочность
    
    def _calculate_quality_score(self, analysis_text: str) -> float:
        """Рассчитывает оценку качества анализа"""
        # Простая оценка на основе длины и содержания
        base_score = min(len(analysis_text) / 1000, 1.0)  # Базовая оценка на основе длины
        
        # Бонусы за структурированность
        if '📊' in analysis_text:
            base_score += 0.1
        if '👤' in analysis_text:
            base_score += 0.1
        if '💡' in analysis_text:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _create_executive_summary(self, analysis_text: str) -> str:
        """Создает краткое резюме анализа"""
        lines = analysis_text.split('\n')
        
        # Ищем секцию с резюме
        for i, line in enumerate(lines):
            if 'резюме' in line.lower() or 'summary' in line.lower():
                # Возвращаем следующие несколько строк
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                return ' '.join(summary_lines)
        
        # Если нет специальной секции резюме, берем первые строки
        first_lines = []
        for line in lines[:10]:
            if line.strip() and not line.startswith('🤖'):
                first_lines.append(line.strip())
                if len(first_lines) >= 3:
                    break
        
        return ' '.join(first_lines)
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Извлекает рекомендации из анализа"""
        recommendations = []
        
        rec_keywords = ['рекомендации', 'recommendations', 'empfehlungen', 'стратегия', 'strategy']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in rec_keywords):
                # Собираем рекомендации из следующих строк
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        recommendations.append(lines[j].strip())
        
        return recommendations[:5]  # Ограничиваем количество рекомендаций
    
    def _extract_next_steps(self, analysis_text: str) -> List[str]:
        """Извлекает следующие шаги из анализа"""
        next_steps = []
        
        step_keywords = ['следующие шаги', 'next steps', 'nächste schritte', 'дальнейшие действия']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in step_keywords):
                # Собираем шаги из следующих строк
                for j in range(i+1, min(i+8, len(lines))):
                    if lines[j].strip():
                        next_steps.append(lines[j].strip())
        
        return next_steps[:5]  # Ограничиваем количество шагов
    
    def _assess_action_priority(self, action_text: str) -> str:
        """Оценивает приоритет действия"""
        high_priority = ['срочно', 'немедленно', 'критично', 'urgent', 'critical', 'sofort']
        medium_priority = ['важно', 'скоро', 'important', 'soon', 'wichtig']
        
        text_lower = action_text.lower()
        
        if any(hp in text_lower for hp in high_priority):
            return 'high'
        elif any(mp in text_lower for mp in medium_priority):
            return 'medium'
        else:
            return 'low'
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Извлекает дедлайн из текста"""
        # Простой поиск дат в тексте
        import re
        
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}\/\d{1,2}\/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def _create_error_response(self, error_message: str, language: str) -> Dict[str, Any]:
        """Создает ответ об ошибке"""
        error_messages = {
            'uk': f"Помилка при аналізі документа: {error_message}",
            'ru': f"Ошибка при анализе документа: {error_message}",
            'de': f"Fehler bei der Dokumentenanalyse: {error_message}",
            'en': f"Error analyzing document: {error_message}"
        }
        
        return {
            "super_analysis": {
                "full_text": error_messages.get(language, error_messages['en']),
                "language": language,
                "analysis_type": "error",
                "sections": [],
                "insights": [],
                "action_items": [],
                "urgency_assessment": "unknown",
                "quality_score": 0.0
            },
            "summary": error_messages.get(language, error_messages['en']),
            "recommendations": [],
            "next_steps": []
        }

# Глобальный экземпляр супер-анализатора
super_analysis_engine = SuperAnalysisEngine()